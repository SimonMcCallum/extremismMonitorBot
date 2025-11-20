# Project Summary - Extremism Monitor Bot

## Quick Reference Guide

### What is this project?

An AI-powered Discord bot system that helps game community managers:
1. **Monitor radicalization risks** using Claude AI to analyze conversations
2. **Track user engagement** to predict and prevent community churn
3. **Learn and improve** through self-learning ML models
4. **Stay updated** with daily risk profile updates from trusted sources

### Who is it for?

- **Game Community Managers**: Protect your gaming communities from toxic escalation
- **Discord Server Admins**: Maintain healthy, safe community spaces
- **Enterprise Communities**: Monitor corporate Discord servers for compliance
- **Educational Institutions**: Protect students in online learning communities

## System Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Discord Bot** | Python + discord.py | Monitors messages, tracks users |
| **Backend API** | FastAPI + PostgreSQL | Stores data, serves admin panel |
| **AI Engine** | Anthropic Claude | Analyzes content for risks |
| **ML System** | scikit-learn + PyTorch | Self-learning risk models |
| **Admin Panel** | React + TypeScript | Web dashboard for management |
| **Daily Updater** | Celery + Claude | Updates risk profiles daily |

## Key Features Summary

### 🔍 Risk Monitoring
- Real-time message analysis
- Multi-level risk scoring (0-100)
- Context-aware AI assessment
- Historical pattern tracking
- Automatic moderator alerts

### 📊 Engagement Analytics
- User activity tracking
- Churn prediction models
- Community health metrics
- Participation trends
- Social network analysis

### 🤖 Self-Learning
- Continuous model improvement
- Feedback integration
- A/B testing framework
- Performance monitoring
- Bias mitigation

### ⚙️ Admin Controls
- Web-based dashboard
- Real-time alerts
- Customizable thresholds
- Export capabilities
- Role-based access

## How It Works

```
1. User posts message in Discord
   ↓
2. Bot captures message + context
   ↓
3. AI analyzes content (Claude API)
   ↓
4. ML model calculates risk score
   ↓
5. If risk threshold exceeded → Alert moderator
   ↓
6. Moderator reviews and takes action
   ↓
7. Feedback improves future predictions
```

## Quick Setup (3 Steps)

### Step 1: Get API Keys
- Create Discord bot at [Discord Developer Portal](https://discord.com/developers/applications)
- Get Anthropic API key at [Claude Console](https://console.anthropic.com/)

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your keys
```

### Step 3: Run with Docker
```bash
docker-compose up -d
```

That's it! Access admin panel at http://localhost:3000

## File Structure Overview

```
extremismMonitorBot/
│
├── 📄 README.md                    # Main project documentation
├── 📄 ARCHITECTURE.md               # Detailed system design
├── 📄 IMPLEMENTATION_GUIDE.md       # Installation & setup instructions
├── 📄 PROJECT_SUMMARY.md            # This file - quick reference
│
├── 🤖 discord-bot/                  # Discord bot application
│   ├── main.py                     # Bot entry point
│   ├── cogs/                       # Command modules
│   ├── utils/                      # Helper functions
│   └── requirements.txt            # Python dependencies
│
├── 🔧 backend/                      # FastAPI backend
│   ├── main.py                     # API entry point
│   ├── api/                        # API endpoints
│   ├── models/                     # Database models
│   ├── services/                   # Business logic
│   ├── ml/                         # ML models & training
│   └── tasks/                      # Background tasks
│
├── 💻 admin-panel/                  # React admin interface
│   ├── src/
│   │   ├── pages/                  # Page components
│   │   ├── components/             # React components
│   │   └── api/                    # API client
│   └── package.json
│
├── 🐳 docker-compose.yml            # Docker orchestration
├── 📋 .env.example                  # Environment variables template
├── 🚫 .gitignore                    # Git ignore rules
│
└── 📚 docs/                         # Additional documentation
```

## Database Schema (Simplified)

```sql
servers         # Discord servers registered
  ├── id, discord_id, name, settings

users           # Discord users being tracked
  ├── id, discord_id, risk_score, engagement_score

messages        # Archived messages
  ├── id, discord_message_id, user_id, content

risk_assessments # AI analysis results
  ├── id, message_id, risk_score, indicators

alerts          # Moderator alerts
  ├── id, user_id, severity, status

engagement_metrics # Time-series data
  └── time, user_id, metric_type, value
```

## Risk Assessment Flow

```python
def assess_risk(message):
    # 1. Extract features
    features = {
        'sentiment': analyze_sentiment(message),
        'toxicity': detect_toxicity(message),
        'keywords': match_risk_keywords(message),
        'context': get_conversation_context(message),
        'user_history': get_user_patterns(message.author)
    }

    # 2. AI analysis (Claude)
    ai_analysis = claude_analyze(message, context)

    # 3. ML prediction
    ml_score = ml_model.predict(features)

    # 4. Combine scores
    final_score = weighted_average([
        ai_analysis.score,
        ml_score,
        pattern_score
    ])

    # 5. Take action based on threshold
    if final_score > HIGH_THRESHOLD:
        alert_moderator(message, final_score)

    return final_score
```

## Configuration Examples

### Low Sensitivity (Gaming Banter)
```env
RISK_LOW_THRESHOLD=40
RISK_MEDIUM_THRESHOLD=70
RISK_HIGH_THRESHOLD=90
ENABLE_AUTO_ALERTS=false
```

### High Sensitivity (Educational)
```env
RISK_LOW_THRESHOLD=20
RISK_MEDIUM_THRESHOLD=50
RISK_HIGH_THRESHOLD=75
ENABLE_AUTO_ALERTS=true
```

## API Endpoints Overview

### Bot Management
- `GET /api/v1/servers` - List registered servers
- `POST /api/v1/servers` - Register new server
- `PATCH /api/v1/servers/{id}/settings` - Update settings

### Risk Management
- `GET /api/v1/risks/alerts` - Get active alerts
- `GET /api/v1/risks/profiles` - Current risk profiles
- `POST /api/v1/risks/assess` - Manual assessment

### Analytics
- `GET /api/v1/analytics/engagement` - Engagement metrics
- `GET /api/v1/analytics/churn` - Churn predictions
- `POST /api/v1/analytics/export` - Export data

## Development Phases

| Phase | Duration | Status | Description |
|-------|----------|--------|-------------|
| Phase 1 | Week 1-2 | ✅ Complete | Architecture & planning |
| Phase 2 | Week 3-4 | 🔄 Next | Core bot implementation |
| Phase 3 | Week 5-6 | ⏳ Pending | Backend API development |
| Phase 4 | Week 7-9 | ⏳ Pending | ML system implementation |
| Phase 5 | Week 10-11 | ⏳ Pending | Admin panel creation |
| Phase 6 | Week 12-13 | ⏳ Pending | Testing & optimization |
| Phase 7 | Week 14-16 | ⏳ Pending | Production deployment |

## Cost Estimates

### Development Costs
- Development time: 14-16 weeks
- Team size: 3-4 developers
- Total: $50k-80k

### Monthly Operating Costs (100 communities)
- Cloud hosting: $300-500
- Claude API: $500-1000
- Database: $200
- Redis: $50
- Monitoring: $100
- **Total: ~$1,200-1,900/month**

Scales to ~+$500/month per 100 additional communities

## Security & Privacy Features

✅ **Encryption**
- Data at rest: AES-256
- Data in transit: TLS 1.3
- Encrypted backups

✅ **Privacy**
- GDPR compliant
- Configurable data retention
- Right to deletion
- Data export capability

✅ **Access Control**
- Role-based permissions
- Audit logging
- API rate limiting
- IP whitelisting

✅ **Ethical AI**
- Explainable decisions
- Human oversight required
- Regular bias audits
- Transparent scoring

## Monitoring Metrics

### System Health
- Bot uptime (target: 99.9%)
- API response time (target: <200ms)
- Database performance
- Error rates (target: <0.1%)

### ML Performance
- Model accuracy (target: >90%)
- False positive rate (target: <5%)
- False negative rate (target: <2%)
- Prediction confidence

### Business Metrics
- Communities served
- Messages analyzed
- Alerts generated
- Actions taken
- User satisfaction

## Common Use Cases

### Gaming Community (10,000 users)
- Average: 50,000 messages/day
- Risk alerts: 5-10/day
- Churn predictions: Weekly reports
- Cost: ~$150/month

### Educational Server (1,000 students)
- Average: 10,000 messages/day
- Risk alerts: 2-5/day
- Engagement tracking: Daily
- Cost: ~$50/month

### Enterprise Community (500 employees)
- Average: 5,000 messages/day
- Risk alerts: 1-3/day
- Compliance reports: Weekly
- Cost: ~$40/month

## Next Steps to Get Started

1. **Review Documentation**
   - Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
   - Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for setup

2. **Set Up Development Environment**
   - Install Docker & Docker Compose
   - Get Discord bot token
   - Get Anthropic API key

3. **Clone and Configure**
   ```bash
   git clone <repository>
   cd extremismMonitorBot
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run Development Server**
   ```bash
   docker-compose up -d
   ```

5. **Access Services**
   - Bot: Invite to Discord
   - API: http://localhost:8000/docs
   - Admin: http://localhost:3000

## Support & Resources

### Documentation
- **Architecture**: System design and components
- **Implementation**: Installation and setup
- **API Docs**: http://localhost:8000/docs (when running)

### External Resources
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude Docs](https://docs.anthropic.com/)

### Community
- GitHub Issues for bugs
- Discussions for questions
- Wiki for guides and tutorials

## Important Ethical Guidelines

⚠️ **This tool must be used responsibly:**

1. **Inform Users**: Users should know monitoring is happening
2. **Human Review**: AI should assist, not replace, human judgment
3. **Privacy First**: Collect only necessary data, respect privacy
4. **Fair & Unbiased**: Regular audits, diverse training data
5. **Transparent**: Clear explanation of how assessments work
6. **Accountable**: Appeal processes, correction mechanisms

## Frequently Asked Questions

**Q: Does this replace human moderators?**
A: No, it assists moderators by flagging potential issues for human review.

**Q: How accurate is the risk assessment?**
A: Target accuracy is >90%, but human judgment is always required.

**Q: What data is collected?**
A: Messages, user interactions, and metadata. Configurable retention periods.

**Q: Is it GDPR compliant?**
A: Yes, with data export, deletion, and transparency features.

**Q: Can users opt out?**
A: Server admins control deployment. Individual opt-out depends on implementation.

**Q: How much does it cost to run?**
A: ~$1,200-1,900/month for 100 communities, scales with usage.

**Q: Can I self-host?**
A: Yes, fully self-hostable with Docker or Kubernetes.

**Q: What languages are supported?**
A: Currently English, with plans for multi-language support.

---

**Document Version**: 1.0
**Last Updated**: 2024-11-20
**Status**: Planning Phase Complete

For detailed information, see:
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Setup instructions
