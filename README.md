# Extremism Monitor Bot 🛡️

An AI-powered Discord bot system designed to help game community managers identify and mitigate radicalization risks while tracking user engagement patterns to improve community health.

## 🎯 Overview

This system provides:
- **Real-time Risk Monitoring**: AI-powered analysis of Discord conversations to identify radicalization indicators
- **Self-Learning System**: Machine learning models that improve over time based on moderator feedback
- **Engagement Analytics**: Track user engagement patterns and predict community churn
- **Admin Dashboard**: Web-based control panel for monitoring and configuration
- **Daily Risk Updates**: Automated system that updates risk profiles from trusted sources
- **Privacy-Focused**: GDPR compliant with configurable data retention

## 🏗️ Architecture

```
Discord Communities → Discord Bot → Backend API → ML Engine
                                         ↓
                               Admin Panel + Database
```

**Key Components:**
1. **Discord Bot Client** - Monitors messages and user interactions
2. **Backend API Platform** - FastAPI-based REST API and WebSocket server
3. **AI Risk Assessment Engine** - Claude-powered content analysis
4. **ML Self-Learning System** - Continuous improvement from feedback
5. **Daily Risk Profile Updater** - Automated updates from external sources
6. **Admin Panel** - React-based web interface

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ with TimescaleDB
- Discord Bot Token
- Anthropic API Key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/extremismMonitorBot.git
cd extremismMonitorBot

# Copy environment files
cp .env.example .env
# Edit .env with your credentials

# Start with Docker Compose
docker-compose up -d

# Initialize database
docker-compose exec api alembic upgrade head

# Invite bot to your Discord server
# Use the OAuth2 URL from Discord Developer Portal
```

### First Time Setup

1. **Create Discord Application**
   - Visit [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Enable bot with required intents
   - Copy bot token

2. **Get Anthropic API Key**
   - Sign up at [Anthropic](https://console.anthropic.com/)
   - Generate API key

3. **Configure Environment**
   - Add tokens to `.env` file
   - Set risk thresholds
   - Configure alert settings

4. **Access Admin Panel**
   - Navigate to http://localhost:3000
   - Create admin account
   - Register your Discord server

## 📚 Documentation

- **[Architecture Guide](ARCHITECTURE.md)** - Complete system design and technical specifications
- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Detailed installation and development instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🛠️ Development

### Project Structure

```
extremismMonitorBot/
├── discord-bot/          # Discord bot client
│   ├── cogs/            # Bot command modules
│   ├── utils/           # Utility functions
│   └── main.py          # Bot entry point
├── backend/             # FastAPI backend
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   ├── ml/              # ML models and training
│   └── tasks/           # Celery background tasks
├── admin-panel/         # React admin interface
│   └── src/
│       ├── components/  # React components
│       ├── pages/       # Page components
│       └── api/         # API client
├── scripts/             # Deployment and maintenance scripts
├── docs/                # Additional documentation
└── tests/               # Test suites
```

### Running Locally

```bash
# Backend API
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Discord Bot
cd discord-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Admin Panel
cd admin-panel
npm install
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest --cov

# Bot tests
cd discord-bot
pytest

# Frontend tests
cd admin-panel
npm run test
```

## 🔒 Security & Privacy

- **Data Encryption**: All data encrypted at rest and in transit
- **Access Control**: Role-based permissions for admin panel
- **Privacy Compliance**: GDPR compliant with data export/deletion
- **Ethical AI**: Transparent risk assessments with human oversight
- **Audit Logging**: Complete audit trail of all actions

## 📊 Features

### For Community Managers

✅ **Real-time Monitoring**
- Automatic scanning of all messages
- Configurable alert thresholds
- Multi-level severity alerts

✅ **Risk Assessment**
- AI-powered content analysis
- Pattern detection across conversations
- Historical trend tracking

✅ **Engagement Analytics**
- User activity tracking
- Churn prediction
- Community health metrics

✅ **Admin Controls**
- Web-based dashboard
- Customizable settings
- Export and reporting tools

### For Platform Administrators

✅ **Self-Learning System**
- Continuous model improvement
- Feedback integration
- A/B testing capabilities

✅ **Daily Updates**
- Automated risk profile updates
- Integration with trusted sources
- Version control for risk data

✅ **Scalability**
- Multi-server support
- Horizontal scaling
- Performance optimization

## 🎮 Use Cases

### Game Community Management
- Monitor toxic behavior escalation
- Identify at-risk community members
- Track engagement and retention
- Improve community health

### Enterprise Discord Servers
- Corporate community safety
- Employee engagement tracking
- Compliance monitoring

### Educational Communities
- Student safety monitoring
- Early intervention systems
- Engagement analytics

## 🤝 Contributing

We welcome contributions! See development phases below.

### Development Phases

- [x] **Phase 1**: Architecture and planning
- [ ] **Phase 2**: Core bot implementation
- [ ] **Phase 3**: Backend API development
- [ ] **Phase 4**: ML system implementation
- [ ] **Phase 5**: Admin panel development
- [ ] **Phase 6**: Testing and optimization
- [ ] **Phase 7**: Production deployment

## 📈 Roadmap

**Current Phase: Planning & Architecture**
- ✅ System architecture design
- ✅ Database schema design
- ✅ Implementation guide
- 🔄 Initial project setup

**Next Steps**
- Core bot implementation
- Backend API development
- ML model training
- Admin panel creation

## 🔧 Configuration

### Risk Thresholds

```env
RISK_LOW_THRESHOLD=30      # Log only
RISK_MEDIUM_THRESHOLD=60   # Monitor closely
RISK_HIGH_THRESHOLD=85     # Alert moderator
RISK_CRITICAL_THRESHOLD=95 # Immediate action
```

### Features

```env
ENABLE_RISK_MONITORING=true
ENABLE_ENGAGEMENT_TRACKING=true
ENABLE_AUTO_ALERTS=true
ENABLE_ML_PREDICTIONS=true
```

## ⚠️ Ethical Considerations

This tool is designed to help community managers identify potential radicalization risks. It should be used responsibly:

- **Transparency**: Users should be informed about monitoring
- **Human Oversight**: AI assessments require human review
- **Privacy**: Minimize data collection and respect privacy rights
- **Fairness**: Regular bias audits and diverse training data
- **Accountability**: Clear processes for appeals and corrections

## 🙏 Acknowledgments

- Discord.py community
- Anthropic Claude AI
- Open-source security research community
- Organizations fighting online extremism

---

**Status**: 🔄 In Development (Planning Phase)
**Version**: 1.0.0-alpha
**Last Updated**: 2024-11-20

For detailed technical documentation, see [ARCHITECTURE.md](ARCHITECTURE.md) and [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md).
