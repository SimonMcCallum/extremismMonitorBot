# System Architecture

## Overview

The Extremism Monitor Bot is a Node.js application that combines Discord bot functionality with AI-powered risk analysis and a web-based admin panel.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Discord Server                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ User 1   │  │ User 2   │  │ User 3   │  │ User N   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │               │
│       └─────────────┴─────────────┴─────────────┘               │
│                      Messages                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                   Discord Bot Client                           │
│                    (discord.js v14)                            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Event Handlers                                           │ │
│  │  • MessageCreate → Analyze content                        │ │
│  │  • GuildMemberAdd → Track new users                       │ │
│  │  • ClientReady → Initialize systems                       │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI Risk Analyzer                            │
│                  (src/ai/riskAnalyzer.js)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Analysis Pipeline:                                       │  │
│  │  1. Sentiment Analysis (sentiment npm package)            │  │
│  │  2. Pattern Matching (5 risk categories, 80+ keywords)    │  │
│  │  3. Behavioral Analysis (caps, spam detection)            │  │
│  │  4. Risk Score Calculation (0-1 scale)                    │  │
│  │  5. Flag Generation (violence, hate, threats, etc.)       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database Layer                              │
│                    (src/database.js)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (better-sqlite3)                         │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌──────────┐ │  │
│  │  │ user_profiles   │  │  message_logs   │  │  alerts  │ │  │
│  │  │ • user_id (PK)  │  │  • id (PK)      │  │ • id (PK)│ │  │
│  │  │ • msg_count     │  │  • message_id   │  │ • msg_id │ │  │
│  │  │ • risk_scores   │  │  • user_id (FK) │  │ • user_id│ │  │
│  │  │ • flag_history  │  │  • content      │  │ • type   │ │  │
│  │  │ • trending      │  │  • risk_score   │  │ • ack    │ │  │
│  │  └─────────────────┘  └─────────────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├─────────────────┐
                         │                 │
                         ▼                 ▼
┌─────────────────────────────────┐  ┌────────────────────────────┐
│       Alert System              │  │     Admin Panel Server      │
│  ┌───────────────────────────┐ │  │   (src/admin/server.js)     │
│  │  Discord Channel Alerts   │ │  │  ┌──────────────────────┐   │
│  │  • Rich embeds            │ │  │  │  Express.js Server   │   │
│  │  • User info              │ │  │  │  • Rate limiting     │   │
│  │  • Risk scores            │ │  │  │  • Authentication    │   │
│  │  • Message preview        │ │  │  │  • REST API          │   │
│  │  • Jump links             │ │  │  └──────────────────────┘   │
│  └───────────────────────────┘ │  │           │                 │
└─────────────────────────────────┘  │           ▼                 │
                                     │  ┌──────────────────────┐   │
                                     │  │  API Endpoints       │   │
                                     │  │  GET /api/stats      │   │
                                     │  │  GET /api/users/...  │   │
                                     │  │  GET /api/messages...│   │
                                     │  │  GET /api/alerts     │   │
                                     │  │  POST /api/alerts/...│   │
                                     │  └──────────────────────┘   │
                                     └────────────┬─────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Web Dashboard (Admin UI)                     │
│                 (src/admin/views/dashboard.html)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Browser Interface                                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │  │
│  │  │ Statistics │  │ High-Risk  │  │  Recent    │          │  │
│  │  │ Dashboard  │  │   Users    │  │  Messages  │          │  │
│  │  └────────────┘  └────────────┘  └────────────┘          │  │
│  │  • Real-time data                                         │  │
│  │  • Auto-refresh (30s)                                     │  │
│  │  • Responsive design                                      │  │
│  │  • Color-coded alerts                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Message Analysis Flow
```
User sends message
    │
    ▼
Discord API
    │
    ▼
Bot receives MessageCreate event
    │
    ▼
AI Analyzer processes message
    │
    ├─► Calculate sentiment score
    ├─► Match risk patterns
    ├─► Detect behavioral indicators
    └─► Generate risk score & flags
    │
    ▼
Database layer
    │
    ├─► Create/update user profile
    └─► Log message analysis
    │
    ▼
Risk evaluation
    │
    ├─► If score >= high threshold
    │   └─► Send alert to Discord channel
    └─► If score < high threshold
        └─► Store silently
```

### 2. Admin Panel Data Flow
```
Community Manager opens dashboard
    │
    ▼
Browser sends HTTP request with auth
    │
    ▼
Rate limiter validates request
    │
    ▼
Express server authenticates
    │
    ▼
API endpoint handler
    │
    ├─► Query database
    └─► Format response
    │
    ▼
JSON response to browser
    │
    ▼
JavaScript updates dashboard UI
    │
    └─► Auto-refresh after 30 seconds
```

## Component Details

### Discord Bot (`src/index.js`)
- **Purpose**: Main entry point, Discord integration
- **Dependencies**: discord.js, database, AI analyzer, admin panel
- **Key Features**:
  - Event-driven architecture
  - Graceful shutdown handling
  - Error logging
  - Message monitoring

### AI Risk Analyzer (`src/ai/riskAnalyzer.js`)
- **Purpose**: Analyze content for risk indicators
- **Dependencies**: sentiment (npm package)
- **Algorithms**:
  - Sentiment analysis
  - Pattern matching
  - Weighted risk scoring
  - Trend detection
- **Output**: Risk score (0-1), flags, categories

### Database Module (`src/database.js`)
- **Purpose**: Data persistence and retrieval
- **Technology**: SQLite with better-sqlite3
- **Features**:
  - WAL mode for concurrency
  - Foreign key constraints
  - Indexed queries
  - CRUD operations
- **Tables**: user_profiles, message_logs, alerts

### Admin Panel (`src/admin/server.js`)
- **Purpose**: Web interface for monitoring
- **Technology**: Express.js
- **Security**:
  - Rate limiting (100 req/15min)
  - Basic authentication
  - Input validation
- **API**: RESTful endpoints for data access

### Logger (`src/utils/logger.js`)
- **Purpose**: Centralized logging
- **Features**:
  - File-based logging
  - Console output
  - Log levels (info, warn, error, debug)
  - Daily log rotation

## Scalability Considerations

### Current Design
- Single-threaded Node.js application
- SQLite for lightweight, embedded database
- Suitable for small to medium Discord servers (< 10,000 users)

### Scaling Options
1. **Horizontal Scaling**:
   - Multiple bot instances with shared database
   - Load balancing across instances

2. **Database Scaling**:
   - Migrate from SQLite to PostgreSQL/MySQL
   - Add read replicas for analytics
   - Implement caching layer (Redis)

3. **Processing Scaling**:
   - Queue-based message processing (RabbitMQ, Redis Queue)
   - Separate worker processes for AI analysis
   - Microservices architecture

## Security Architecture

### Defense Layers
1. **Input Layer**:
   - Rate limiting on admin panel
   - Input validation on all endpoints
   - Authentication on sensitive routes

2. **Processing Layer**:
   - No eval() or dangerous code execution
   - Parameterized database queries
   - Error handling prevents information leakage

3. **Storage Layer**:
   - Foreign key constraints
   - Data validation before storage
   - No sensitive data in logs

4. **Output Layer**:
   - Sanitized responses
   - CORS headers (when needed)
   - Secure Discord API usage

## Performance Characteristics

### Benchmarks (Approximate)
- Message analysis: < 10ms per message
- Database write: < 5ms per operation
- Database read: < 2ms per query
- Admin panel load: < 100ms
- Memory usage: ~50-100MB idle, ~150-200MB under load

### Optimization Techniques
- Database indexes on frequently queried fields
- Connection pooling (SQLite prepared statements)
- Minimal DOM manipulation in dashboard
- Efficient pattern matching algorithms

## Monitoring and Observability

### Logging
- Application logs in `logs/` directory
- Daily log rotation
- Structured logging with timestamps

### Metrics (Available via Admin Panel)
- Total users tracked
- Messages analyzed
- Alerts generated
- High-risk users count
- Bot uptime

### Health Checks
- Bot status (online/offline)
- Guild count
- Database connectivity
- Admin panel responsiveness

## Development Workflow

```
1. Code changes
   │
   ▼
2. ESLint validation
   │
   ▼
3. Jest unit tests
   │
   ▼
4. CodeQL security scan
   │
   ▼
5. Manual testing
   │
   ▼
6. Commit and push
   │
   ▼
7. Deploy
```

## Technology Stack

### Runtime
- Node.js 18+
- JavaScript (ES2021)

### Core Dependencies
- discord.js (Discord API)
- express (Web server)
- better-sqlite3 (Database)
- sentiment (AI analysis)
- express-rate-limit (Security)
- dotenv (Configuration)

### Development Tools
- Jest (Testing)
- ESLint (Code quality)
- nodemon (Development)

## Configuration Management

### Environment Variables
All configuration via `.env` file:
- Discord credentials
- Admin panel settings
- Risk thresholds
- Feature flags
- Database path

### Benefits
- No hardcoded secrets
- Easy deployment configuration
- Environment-specific settings
- Security best practices
