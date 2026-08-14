# 📋 Setup & Deployment Guide

Complete guide to setting up DealFinder locally, testing, and deploying to production.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Setup](#docker-setup)
3. [Database Setup](#database-setup)
4. [API Keys & Configuration](#api-keys--configuration)
5. [Running Tests](#running-tests)
6. [Deployment](#deployment)

---

## Local Development

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15+ (or Docker)
- Git
- Claude API key

### Step 1: Clone Repository

```bash
git clone https://github.com/biruppal/DealFinder.git
cd DealFinder
```

### Step 2: Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example
cp .env.example .env

# Edit with your settings
nano .env  # or use your favorite editor
```

**Required variables**:
```env
ANTHROPIC_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://localhost/dealfinder
ENVIRONMENT=development
```

### Step 5: Set Up Database (Local PostgreSQL)

```bash
# Create database
createdb dealfinder

# Or if using PostgreSQL admin
psql -U postgres -c "CREATE DATABASE dealfinder;"

# Run migrations
alembic upgrade head
```

### Step 6: Run API Server

```bash
# Terminal 1: API Server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Scraper (optional)
python -m scrapers.run_scrapers
```

**Visit**:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Quick Start

```bash
# From project root
cd DealFinder

# Set up environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check logs
docker-compose -f docker/docker-compose.yml logs -f api

# Run migrations
docker-compose -f docker/docker-compose.yml exec api alembic upgrade head

# Check health
curl http://localhost:8000/health
```

### Services Started

```
✓ PostgreSQL (port 5432)
✓ FastAPI (port 8000)
✓ Redis (port 6379) - for caching/sessions
```

### Useful Commands

```bash
# View logs
docker-compose -f docker/docker-compose.yml logs api

# Access database
docker-compose -f docker/docker-compose.yml exec db psql -U dealfinder

# Stop all services
docker-compose -f docker/docker-compose.yml down

# Restart API
docker-compose -f docker/docker-compose.yml restart api

# View running services
docker-compose -f docker/docker-compose.yml ps
```

---

## Database Setup

### Manual PostgreSQL Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create user
CREATE USER dealfinder WITH PASSWORD 'dev_password';

# Create database
CREATE DATABASE dealfinder OWNER dealfinder;

# Enable extensions
\c dealfinder
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

# Exit
\q
```

### Alembic Migrations

```bash
# View migration history
alembic history

# Run pending migrations
alembic upgrade head

# Create new migration (after changing models)
alembic revision --autogenerate -m "Add new_column to listings"

# Rollback last migration
alembic downgrade -1

# Create initial migration
alembic revision --autogenerate -m "Initial migration"
```

### Database Verification

```bash
# Connect to database
psql -U dealfinder -d dealfinder -h localhost

# List tables
\dt

# Check listings table
SELECT * FROM listings LIMIT 5;

# Check indexes
\d listings

# Exit
\q
```

---

## API Keys & Configuration

### Claude API Key

1. Go to https://console.anthropic.com
2. Create API key
3. Add to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Notification Services

#### Email (Optional)

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Not your regular password!
```

**For Gmail**:
1. Enable 2FA
2. Generate app password
3. Use app password in `.env`

#### Telegram (Optional)

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
```

**Setup**:
1. Create bot with @BotFather
2. Get token
3. Send message to bot
4. Get chat ID from bot

---

## Running Tests

### All Tests

```bash
# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
# or
firefox htmlcov/index.html  # Linux
```

### Specific Tests

```bash
# Test agent only
pytest tests/test_agent.py -v

# Test API only
pytest tests/test_api.py -v

# Test one function
pytest tests/test_agent.py::TestDealAnalyzer::test_agent_initialization -v

# Run marked tests
pytest -m "not slow" -v
```

### Test Coverage by Component

```
tests/
├── test_agent.py         # Agent logic, vision, tool use
├── test_scrapers.py      # Web scraping functionality
├── test_api.py           # FastAPI endpoints
├── test_db.py            # Database operations
└── conftest.py           # Pytest fixtures
```

### CI/CD Testing (GitHub Actions)

Tests run automatically on:
- Push to main/develop
- Pull requests

View in **GitHub** → **Actions** tab

---

## Deployment

### Option 1: Railway (Recommended for Beginners)

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Connect Repository**
   - Create new project
   - Select "Deploy from GitHub repo"
   - Choose DealFinder repo

3. **Add Services**
   ```bash
   # In Railway dashboard:
   # - Add PostgreSQL plugin
   # - Add Redis plugin
   ```

4. **Set Environment Variables**
   ```bash
   ANTHROPIC_API_KEY=sk-...
   ENVIRONMENT=production
   ```

5. **Deploy**
   - Railway auto-deploys on git push

### Option 2: Render

1. **Create Render Account**
   - Go to https://render.com
   - Sign up

2. **Create Web Service**
   - New → Web Service
   - Connect GitHub repo
   - Select DealFinder

3. **Configure**
   ```
   Build Command: pip install -r requirements.txt && alembic upgrade head
   Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add PostgreSQL**
   - Create new PostgreSQL database
   - Get connection string
   - Add to environment variables

### Option 3: Docker to Cloud (DigitalOcean, AWS, Google Cloud)

```bash
# Build image
docker build -f docker/Dockerfile -t dealfinder:latest .

# Tag for registry
docker tag dealfinder:latest your-registry/dealfinder:latest

# Push to registry
docker push your-registry/dealfinder:latest

# Deploy (depends on platform)
```

### Post-Deployment

```bash
# Run migrations on deployed database
# (Use your platform's CLI or SSH)

alembic upgrade head

# Check health
curl https://your-deployed-url.com/health

# Monitor logs
# (Check your platform's log viewer)
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "SQLALCHEMY_DATABASE_URL not set"

```bash
# Make sure .env is loaded
export $(cat .env | xargs)
# or
source .env
```

### "psycopg2: could not connect to server"

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Or with Docker
docker-compose ps
```

### "No module named 'fastapi'"

```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall
pip install fastapi uvicorn
```

### Port 8000 already in use

```bash
# Use different port
uvicorn api.main:app --port 8001

# Or kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Docker container won't start

```bash
# Check logs
docker-compose logs api

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose up -d
```

---

## Development Workflow

### Before Committing

```bash
# Format code
black . --line-length 127

# Lint
flake8 . --max-line-length 127

# Type check
mypy --ignore-missing-imports agent/ api/

# Test
pytest tests/ -v

# Coverage
pytest tests/ --cov=. --cov-report=term-missing
```

### Commit Message Format

```
feat: Add new feature
fix: Fix a bug
docs: Update documentation
test: Add/update tests
refactor: Refactor code
```

### Pull Request Process

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests and linting
4. Push: `git push origin feature/your-feature`
5. Create PR
6. Wait for CI to pass
7. Get review
8. Merge to main

---

## Additional Resources

- [Anthropic Docs](https://docs.anthropic.com)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [PostgreSQL Docs](https://www.postgresql.org/docs)
- [Docker Docs](https://docs.docker.com)

---

## Monitoring & Logging

### Local Logging

```bash
# Check API logs
tail -f logs/api.log

# Check scraper logs
tail -f logs/scraper.log
```

### Deployed Monitoring

- **Railway**: Dashboard → Monitoring tab
- **Render**: Dashboard → Logs
- **CloudWatch** (AWS): View metrics and logs

---

## Performance Tips

1. **Database Indexes**: Already optimized in `db/models.py`
2. **Caching**: Redis configured in `docker-compose.yml`
3. **Async**: FastAPI uses async/await for concurrency
4. **Batch Queries**: Use `joinedload` for relationships

---

Questions? Check [README.md](../README.md) or open an issue!
