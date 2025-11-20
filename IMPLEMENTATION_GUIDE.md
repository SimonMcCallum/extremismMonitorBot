# Implementation Guide - Extremism Monitor Bot

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Configuration](#configuration)
5. [Development Workflow](#development-workflow)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python** 3.11 or higher
- **Node.js** 18 or higher (for admin panel)
- **Docker** 20.10+ and Docker Compose 2.0+
- **PostgreSQL** 15+ with TimescaleDB extension
- **Redis** 7+
- **Git** 2.30+

### Required Accounts
- **Discord Developer Portal** account
  - Create bot application
  - Enable necessary intents
- **Anthropic API** account
  - Get API key for Claude
- **Cloud Provider** (AWS/GCP/Azure) for production

### Development Tools
- **Code Editor**: VS Code (recommended) or PyCharm
- **API Client**: Postman or Insomnia
- **Database Client**: pgAdmin, DBeaver, or TablePlus

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/extremismMonitorBot.git
cd extremismMonitorBot

# Run the setup script
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy example environment files
cp .env.example .env
cp discord-bot/.env.example discord-bot/.env
cp backend/.env.example backend/.env
cp admin-panel/.env.example admin-panel/.env

# Edit .env files with your credentials
nano .env
```

### 3. Start Development Environment

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Seed initial data (optional)
docker-compose exec api python scripts/seed_data.py
```

### 5. Access Services

- **Bot**: Invite to Discord server using OAuth2 URL
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000
- **Database**: localhost:5432

## Detailed Installation

### Step 1: Discord Bot Setup

#### Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Name it "Extremism Monitor Bot"
4. Go to "Bot" section
5. Click "Add Bot"
6. **Important**: Enable these Privileged Gateway Intents:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent

#### Get Bot Token

1. In Bot section, click "Reset Token"
2. Copy the token (you'll need this for `.env`)
3. **Never share this token publicly!**

#### Set Bot Permissions

Required permissions (permission integer: 8589934592):
- Read Messages/View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History
- Add Reactions
- Use Slash Commands
- Manage Messages (for cleanup)

#### Generate Invite URL

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8589934592&scope=bot%20applications.commands
```

Replace `YOUR_CLIENT_ID` with your application's client ID.

### Step 2: Project Structure Setup

```bash
# Create directory structure
mkdir -p {discord-bot,backend,admin-panel,scripts,docs,tests}
mkdir -p discord-bot/{cogs,utils,models}
mkdir -p backend/{api,models,services,ml,tasks}
mkdir -p admin-panel/{src,public}
mkdir -p scripts/{deployment,maintenance}
```

### Step 3: Discord Bot Installation

```bash
cd discord-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install discord.py==2.3.2 \
            anthropic==0.8.1 \
            python-dotenv==1.0.0 \
            asyncpg==0.29.0 \
            redis==5.0.1 \
            aiohttp==3.9.1 \
            pydantic==2.5.0 \
            loguru==0.7.2
```

#### Discord Bot Configuration

Create `discord-bot/.env`:

```env
# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id_here

# Backend API
API_BASE_URL=http://localhost:8000
API_KEY=your_api_key_here

# Claude AI
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=postgresql://extremism_user:password@localhost:5432/extremism_monitor

# Redis
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Features
ENABLE_RISK_MONITORING=true
ENABLE_ENGAGEMENT_TRACKING=true
ENABLE_AUTO_ALERTS=true

# Thresholds
RISK_ALERT_THRESHOLD=70
MESSAGE_BATCH_SIZE=100
ANALYSIS_DELAY_SECONDS=2
```

### Step 4: Backend API Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install fastapi==0.104.1 \
            uvicorn[standard]==0.24.0 \
            sqlalchemy==2.0.23 \
            alembic==1.12.1 \
            asyncpg==0.29.0 \
            redis==5.0.1 \
            python-jose[cryptography]==3.3.0 \
            passlib[bcrypt]==1.7.4 \
            python-multipart==0.0.6 \
            anthropic==0.8.1 \
            scikit-learn==1.3.2 \
            torch==2.1.1 \
            transformers==4.35.2 \
            sentence-transformers==2.2.2 \
            chromadb==0.4.18 \
            celery==5.3.4 \
            pydantic==2.5.0 \
            pydantic-settings==2.1.0
```

#### Backend Configuration

Create `backend/.env`:

```env
# Application
APP_NAME=Extremism Monitor API
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://extremism_user:password@localhost:5432/extremism_monitor
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Claude AI
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229
MAX_TOKENS=4096

# ML Models
ML_MODEL_PATH=./models
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./data/vectordb

# Celery (for background tasks)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Monitoring
ENABLE_PROMETHEUS=true
PROMETHEUS_PORT=9090
```

#### Database Setup

```bash
# Create PostgreSQL database
createdb extremism_monitor

# Or using psql
psql -U postgres
CREATE DATABASE extremism_monitor;
CREATE USER extremism_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE extremism_monitor TO extremism_user;

# Enable extensions
\c extremism_monitor
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pgvector;
```

#### Run Migrations

```bash
cd backend

# Initialize Alembic
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Step 5: Admin Panel Installation

```bash
cd admin-panel

# Install Node.js dependencies
npm install

# Or using yarn
yarn install

# Install specific packages
npm install react react-dom react-router-dom \
            @tanstack/react-query \
            axios \
            zustand \
            tailwindcss \
            @headlessui/react \
            @heroicons/react \
            recharts \
            date-fns \
            react-hook-form \
            zod
```

#### Admin Panel Configuration

Create `admin-panel/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_NAME=Extremism Monitor Admin
VITE_ENVIRONMENT=development
```

### Step 6: Docker Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: extremism-postgres
    environment:
      POSTGRES_USER: extremism_user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: extremism_monitor
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - extremism-network

  redis:
    image: redis:7-alpine
    container_name: extremism-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - extremism-network

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: extremism-api
    environment:
      - DATABASE_URL=postgresql+asyncpg://extremism_user:password@postgres:5432/extremism_monitor
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
      - ./backend/models:/app/models
    networks:
      - extremism-network
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  bot:
    build:
      context: ./discord-bot
      dockerfile: Dockerfile
    container_name: extremism-bot
    environment:
      - API_BASE_URL=http://api:8000
      - DATABASE_URL=postgresql://extremism_user:password@postgres:5432/extremism_monitor
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - api
      - postgres
      - redis
    volumes:
      - ./discord-bot:/app
    networks:
      - extremism-network
    restart: unless-stopped

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: extremism-celery
    environment:
      - DATABASE_URL=postgresql+asyncpg://extremism_user:password@postgres:5432/extremism_monitor
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    networks:
      - extremism-network
    command: celery -A tasks.celery_app worker --loglevel=info

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: extremism-celery-beat
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - redis
    networks:
      - extremism-network
    command: celery -A tasks.celery_app beat --loglevel=info

  admin-panel:
    build:
      context: ./admin-panel
      dockerfile: Dockerfile
    container_name: extremism-admin
    ports:
      - "3000:3000"
    volumes:
      - ./admin-panel:/app
      - /app/node_modules
    networks:
      - extremism-network
    environment:
      - VITE_API_BASE_URL=http://localhost:8000

networks:
  extremism-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

## Configuration

### Discord Bot Configuration

Key settings in `discord-bot/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Discord
    discord_bot_token: str
    discord_client_id: str

    # API
    api_base_url: str
    api_key: str

    # AI
    anthropic_api_key: str

    # Risk thresholds
    risk_low_threshold: int = 30
    risk_medium_threshold: int = 60
    risk_high_threshold: int = 85

    # Performance
    message_batch_size: int = 100
    analysis_delay: float = 2.0
    max_concurrent_analyses: int = 5

    class Config:
        env_file = ".env"
```

### Backend Configuration

Key settings in `backend/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_name: str = "Extremism Monitor API"
    debug: bool = False

    # Database
    database_url: str
    database_pool_size: int = 20

    # Redis
    redis_url: str

    # Auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # AI
    anthropic_api_key: str
    claude_model: str = "claude-3-sonnet-20240229"

    # ML
    ml_model_path: str = "./models"
    embedding_model: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
```

## Development Workflow

### Running Services Locally

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

#### Option 2: Manual Start

```bash
# Terminal 1: PostgreSQL & Redis (if not using Docker)
# See installation instructions for your OS

# Terminal 2: Backend API
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 3: Celery Worker
cd backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info

# Terminal 4: Celery Beat (scheduler)
cd backend
source venv/bin/activate
celery -A tasks.celery_app beat --loglevel=info

# Terminal 5: Discord Bot
cd discord-bot
source venv/bin/activate
python main.py

# Terminal 6: Admin Panel
cd admin-panel
npm run dev
```

### Making Code Changes

1. **Bot Changes**
   ```bash
   # Edit files in discord-bot/
   # Bot will auto-reload if using --reload flag
   ```

2. **Backend Changes**
   ```bash
   # Edit files in backend/
   # FastAPI will auto-reload with --reload
   ```

3. **Database Changes**
   ```bash
   # Create migration
   cd backend
   alembic revision --autogenerate -m "Description"

   # Review migration file

   # Apply migration
   alembic upgrade head
   ```

4. **Admin Panel Changes**
   ```bash
   # Vite will auto-reload on file changes
   ```

### Code Quality Tools

```bash
# Format code
black discord-bot/ backend/
isort discord-bot/ backend/

# Lint
pylint discord-bot/ backend/
flake8 discord-bot/ backend/

# Type checking
mypy discord-bot/ backend/

# Frontend
cd admin-panel
npm run lint
npm run format
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_risk_assessment.py

# Run specific test
pytest tests/test_risk_assessment.py::test_high_risk_detection
```

### Bot Tests

```bash
cd discord-bot

# Run all tests
pytest

# Run integration tests
pytest tests/integration/

# Run unit tests only
pytest tests/unit/
```

### Frontend Tests

```bash
cd admin-panel

# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## Deployment

### Production Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup system
- [ ] Set up monitoring and alerting
- [ ] Review and test disaster recovery plan
- [ ] Conduct security audit
- [ ] Set up log aggregation
- [ ] Configure auto-scaling
- [ ] Test rate limiting
- [ ] Review privacy policy compliance

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/bot.yaml
kubectl apply -f k8s/admin-panel.yaml

# Check status
kubectl get pods -n extremism-monitor

# View logs
kubectl logs -f deployment/api -n extremism-monitor
```

### Environment Variables for Production

Create `.env.production`:

```env
# Security - CHANGE THESE!
SECRET_KEY=generate-a-strong-random-key-here
DATABASE_PASSWORD=strong-random-password
REDIS_PASSWORD=strong-random-password

# Disable debug
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://extremism_user:${DATABASE_PASSWORD}@postgres:5432/extremism_monitor
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["https://yourdomain.com"]

# HTTPS
USE_HTTPS=true
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENABLE_PROMETHEUS=true
```

## Troubleshooting

### Common Issues

#### Bot Not Responding

```bash
# Check bot is running
docker-compose ps bot

# View bot logs
docker-compose logs bot

# Common fixes:
# 1. Verify bot token is correct
# 2. Check privileged intents are enabled
# 3. Ensure bot has proper permissions in Discord
# 4. Verify API connection
```

#### Database Connection Errors

```bash
# Test connection
docker-compose exec postgres psql -U extremism_user -d extremism_monitor

# Common fixes:
# 1. Verify DATABASE_URL is correct
# 2. Check PostgreSQL is running
# 3. Ensure database exists
# 4. Verify user permissions
```

#### API Not Accessible

```bash
# Check API is running
curl http://localhost:8000/health

# View API logs
docker-compose logs api

# Common fixes:
# 1. Check port 8000 is not in use
# 2. Verify environment variables
# 3. Check database migrations ran
# 4. Review CORS settings
```

#### High Memory Usage

```bash
# Monitor resource usage
docker stats

# Common fixes:
# 1. Reduce MESSAGE_BATCH_SIZE
# 2. Limit MAX_CONCURRENT_ANALYSES
# 3. Increase server resources
# 4. Enable message caching
```

### Debug Mode

Enable detailed logging:

```env
# In .env
LOG_LEVEL=DEBUG
SQLALCHEMY_ECHO=true
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# Bot health (check logs)
docker-compose logs bot | grep "Bot is ready"
```

## Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)

## Support

For issues and questions:
- Create an issue on GitHub
- Check documentation at `/docs`
- Review logs for error messages
- Consult architecture documentation

---

**Version**: 1.0.0
**Last Updated**: 2024-11-20
