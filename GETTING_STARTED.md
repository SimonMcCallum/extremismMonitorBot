# Getting Started - Development Setup

This guide will help you set up the development environment and start working on the Extremism Monitor Bot project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Python** 3.11+
- **Node.js** 18+ (for admin panel, later)
- **Git** 2.30+
- **Discord Bot Token** (from [Discord Developer Portal](https://discord.com/developers/applications))
- **Anthropic API Key** (from [Claude Console](https://console.anthropic.com/))

## Quick Start (Docker)

### 1. Clone the Repository

```bash
git clone https://github.com/SimonMcCallum/extremismMonitorBot.git
cd extremismMonitorBot
```

### 2. Set Up Environment Variables

Create `.env` files for each component:

```bash
# Copy example environment files
cp .env.example .env
cp discord-bot/.env.example discord-bot/.env
cp backend/.env.example backend/.env
```

Edit the `.env` files with your actual credentials:

**`discord-bot/.env`**:
```env
DISCORD_BOT_TOKEN=your_actual_bot_token_here
DISCORD_CLIENT_ID=your_actual_client_id_here
ANTHROPIC_API_KEY=your_actual_anthropic_key_here
DATABASE_URL=postgresql://extremism_user:password@postgres:5432/extremism_monitor
REDIS_URL=redis://redis:6379/0
```

**`backend/.env`**:
```env
DATABASE_URL=postgresql+asyncpg://extremism_user:password@postgres:5432/extremism_monitor
REDIS_URL=redis://redis:6379/0
ANTHROPIC_API_KEY=your_actual_anthropic_key_here
SECRET_KEY=your_generated_secret_key_here
```

### 3. Start All Services

```bash
# Start PostgreSQL, Redis, Backend API, and Discord Bot
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f bot
docker-compose logs -f api
```

### 4. Verify Services Are Running

```bash
# Check service status
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test API status
curl http://localhost:8000/api/v1/status
```

### 5. Invite Bot to Your Discord Server

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to OAuth2 → URL Generator
4. Select scopes: `bot`, `applications.commands`
5. Select bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History
   - Add Reactions
   - Use Slash Commands
6. Copy the generated URL and open it in your browser
7. Select your test server and authorize

### 6. Test the Bot

In your Discord server:
```
!status          # Check bot status (if using prefix commands)
/status          # Check bot status (slash command)
/sync            # Sync slash commands
```

## Local Development (Without Docker)

If you prefer to run services locally:

### 1. Set Up PostgreSQL

```bash
# Install PostgreSQL 15 with TimescaleDB
# macOS (using Homebrew)
brew install postgresql@15 timescaledb

# Ubuntu/Debian
sudo apt-get install postgresql-15 postgresql-15-timescaledb

# Create database
createdb extremism_monitor
psql -d extremism_monitor -f scripts/init-db.sql
```

### 2. Set Up Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Set Up Discord Bot

```bash
cd discord-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run bot
python main.py
```

### 4. Set Up Backend API

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run API
uvicorn main:app --reload --port 8000
```

## Running Tests

### Discord Bot Tests

```bash
cd discord-bot
source venv/bin/activate
pytest --cov=. --cov-report=html
```

### Backend API Tests

```bash
cd backend
source venv/bin/activate
pytest --cov=. --cov-report=html
```

### View Coverage Reports

```bash
# Bot coverage
open discord-bot/htmlcov/index.html

# Backend coverage
open backend/htmlcov/index.html
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit files in:
- `discord-bot/` for bot changes
- `backend/` for API changes
- `admin-panel/` for frontend changes (when available)

### 3. Run Tests

```bash
# Test bot
cd discord-bot && pytest

# Test backend
cd backend && pytest
```

### 4. Format Code

```bash
# Format with black
black discord-bot/ backend/

# Sort imports with isort
isort discord-bot/ backend/

# Check with pylint (optional)
pylint discord-bot/
pylint backend/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Common Tasks

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart bot
docker-compose restart api
```

### View Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U extremism_user -d extremism_monitor

# Common queries
\dt                  # List tables
SELECT * FROM servers;
SELECT * FROM users LIMIT 10;
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

### Clear Database

```bash
# Stop services
docker-compose down

# Remove volumes (this deletes all data!)
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Update Dependencies

```bash
# Bot dependencies
cd discord-bot
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt

# Backend dependencies
cd backend
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt
```

### Add New Database Table

1. Create SQLAlchemy model in `backend/models/`
2. Create Alembic migration:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new table"
   ```
3. Review and edit migration in `backend/alembic/versions/`
4. Apply migration:
   ```bash
   alembic upgrade head
   ```

## Troubleshooting

### Bot Not Starting

```bash
# Check logs
docker-compose logs bot

# Common issues:
# 1. Missing DISCORD_BOT_TOKEN
# 2. Invalid token
# 3. Missing privileged intents in Discord Developer Portal
```

### API Not Responding

```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
docker-compose logs api

# Common issues:
# 1. Port 8000 already in use
# 2. Database connection failed
# 3. Missing environment variables
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U extremism_user -d extremism_monitor

# Check logs
docker-compose logs postgres
```

### Import Errors

```bash
# Ensure you're in the correct directory
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Read the Documentation**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Detailed implementation
   - [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Development roadmap

2. **Explore the Code**
   - Discord bot: `discord-bot/`
   - Backend API: `backend/`
   - Database models: `backend/models/`

3. **Run the Tests**
   - Understand how testing works
   - Add tests for new features

4. **Start Contributing**
   - Pick a task from the development plan
   - Create a feature branch
   - Implement and test
   - Submit a pull request

## Getting Help

- **Documentation**: Check the `/docs` directory
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## Development Environment Status

✅ **Completed**:
- Project structure
- Discord bot foundation
- Backend API foundation
- Database schema
- Docker Compose setup
- Testing framework
- CI/CD pipeline

🔄 **In Progress**:
- AI risk assessment engine
- ML model implementation
- Admin panel

⏳ **Upcoming**:
- Daily risk updater
- Advanced analytics
- Production deployment

---

**Happy Coding!** 🚀

For questions or issues, please create an issue on GitHub or refer to the documentation.
