# Extremism Monitor Bot - System Architecture & Implementation Plan

## Executive Summary

This document outlines the architecture for a Discord bot system designed to help game community managers monitor and mitigate radicalization risks while also tracking user engagement patterns.

## System Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      DISCORD COMMUNITIES                         │
│                    (Game Communities)                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DISCORD BOT CLIENT                            │
│  - Message Monitoring                                            │
│  - Real-time Risk Assessment                                     │
│  - User Interaction Tracking                                     │
│  - Admin Commands                                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API PLATFORM                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │  REST API       │  │  WebSocket       │  │  Admin Panel   │ │
│  │  Server         │  │  Real-time       │  │  Web UI        │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────────┐
│  AI RISK     │ │  ML ENGINE  │ │  DAILY UPDATER   │
│  ASSESSMENT  │ │  Self-      │ │  Risk Profile    │
│  ENGINE      │ │  Learning   │ │  Crawler         │
└──────────────┘ └─────────────┘ └──────────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                                │
│  - User Profiles & History                                       │
│  - Message Archive                                               │
│  - Risk Assessments                                              │
│  - Engagement Metrics                                            │
│  - Training Data                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Discord Bot
- **Language**: Python 3.11+
- **Framework**: discord.py 2.x
- **AI Integration**: Anthropic Claude API
- **Async Framework**: asyncio

### Backend Platform
- **Framework**: FastAPI (Python)
- **API**: REST + WebSocket
- **Authentication**: JWT tokens
- **Rate Limiting**: Redis-based

### AI & ML Components
- **AI Provider**: Anthropic Claude (for analysis)
- **ML Framework**: scikit-learn, PyTorch
- **NLP**: transformers (Hugging Face)
- **Vector DB**: ChromaDB or Pinecone (for semantic search)

### Admin Panel
- **Frontend**: React + TypeScript
- **UI Framework**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts or Chart.js
- **State Management**: Zustand or Redux

### Database
- **Primary DB**: PostgreSQL 15+
- **Cache**: Redis
- **Time-series**: TimescaleDB (PostgreSQL extension)
- **Vector Storage**: pgvector (PostgreSQL extension)

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## Detailed Component Design

### 1. Discord Bot Client

#### Responsibilities
- Monitor all messages in registered servers
- Perform real-time risk assessment
- Track user engagement patterns
- Respond to admin commands
- Report alerts to community managers

#### Key Features
```python
# Core event handlers
- on_message()      # Message monitoring
- on_member_join()  # New member tracking
- on_member_remove() # Churn tracking
- on_reaction_add() # Engagement tracking
- on_voice_state_update() # Voice activity

# Admin commands
- /risk-report <user>    # Get risk assessment
- /engagement-stats      # View community health
- /configure <setting>   # Update bot settings
- /alert-threshold <level> # Set alert sensitivity
- /export-data <timeframe> # Export analytics
```

#### Risk Detection Workflow
```
Message Received
    │
    ├─> Store in Database
    │
    ├─> Extract Features:
    │   - Sentiment analysis
    │   - Keyword matching (risk terms)
    │   - Context understanding (Claude API)
    │   - User history analysis
    │   - Interaction patterns
    │
    ├─> ML Risk Scoring
    │   - Combine features
    │   - Apply trained model
    │   - Calculate risk score (0-100)
    │
    └─> Action Based on Score:
        - Low (0-30): Log only
        - Medium (31-60): Track closely
        - High (61-85): Alert moderator
        - Critical (86-100): Immediate alert
```

### 2. Backend API Platform

#### API Endpoints

**Authentication**
```
POST   /api/v1/auth/register          # Register new community
POST   /api/v1/auth/login             # Admin login
POST   /api/v1/auth/refresh           # Refresh token
```

**Bot Configuration**
```
GET    /api/v1/servers                # List registered servers
POST   /api/v1/servers                # Register new server
PATCH  /api/v1/servers/{id}/settings  # Update settings
DELETE /api/v1/servers/{id}           # Remove server
```

**Risk Management**
```
GET    /api/v1/risks/profiles         # Get current risk profiles
POST   /api/v1/risks/assess           # Manual assessment
GET    /api/v1/risks/alerts           # Get alerts
PATCH  /api/v1/risks/alerts/{id}      # Mark alert as handled
```

**Analytics**
```
GET    /api/v1/analytics/engagement   # Engagement metrics
GET    /api/v1/analytics/churn        # Churn predictions
GET    /api/v1/analytics/trends       # Trend analysis
POST   /api/v1/analytics/export       # Export data
```

**User Management**
```
GET    /api/v1/users/{id}/profile     # User profile
GET    /api/v1/users/{id}/history     # Interaction history
GET    /api/v1/users/{id}/risk        # Risk assessment
```

#### WebSocket Events
```
ws://api/events

Events:
- risk_alert          # Real-time risk alerts
- engagement_update   # Live engagement metrics
- system_status       # Bot health updates
```

### 3. AI Risk Assessment Engine

#### Risk Profile Structure
```json
{
  "version": "2024.11",
  "updated_at": "2024-11-20T00:00:00Z",
  "categories": [
    {
      "id": "political_extremism",
      "severity": "high",
      "indicators": [
        {
          "type": "keyword",
          "patterns": ["list of terms"],
          "weight": 0.8
        },
        {
          "type": "semantic",
          "description": "Dehumanizing language",
          "weight": 0.9
        },
        {
          "type": "behavioral",
          "pattern": "rapid_escalation",
          "weight": 0.7
        }
      ]
    },
    {
      "id": "hate_speech",
      "severity": "high",
      "indicators": [...]
    },
    {
      "id": "violent_rhetoric",
      "severity": "critical",
      "indicators": [...]
    }
  ]
}
```

#### Assessment Process
1. **Content Analysis** (Claude API)
   - Understand context and intent
   - Detect subtle indicators
   - Analyze conversation threads

2. **Pattern Matching**
   - Keyword detection
   - Regex patterns
   - Semantic similarity

3. **Behavioral Analysis**
   - Message frequency changes
   - Interaction pattern shifts
   - Network analysis (who they talk to)

4. **Historical Context**
   - User's past behavior
   - Progression tracking
   - Intervention effectiveness

### 4. Daily Risk Profile Updater

#### Data Sources
1. **Trusted Organizations**
   - SPLC (Southern Poverty Law Center)
   - ADL (Anti-Defamation League)
   - GNET (Global Network on Extremism)
   - Academic research databases

2. **Open Source Intelligence**
   - Trends in online radicalization
   - New terminology and coded language
   - Emerging movements

3. **Community Feedback**
   - Moderator reports
   - False positive analysis
   - New pattern identification

#### Update Process
```python
# Daily at 00:00 UTC
async def daily_risk_update():
    # 1. Fetch updates from sources
    new_data = await fetch_risk_sources()

    # 2. AI analysis of new information
    analyzed = await claude_analyze(new_data)

    # 3. Update risk profiles
    updated_profiles = merge_risk_data(current_profiles, analyzed)

    # 4. Validate with ML model
    validated = validate_profiles(updated_profiles)

    # 5. Deploy to production
    await deploy_profiles(validated)

    # 6. Notify admins of changes
    await notify_significant_changes()
```

### 5. Self-Learning ML System

#### Training Pipeline

**Data Collection**
```python
training_data = {
    "messages": Message content + context,
    "labels": {
        "moderator_action": true/false,
        "risk_level": 0-100,
        "feedback": "correct/false_positive/false_negative"
    },
    "features": {
        "sentiment": float,
        "toxicity": float,
        "user_history": dict,
        "engagement_metrics": dict
    }
}
```

**Model Architecture**
1. **Feature Extraction**
   - Text embeddings (sentence-transformers)
   - User behavior features
   - Temporal features
   - Network features

2. **Model Stack**
   - Random Forest (baseline)
   - Gradient Boosting (primary)
   - Neural Network (deep learning)
   - Ensemble combining all three

3. **Continuous Learning**
   - Weekly retraining with new data
   - A/B testing new models
   - Performance monitoring
   - Rollback capability

#### Engagement Prediction Model

**Features for Churn Prediction**
- Message frequency trend
- Response rate to others
- Time since last activity
- Sentiment trajectory
- Social network centrality
- Event participation

**Output**
- Churn probability (0-100%)
- Contributing factors
- Recommended interventions

### 6. Admin Panel

#### Dashboard Views

**Overview Dashboard**
- Active users count
- Messages analyzed (24h/7d/30d)
- Active alerts
- Risk level distribution
- System health

**Risk Management**
- Alert queue with severity
- User risk profiles
- Investigation tools
- Historical risk trends
- Action logs

**Engagement Analytics**
- Active users over time
- Message volume trends
- Churn predictions
- User retention metrics
- Community health score

**Configuration**
- Bot settings per server
- Alert thresholds
- Risk profile management
- Integration settings
- User permissions

**Reports**
- Automated weekly/monthly reports
- Custom date range analysis
- Export capabilities (CSV, JSON, PDF)
- Visualization tools

## Database Schema

### Core Tables

```sql
-- Server registrations
CREATE TABLE servers (
    id BIGSERIAL PRIMARY KEY,
    discord_server_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id BIGINT NOT NULL,
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    features_enabled JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Users (Discord users we're tracking)
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    discord_user_id VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    joined_at TIMESTAMP,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    total_messages INTEGER DEFAULT 0,
    risk_score FLOAT DEFAULT 0,
    engagement_score FLOAT DEFAULT 0,
    churn_probability FLOAT DEFAULT 0,
    flags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages (archived for analysis)
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    discord_message_id VARCHAR(20) UNIQUE NOT NULL,
    server_id BIGINT REFERENCES servers(id),
    user_id BIGINT REFERENCES users(id),
    channel_id VARCHAR(20) NOT NULL,
    content TEXT,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Risk assessments
CREATE TABLE risk_assessments (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES messages(id),
    user_id BIGINT REFERENCES users(id),
    server_id BIGINT REFERENCES servers(id),
    risk_score FLOAT NOT NULL,
    risk_category VARCHAR(100),
    indicators JSONB NOT NULL,
    ai_analysis TEXT,
    flagged BOOLEAN DEFAULT false,
    reviewed BOOLEAN DEFAULT false,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts for moderators
CREATE TABLE alerts (
    id BIGSERIAL PRIMARY KEY,
    server_id BIGINT REFERENCES servers(id),
    user_id BIGINT REFERENCES users(id),
    assessment_id BIGINT REFERENCES risk_assessments(id),
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to BIGINT,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Engagement metrics (time-series)
CREATE TABLE engagement_metrics (
    time TIMESTAMPTZ NOT NULL,
    server_id BIGINT REFERENCES servers(id),
    user_id BIGINT REFERENCES users(id),
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}'
);

-- Convert to TimescaleDB hypertable
SELECT create_hypertable('engagement_metrics', 'time');

-- Risk profiles (updated daily)
CREATE TABLE risk_profiles (
    id BIGSERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    indicators JSONB NOT NULL,
    sources JSONB NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP
);

-- ML model metadata
CREATE TABLE ml_models (
    id BIGSERIAL PRIMARY KEY,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    metrics JSONB NOT NULL,
    training_data_size INTEGER,
    active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP
);

-- Training data for ML
CREATE TABLE training_data (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES messages(id),
    features JSONB NOT NULL,
    label_risk_score FLOAT,
    label_action_taken VARCHAR(100),
    feedback VARCHAR(50),
    used_in_training BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Admin users
CREATE TABLE admin_users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'moderator',
    server_id BIGINT REFERENCES servers(id),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    admin_user_id BIGINT REFERENCES admin_users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id BIGINT,
    changes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_server_id ON messages(server_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_risk_assessments_user_id ON risk_assessments(user_id);
CREATE INDEX idx_risk_assessments_flagged ON risk_assessments(flagged) WHERE flagged = true;
CREATE INDEX idx_alerts_status ON alerts(status) WHERE status = 'open';
CREATE INDEX idx_users_risk_score ON users(risk_score DESC);
```

## Security & Privacy

### Data Protection
1. **Encryption**
   - All data encrypted at rest (AES-256)
   - TLS 1.3 for data in transit
   - Encrypted backups

2. **Data Retention**
   - Messages: 90 days (configurable)
   - Risk assessments: 1 year
   - Aggregated metrics: Indefinite
   - Right to deletion honored

3. **Access Control**
   - Role-based access (RBAC)
   - Audit logging for all actions
   - API rate limiting
   - IP whitelisting for admin panel

4. **Privacy Compliance**
   - GDPR compliant
   - Clear privacy policy
   - User data export capability
   - Anonymization options

### Ethical Guidelines
1. **Transparency**
   - Users informed of monitoring
   - Clear explanation of risk assessment
   - Appeal process for flagged content

2. **Bias Mitigation**
   - Regular bias audits of ML models
   - Diverse training data
   - Human oversight required for actions

3. **Responsible AI**
   - Explainable AI decisions
   - Human-in-the-loop for critical alerts
   - Regular accuracy reviews

## Deployment Architecture

### Development
```yaml
# docker-compose.yml (development)
services:
  bot:
    build: ./discord-bot
    environment:
      - ENV=development
    volumes:
      - ./discord-bot:/app

  api:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  admin-panel:
    build: ./admin-panel
    ports:
      - "3000:3000"
```

### Production
```yaml
# Kubernetes deployment structure
- Namespace: extremism-monitor

  Deployments:
    - discord-bot (replicas: 3)
    - api-server (replicas: 5)
    - ml-engine (replicas: 2)
    - daily-updater (cronjob)
    - admin-panel (replicas: 2)

  Services:
    - api-service (LoadBalancer)
    - admin-service (LoadBalancer)

  StatefulSets:
    - postgres-cluster (3 replicas)
    - redis-cluster (3 replicas)

  Storage:
    - PersistentVolumes for database
    - Object storage for backups
```

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up project structure
- [ ] Initialize Discord bot framework
- [ ] Create basic backend API
- [ ] Set up PostgreSQL database
- [ ] Implement authentication
- [ ] Basic message logging

### Phase 2: Core Risk Assessment (Weeks 3-4)
- [ ] Integrate Claude API
- [ ] Implement basic risk detection
- [ ] Create risk profile structure
- [ ] Build alert system
- [ ] Add moderator commands

### Phase 3: Admin Panel (Weeks 5-6)
- [ ] Build React admin interface
- [ ] Implement dashboard views
- [ ] Create configuration management
- [ ] Add alert management UI
- [ ] Implement reporting tools

### Phase 4: ML & Self-Learning (Weeks 7-9)
- [ ] Build feature extraction pipeline
- [ ] Train initial ML models
- [ ] Implement continuous learning
- [ ] Create engagement prediction model
- [ ] Build A/B testing framework

### Phase 5: Daily Updater (Week 10)
- [ ] Implement risk source fetching
- [ ] Create AI analysis pipeline
- [ ] Build profile update mechanism
- [ ] Add change notification system

### Phase 6: Advanced Features (Weeks 11-12)
- [ ] Implement churn prediction
- [ ] Add community health metrics
- [ ] Build intervention recommendations
- [ ] Create export capabilities

### Phase 7: Testing & Optimization (Weeks 13-14)
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation completion

### Phase 8: Deployment (Week 15-16)
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] Backup systems
- [ ] Disaster recovery plan
- [ ] User onboarding materials

## Monitoring & Maintenance

### Key Metrics
1. **System Health**
   - Bot uptime
   - API response times
   - Database performance
   - Error rates

2. **ML Performance**
   - Model accuracy
   - False positive rate
   - False negative rate
   - Prediction confidence

3. **Business Metrics**
   - Communities served
   - Messages analyzed
   - Alerts generated
   - Moderator actions

### Alerting
- PagerDuty for critical issues
- Slack notifications for warnings
- Email digests for daily reports

## Cost Estimation

### Monthly Costs (Assuming 100 communities, ~100k users)

| Component | Estimated Cost |
|-----------|----------------|
| Claude API calls | $500-1000 |
| Cloud hosting (AWS/GCP) | $300-500 |
| PostgreSQL hosting | $200 |
| Redis hosting | $50 |
| CDN | $50 |
| Monitoring tools | $100 |
| **Total** | **~$1,200-1,900/month** |

### Scaling Costs
- Per 100 additional communities: +$500/month
- Per 1M additional messages: +$200/month

## Next Steps

1. **Immediate Actions**
   - Choose between Python or Node.js for bot
   - Set up development environment
   - Create initial project structure
   - Configure CI/CD pipeline

2. **Team Requirements**
   - Backend developer (Python/FastAPI)
   - Frontend developer (React)
   - ML engineer
   - DevOps engineer
   - Security consultant

3. **Approvals Needed**
   - Privacy policy review
   - Legal compliance check
   - Budget approval
   - Data retention policy

---

**Document Version**: 1.0
**Last Updated**: 2024-11-20
**Owner**: Development Team
**Status**: Draft - Pending Review
