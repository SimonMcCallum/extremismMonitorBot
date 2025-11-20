# Extremism Monitor Bot - Features Overview

## 🤖 Discord Bot Capabilities

### Real-Time Monitoring
- **Continuous Message Analysis**: Every message is analyzed in real-time
- **User Risk Profiling**: Tracks individual users over time
- **Automated Alerts**: High-risk content triggers immediate notifications
- **Member Tracking**: New members are automatically added to the system

### AI Analysis Engine
The bot uses multiple techniques to assess risk:
1. **Sentiment Analysis**: Evaluates tone and negativity
2. **Keyword Pattern Matching**: 80+ keywords across 5 categories
3. **Behavioral Indicators**: Caps lock, spam patterns
4. **Trend Detection**: Identifies escalating behavior patterns

### Risk Categories Monitored
- 🔴 **Violence**: Threats of physical harm, weapons, attacks
- 🔴 **Hate Speech**: Racist, discriminatory, dehumanizing language
- 🔴 **Radicalization**: Extremist ideology, calls to action
- 🔴 **Threats**: Direct or implied threats to individuals
- 🔴 **Toxicity**: Harassment, bullying, toxic behavior

## 📊 Admin Panel Dashboard

### Statistics Display
```
┌─────────────────────────────────────────────────┐
│  Extremism Monitor Bot - Admin Panel           │
│  Status: ● Online | Guilds: 3 | Uptime: 5h 23m │
└─────────────────────────────────────────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Total Users  │ │   Messages   │ │ Total Alerts │ │   Pending    │
│     247      │ │    15,823    │ │      42      │ │      8       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### High Risk Users Panel
Shows users ranked by risk score with:
- User ID and mention
- Risk level (Low/Medium/High/Critical)
- Risk percentage
- Message count and high-risk message count
- Trending indicator (⚠️ if escalating)

### Recent High Risk Messages Panel
Displays recent concerning messages with:
- Risk score and severity level
- User ID and timestamp
- Message preview (first 200 characters)
- Detected flags/categories
- Quick filters by flag type

## 🔔 Alert System

When high-risk content is detected, the bot posts to the alert channel:

```
┌────────────────────────────────────────────────┐
│ ⚠️ High Risk Content Detected                  │
├────────────────────────────────────────────────┤
│ User: @username#1234 (UserID)                  │
│ Risk Score: 87.5%                              │
│ User Total Risk: 65.2%                         │
│ Channel: #general                              │
├────────────────────────────────────────────────┤
│ Flags: violence, threats                       │
├────────────────────────────────────────────────┤
│ Message Preview:                               │
│ "I'm going to attack..."                       │
├────────────────────────────────────────────────┤
│ [Jump to Message] → Direct link                │
└────────────────────────────────────────────────┘
```

## 🎯 Risk Scoring System

### Score Ranges
- **0.0 - 0.3** (Low) - Normal conversation
- **0.3 - 0.6** (Medium) - Elevated language
- **0.6 - 0.8** (High) - Concerning content
- **0.8 - 1.0** (Critical) - Immediate attention required

### How Scores Are Calculated
1. **Base Sentiment Score**: Negative sentiment adds risk
2. **Keyword Matches**: Each category match increases risk
3. **Multiple Flags**: Cumulative risk from multiple categories
4. **Behavioral Patterns**: Caps, spam add minor risk
5. **Historical Context**: User history influences future scores

### User Profile Risk
- **Total Risk Score**: Weighted sum of all messages
- **Average Risk Score**: Mean risk across all messages
- **High Risk Count**: Number of messages above threshold
- **Trending Status**: Is risk increasing or decreasing?

## 💾 Data Storage

### Database Schema
```
user_profiles
├── user_id (PRIMARY KEY)
├── message_count
├── total_risk_score
├── average_risk_score
├── high_risk_count
├── flag_history (JSON)
└── last_analyzed

message_logs
├── id (AUTO INCREMENT)
├── message_id (UNIQUE)
├── user_id (FOREIGN KEY)
├── content
├── risk_score
├── flags (JSON)
└── created_at

alerts
├── id (AUTO INCREMENT)
├── message_id
├── user_id (FOREIGN KEY)
├── alert_type
├── risk_score
├── details (JSON)
├── acknowledged
└── created_at
```

## 🔐 Security Features

- **Rate Limiting**: 100 requests per 15 minutes per IP
- **Basic Authentication**: Username/password for admin panel
- **Environment Variables**: Sensitive data never hardcoded
- **Input Validation**: All user input is validated
- **Database Constraints**: Foreign keys and unique constraints
- **HTTPS Ready**: Deploy behind reverse proxy for encryption

## 🚀 API Endpoints

### Statistics
- `GET /api/stats` - Overall system statistics

### Users
- `GET /api/users/high-risk` - High-risk users list
- `GET /api/users/:userId` - User profile details
- `GET /api/users/:userId/messages` - User message history

### Messages
- `GET /api/messages/high-risk` - Recent high-risk messages

### Alerts
- `GET /api/alerts` - Unacknowledged alerts
- `POST /api/alerts/:alertId/acknowledge` - Mark alert as reviewed

## 📈 Use Cases

### Community Managers
- Monitor community health in real-time
- Identify problematic users early
- Track trends in community behavior
- Respond quickly to concerning content

### Moderation Teams
- Prioritize which messages need review
- Build evidence for moderation actions
- Track repeat offenders
- Generate moderation reports

### Server Administrators
- Assess overall server risk levels
- Identify patterns in problematic behavior
- Adjust server rules based on data
- Provide transparency to users about monitoring

## 🔧 Customization

### Adjustable Thresholds
- Low risk threshold (default: 0.3)
- Medium risk threshold (default: 0.6)
- High risk threshold (default: 0.8)

### Add Custom Keywords
Edit `src/ai/riskAnalyzer.js` to add keywords to existing categories or create new categories.

### Configure Monitoring
- Enable/disable message scanning
- Enable/disable user tracking
- Choose which channels to monitor
- Set alert channel preferences

## 📱 Responsive Design

The admin panel is fully responsive and works on:
- Desktop browsers (1920x1080 and up)
- Tablets (iPad, Android tablets)
- Mobile devices (phones in landscape/portrait)

## ♻️ Auto-Refresh

The dashboard automatically refreshes every 30 seconds to show:
- Updated statistics
- New high-risk users
- Recent messages
- Current alerts

No manual refresh needed!

## 🎨 User Experience

### Color-Coded Alerts
- 🟢 **Green**: Low risk
- 🟡 **Yellow**: Medium risk
- 🟠 **Orange**: High risk
- 🔴 **Red**: Critical risk

### Visual Indicators
- Status dots show bot online/offline status
- Trending arrows indicate escalating behavior
- Badges highlight important metrics
- Smooth animations provide feedback

### Easy Navigation
- Clean, modern interface
- Intuitive layout
- Quick access to all features
- Mobile-friendly design

## 🔮 Future Enhancements (Potential)

- Integration with OpenAI GPT for advanced analysis
- Image and attachment scanning
- Multi-language support
- Export reports to PDF/CSV
- Slack/Teams integration
- Machine learning model training
- Voice channel monitoring
- Webhook integrations
- Custom alerting rules
- Dashboard widgets
