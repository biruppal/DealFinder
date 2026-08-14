# 🎯 DealFinder - AI-Powered Deal Analyzer

> **Find hidden gems at garage and estate sales using Claude's vision and web search capabilities.**

An intelligent agent that analyzes items from garage sales and estate sales websites, compares prices using real market data, and notifies you of exceptional deals. Built with production-grade engineering practices.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![Claude AI](https://img.shields.io/badge/Claude-Vision%20%2B%20Tools-purple)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Features

### Core Intelligence
- **🤖 Claude Vision AI**: Analyzes item photos to identify condition, style, artist (for art), and authenticity
- **🔍 Agentic Web Search**: Uses Claude tool-use to research comparable market prices in real-time
- **💡 Smart Categorization**: Automatically categorizes items (art, furniture, vintage, jewelry, etc.)
- **📊 Deal Scoring**: Calculates deal quality (0-100) based on value-to-price ratio

### Category-Specific Features
- **🎨 Art Analysis**: Identifies artist, style, period, provenance, and auction history
- **🪑 Furniture Expertise**: Detects era, designer, condition, and market trends
- **💎 Collectibles Intel**: Assesses rarity, condition, and collector demand

### User Features
- **🔔 Real-time Notifications**: Email, Telegram, Discord alerts for great deals
- **⚙️ Customizable Alerts**: Filter by category, minimum deal score, maximum price
- **📈 WebSocket Support**: Live deal updates as they're discovered
- **🌐 REST API**: Fully documented OpenAPI (Swagger) interface

### DevOps & Production
- **🐳 Docker Containerization**: Multi-stage builds, health checks
- **🔄 CI/CD Pipeline**: GitHub Actions with testing, coverage, security scanning
- **📦 Database Migrations**: Alembic for schema versioning
- **✅ 80%+ Test Coverage**: Pytest with comprehensive test suite
- **🛡️ Security**: Non-root Docker user, input validation, parameterized queries

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SOURCES                              │
│  Estate Sales US │ Craigslist │ Garage Sale Finder │ Facebook   │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SCRAPERS LAYER                                 │
│  Base Scraper │ Estate Sales Scraper │ Craigslist Scraper       │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 DEAL ANALYZER AGENT                               │
│            Claude Vision + Tool Use + Web Search                 │
│  - Image Analysis      │ - Price Comparison  │ - Market Research │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                 │
│      PostgreSQL │ SQLAlchemy ORM │ Alembic Migrations           │
│  Listings │ Analyses │ Users │ Alerts │ Price History            │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                                 │
│  Notification │ Price Comparison │ Categorization │ Scheduling   │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                               │
│   GET /api/v1/deals  │  POST /api/v1/subscribe  │  WS /ws/deals │
│             OpenAPI Docs at /docs                                │
└────────┬──────────────────────┬──────────────────────────────────┘
         │                      │
         ▼                      ▼
  Frontend/Mobile         User Notifications
   Applications          (Email/Telegram/Discord)
```

### Key Technologies

| Layer | Technology | Why |
|-------|-----------|-----|
| **AI/ML** | Claude 3.5 Sonnet | Vision analysis + agentic tool use |
| **Backend** | FastAPI | Modern async, auto OpenAPI docs |
| **Database** | PostgreSQL + SQLAlchemy | Production-grade with ORM |
| **Web Scraping** | BeautifulSoup + Selenium | Parse multiple estate sale sites |
| **Scheduling** | APScheduler | Periodic scraping & analysis |
| **Deployment** | Docker + Docker Compose | Containerized, reproducible |
| **CI/CD** | GitHub Actions | Automated testing & deployment |
| **Testing** | Pytest | 80%+ coverage |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 15+ (or use Docker Compose)
- Claude API key from Anthropic

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate
git clone https://github.com/biruppal/DealFinder.git
cd DealFinder

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start everything (DB, API, Redis)
docker-compose -f docker/docker-compose.yml up -d

# Run migrations (create tables)
docker-compose exec api alembic upgrade head

# Check health
curl http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
export $(cat .env | xargs)

# Run migrations
alembic upgrade head

# Start API server
uvicorn api.main:app --reload

# In another terminal, start scraper
python -m scrapers.run_scrapers
```

---

## 📖 API Documentation

### Interactive Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Example Endpoints

#### Get Top Deals
```bash
curl "http://localhost:8000/api/v1/deals?category=art&min_score=75&sort_by=deal_score&limit=10"
```

**Response**:
```json
{
  "deals": [
    {
      "id": 1,
      "item_name": "19th Century Oil Painting",
      "category": "art",
      "listed_price": 150.0,
      "estimated_value": 500.0,
      "deal_score": 85,
      "recommendation": "excellent_deal",
      "artist_name": "Unknown European",
      "comparable_items": [
        {
          "name": "Similar painting",
          "sold_price": 450,
          "source": "Auction.com",
          "date": "2024-01-15"
        }
      ]
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

#### Subscribe to Alerts
```bash
curl -X POST http://localhost:8000/api/v1/users/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "collector@example.com",
    "categories": ["art", "vintage"],
    "min_deal_score": 75,
    "telegram_user_id": "123456789"
  }'
```

#### WebSocket Real-time Alerts
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/deals/user123');
ws.onmessage = (event) => {
  const deal = JSON.parse(event.data);
  console.log('New deal!', deal.item_name, deal.deal_score);
};
```

---

## 🎯 How It Works

### Deal Analysis Flow

```
1. SCRAPE
   └─ Fetch listings from estate sales websites
      └─ Extract: title, price, images, location

2. ANALYZE (Claude Agentic Loop)
   ├─ Vision: Claude analyzes item photo
   │  └─ Identifies: type, condition, style, artist (if art)
   │
   ├─ Tool Use: Claude decides what to research
   │  ├─ search_comparable_items()
   │  │  └─ Find similar items & prices online
   │  ├─ get_market_value()
   │  │  └─ Estimate fair market value
   │  └─ search_artist_prices() [for art]
   │     └─ Get auction records & gallery prices
   │
   └─ Synthesize: Claude creates deal analysis
      └─ Calculates: value-to-price ratio, deal score, recommendation

3. NOTIFY
   └─ If deal_score >= user's threshold
      └─ Send alert via email/telegram/discord

4. PERSIST
   └─ Store in PostgreSQL for browsing/analytics
```

### Agentic Loop Example

```python
# Claude gets listing image + price
# Claude decides: "I need to search for this artist"
# Tool: search_artist_prices(artist_name="John Singer Sargent")
# Result: average price $5000, recent sales: 15
# Claude: "At $150, this is 33x below market! Deal score: 92"
```

---

## 📊 Database Schema

See `docs/ARCHITECTURE.md` for full schema with:
- Table relationships
- Index strategies
- Query optimization notes

**Key tables**:
- `listings` - Raw scraped data
- `deal_analyses` - Claude's analysis results
- `users` - Alert subscribers
- `user_alerts` - Notification tracking
- `price_history` - Track price changes

---

## ✅ Testing

```bash
# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v

# Run with markers
pytest -m "not slow" -v
```

**Test Coverage**:
- `test_agent.py` - Deal analyzer, vision, tool use
- `test_scrapers.py` - Scraper base class, implementations
- `test_api.py` - FastAPI endpoints, validation
- `test_db.py` - ORM models, migrations

---

## 🔧 Configuration

### Environment Variables

```env
# Claude API
ANTHROPIC_API_KEY=sk-...

# Database
DATABASE_URL=postgresql://user:pass@localhost/dealfinder
ENVIRONMENT=development

# Notifications
TELEGRAM_BOT_TOKEN=...
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your_email@gmail.com

# API
API_HOST=0.0.0.0
API_PORT=8000

# Scraping
SCRAPE_INTERVAL_MINUTES=60
MAX_CONCURRENT_SCRAPES=3
```

---

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design, data flow, scaling
- **[API.md](docs/API.md)** - Detailed endpoint documentation
- **[SETUP.md](docs/SETUP.md)** - Advanced setup & deployment
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Development guidelines

---

## 🚀 Deployment

### Deploy to Railway/Render

```bash
# 1. Push to GitHub
git push origin main

# 2. Connect via Railway/Render dashboard
# 3. Set environment variables
# 4. Deploy!
```

See `docs/SETUP.md#Deployment` for detailed instructions.

---

## 📈 Project Stats

- **Lines of Code**: 2,000+
- **Test Coverage**: 80%+
- **API Endpoints**: 12+
- **Database Tables**: 8
- **Supported Sources**: 3+ (estate sales, craigslist, garage sale finder)
- **Categories**: 8 (art, furniture, vintage, jewelry, electronics, books, collectibles, home decor)

---

## 🎓 Learning Value

This project demonstrates:

✅ **AI/ML**: Claude Vision API, agentic tool use, multimodal analysis  
✅ **Backend**: FastAPI, async Python, REST API design  
✅ **Database**: PostgreSQL, SQLAlchemy ORM, migrations, indexing  
✅ **Web Scraping**: BeautifulSoup, Selenium, handling multiple sources  
✅ **DevOps**: Docker, Docker Compose, CI/CD, GitHub Actions  
✅ **Testing**: Pytest, mocking, coverage reporting  
✅ **Production Patterns**: Error handling, logging, monitoring, health checks  
✅ **Documentation**: READMEs, API docs, architecture diagrams  

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see LICENSE file

---

## 🙋 About

Built to:
1. **Learn**: Deep dive into Claude AI, APIs, and production engineering
2. **Solve**: Real problem (finding deals) with agentic AI
3. **Impress**: Recruiters with full-stack AI project

---

## 📞 Questions?

Open an issue or reach out on [GitHub](https://github.com/biruppal/DealFinder)

---

<div align="center">

**[⬆ back to top](#-dealfinder---ai-powered-deal-analyzer)**

</div>
