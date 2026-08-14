# 🏗️ Architecture Documentation

Comprehensive guide to DealFinder's system design, data flow, scaling strategies, and technical decisions.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SOURCES                         │
│              Estate Sales US, Craigslist, Facebook              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPER LAYER                                 │
│     Fetches listings, downloads images, normalizes data         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MESSAGE QUEUE (Optional)                      │
│     Bull, Celery, or RabbitMQ for async processing              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT LAYER                                    │
│      Claude Vision + Tools + Web Search Integration            │
│    Analyzes items, researches prices, generates insights        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATA PERSISTENCE                                │
│    PostgreSQL + SQLAlchemy ORM + Redis Cache                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────┴────┬──────────────┬─────────────┐
                    ▼         ▼              ▼             ▼
        Notification Service  Analytics  Webhooks     API Server
          (Email/Telegram)   Dashboard   (Discord)    (FastAPI)
                    │         │              │             │
                    └────────────────────────┴─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  User Notifications  │
                    │  API Responses       │
                    │  Real-time Updates   │
                    └──────────────────────┘
```

---

## Data Flow

### Listing Lifecycle

```
1. SCRAPE PHASE (8 AM daily)
   ├─ Scraper connects to estatesales.us
   ├─ Fetches all listings for today
   ├─ Downloads images locally
   ├─ Creates Listing records in DB
   └─ Queue items for analysis

2. ANALYSIS PHASE (8:15 AM, concurrent)
   ├─ Agent picks listing from queue
   ├─ Claude vision analyzes image
   │  ├─ Identifies item type
   │  ├─ Assesses condition
   │  └─ Detects artist (if art)
   ├─ Claude uses tools
   │  ├─ search_comparable_items
   │  ├─ get_market_value
   │  └─ search_artist_prices
   ├─ Creates DealAnalysis record
   └─ Calculates deal_score

3. NOTIFICATION PHASE
   ├─ Find all users interested in category
   ├─ Check if deal_score >= user threshold
   ├─ Send notifications
   │  ├─ Email
   │  ├─ Telegram
   │  └─ Discord
   └─ Record UserAlert for tracking

4. SERVING PHASE (Real-time)
   ├─ User queries /api/v1/deals
   ├─ API queries PostgreSQL
   ├─ Returns cached results
   └─ User sees latest deals
```

---

## Database Schema

### Core Tables

#### Listings
```sql
CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    source_url VARCHAR(500) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    listed_price FLOAT NOT NULL,
    image_urls JSONB,
    location VARCHAR(255),
    listed_date TIMESTAMP DEFAULT NOW(),
    scraped_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for common queries
CREATE INDEX idx_source_url ON listings(source, source_url);
CREATE INDEX idx_listed_date ON listings(listed_date DESC);
CREATE INDEX idx_is_active ON listings(is_active);
```

#### DealAnalyses
```sql
CREATE TABLE deal_analyses (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER UNIQUE REFERENCES listings(id),
    item_name VARCHAR(255) NOT NULL,
    category ENUM('art', 'furniture', ...) DEFAULT 'unknown',
    estimated_value FLOAT,
    deal_score FLOAT,
    recommendation VARCHAR(50),
    artist_name VARCHAR(255),  -- For art
    analyzed_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for filtering/sorting
CREATE INDEX idx_deal_score ON deal_analyses(deal_score DESC);
CREATE INDEX idx_category ON deal_analyses(category);
CREATE INDEX idx_recommendation ON deal_analyses(recommendation);
```

#### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    preferred_categories JSONB,
    min_deal_score INTEGER DEFAULT 70,
    telegram_user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_email ON users(email);
```

#### UserAlerts (Notification Log)
```sql
CREATE TABLE user_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    analysis_id INTEGER REFERENCES deal_analyses(id),
    sent_at TIMESTAMP,
    channel VARCHAR(50),  -- 'email', 'telegram', 'discord'
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_sent ON user_alerts(user_id, sent_at);
```

### Indexing Strategy

| Table | Index | Purpose |
|-------|-------|---------|
| listings | idx_source_url | Prevent duplicates, fast lookups |
| listings | idx_listed_date | Sort by recency |
| listings | idx_is_active | Filter active listings |
| deal_analyses | idx_deal_score | Sort deals (0-100) |
| deal_analyses | idx_category | Filter by category |
| deal_analyses | idx_recommendation | Group by quality |
| users | idx_email | Unique constraint, lookups |
| user_alerts | idx_user_sent | Find recent alerts |

---

## Claude Integration

### Vision API Usage

```python
# 1. Image to Base64
image_data = base64.b64encode(open(image_path, 'rb').read())

# 2. Send to Claude with vision
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data
                }
            },
            {
                "type": "text",
                "text": "Analyze this item..."
            }
        ]
    }]
)
```

### Tool Use Pattern (Agentic Loop)

```python
messages = [{"role": "user", "content": "Analyze this painting..."}]

while True:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        tools=TOOLS,  # Define search, value, artist price tools
        messages=messages
    )
    
    if response.stop_reason == "tool_use":
        # Claude wants to use a tool
        tool_result = execute_tool(response.tool_use)
        messages.append(tool_result)
        # Loop again
    else:
        # Claude done with analysis
        break
```

### Cost Optimization

- **Batching**: Group multiple listings in single request
- **Caching**: Cache market prices for common items
- **Sampling**: Analyze subset of new listings
- **Rate Limiting**: 100 analyses/hour max

---

## Scaling Strategies

### Phase 1: Single Instance (Current)
- Single FastAPI server
- PostgreSQL database
- Redis cache
- Suitable for: < 1000 daily listings

### Phase 2: Horizontal Scaling
```yaml
# Load balancer distributes requests
┌─────────────┐
│Load Balancer│ (Nginx)
└──────┬──────┘
   ┌───┼───┐
   ▼   ▼   ▼
[API1][API2][API3] → PostgreSQL ← [Redis Cluster]
   │   │   │
   └───┼───┘
       │
  [Scraper Queue]
```

### Phase 3: Microservices
```
API Service          Scraper Service      Agent Service
  (FastAPI)         (Scheduled Tasks)     (Claude Analysis)
    │                    │                    │
    └────────┬───────────┼────────┬──────────┘
             ▼           ▼        ▼
        PostgreSQL    Redis   Message Queue
```

### Database Optimization

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)

# Use bulk inserts for listings
session.bulk_insert_mappings(Listing, listing_dicts)
session.commit()

# Use eager loading for relationships
query = session.query(DealAnalysis).options(
    joinedload(DealAnalysis.listing)
)
```

---

## API Design

### RESTful Principles

```
GET    /api/v1/deals              → List all deals
GET    /api/v1/deals/{id}         → Single deal
GET    /api/v1/deals?category=art → Filter deals
POST   /api/v1/users/subscribe    → Create subscription
DELETE /api/v1/users/{id}         → Cancel subscription
```

### Response Caching

```python
@app.get("/api/v1/deals")
@cache(expire=300)  # 5 minute cache
def get_deals():
    return db.query(DealAnalysis).all()
```

### WebSocket for Real-time

```python
@app.websocket("/ws/deals/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # Send new deals as they arrive
    while True:
        deal = await get_new_deal_for_user(user_id)
        await websocket.send_json(deal)
```

---

## Error Handling

### Graceful Degradation

```python
try:
    analysis = agent.analyze_listing(listing)
except APIError as e:
    # Log but don't fail
    logger.error(f"Claude API error: {e}")
    # Return basic analysis
    return basic_analysis(listing)
except ImageError as e:
    # Fallback to text-only analysis
    return text_only_analysis(listing)
```

### Retry Strategy

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def analyze_with_retry(listing):
    return agent.analyze_listing(listing)
```

---

## Monitoring & Observability

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Analyzed listing {listing_id}: score={score}")
logger.warning(f"Failed to analyze {listing_id}, retrying...")
logger.error(f"Critical error in scraper", exc_info=True)
```

### Metrics

```
# Prometheus metrics
dealfinder_listings_total{source="estate_sales"}
dealfinder_analyses_total{category="art"}
dealfinder_notifications_sent{channel="email"}
dealfinder_api_response_time_seconds
dealfinder_claude_api_calls{model="vision"}
```

### Alerting

```
Triggers:
- Scraper fails 3x in a row
- API error rate > 5%
- Deal analysis takes > 30s
- Database connection pool exhausted
- Claude API quota exceeded
```

---

## Security Considerations

### API Security

```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/deals")
@limiter.limit("100/minute")
def get_deals():
    pass

# CORS
CORSMiddleware(
    allow_origins=["https://example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)

# Input validation
from pydantic import BaseModel, validator
```

### Database Security

```python
# Parameterized queries (SQLAlchemy does this)
query = session.query(User).filter(User.email == email)  # Safe

# Connection encryption
DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
```

### Secrets Management

```bash
# Use environment variables
ANTHROPIC_API_KEY from .env
DATABASE_PASSWORD from GitHub Secrets
TELEGRAM_BOT_TOKEN from deployment platform
```

---

## Testing Strategy

### Unit Tests
- Agent logic: 20 tests
- API endpoints: 15 tests
- Database models: 10 tests
- Scrapers: 12 tests

### Integration Tests
- End-to-end listing analysis
- Database persistence
- API with mock Claude

### Load Testing
```bash
# Test with Locust
pip install locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## Deployment Architecture

### Development
```
Laptop → LocalStack (PostgreSQL) → Claude API
```

### Staging
```
GitHub → Docker Registry → Railway/Render → PostgreSQL → Claude API
```

### Production
```
GitHub → Docker Registry → Kubernetes/VM → PostgreSQL (Cloud) → Claude API
```

---

## Future Improvements

### Phase 2
- [ ] WebSocket real-time updates
- [ ] Redis caching layer
- [ ] Elasticsearch for full-text search
- [ ] Mobile app (React Native)

### Phase 3
- [ ] ML model for deal scoring
- [ ] Computer vision for authenticity
- [ ] Multi-language support
- [ ] Custom price models per category

### Phase 4
- [ ] Marketplace integration (list deals)
- [ ] Subscription service
- [ ] Premium features
- [ ] White-label API

---

## Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Image analysis | 2-5s | Claude vision |
| Tool use search | 3-8s | Web search |
| DB insert | < 100ms | Batch operations |
| API response | < 200ms | Cached |
| Full analysis | 5-13s | Vision + tools |

---

## Compliance & Privacy

- **GDPR**: User data minimization, right to deletion
- **CCPA**: Privacy notice, opt-out mechanism
- **Data Retention**: Delete old listings after 30 days
- **PII Protection**: Never log sensitive data

---

