# Extremism Monitor Bot

A Discord bot with AI capabilities to analyze and monitor game communities, assessing the risk of escalation to radicalization and extremism. The bot features real-time message monitoring, risk profiling, and a web-based admin panel for community managers.

## Features

### 🤖 Discord Bot
- **Real-time Message Monitoring**: Automatically analyzes all messages in monitored servers
- **AI Risk Analysis**: Uses sentiment analysis and pattern matching to assess risk levels
- **User Risk Profiles**: Tracks individual users over time with cumulative risk scoring
- **Automated Alerts**: Sends alerts to designated channels when high-risk content is detected
- **Member Tracking**: Monitors new members joining the community

### 🧠 AI Risk Assessment
- **Sentiment Analysis**: Evaluates message tone and negativity
- **Pattern Detection**: Identifies keywords and phrases related to:
  - Violence
  - Hate speech
  - Radicalization
  - Threats
  - Toxic behavior
- **Risk Scoring**: Calculates risk scores on a scale of 0-1
- **Trend Detection**: Identifies users with escalating risk patterns

### 📊 Admin Panel
- **Web Dashboard**: Beautiful, responsive web interface for community managers
- **Real-time Statistics**: View total users, messages analyzed, and alerts
- **High-Risk Users List**: See users ranked by risk score
- **Message History**: Review recent high-risk messages
- **Auto-refresh**: Dashboard updates automatically every 30 seconds

### 💾 Data Persistence
- **SQLite Database**: Stores all user profiles, messages, and alerts
- **Message Logging**: Complete audit trail of analyzed content
- **Alert Management**: Track acknowledged and pending alerts

## Installation

### Prerequisites
- Node.js 18.0.0 or higher
- npm (Node Package Manager)
- Discord Bot Token (see Setup section)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/SimonMcCallum/extremismMonitorBot.git
cd extremismMonitorBot
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_GUILD_ID=your_discord_guild_id_here

# Admin Panel Configuration
ADMIN_PANEL_PORT=3000
ADMIN_PANEL_USERNAME=admin
ADMIN_PANEL_PASSWORD=change_this_password

# AI Risk Assessment Configuration
RISK_THRESHOLD_LOW=0.3
RISK_THRESHOLD_MEDIUM=0.6
RISK_THRESHOLD_HIGH=0.8

# Database Configuration
DATABASE_PATH=./data/monitor.db

# Monitoring Configuration
MESSAGE_SCAN_ENABLED=true
USER_TRACKING_ENABLED=true
ALERT_CHANNEL_ID=your_alert_channel_id_here
```

4. **Create a Discord Bot**

Go to [Discord Developer Portal](https://discord.com/developers/applications):
- Click "New Application" and give it a name
- Go to "Bot" section and click "Add Bot"
- Copy the bot token and add it to your `.env` file
- Enable these Privileged Gateway Intents:
  - Server Members Intent
  - Message Content Intent
- Go to "OAuth2" > "URL Generator"
- Select scopes: `bot`
- Select permissions: `Read Messages/View Channels`, `Send Messages`, `Read Message History`
- Use the generated URL to invite the bot to your server

5. **Run the bot**
```bash
npm start
```

For development with auto-restart:
```bash
npm run dev
```

## Usage

### Admin Panel

1. Open your browser and go to `http://localhost:3000` (or your configured port)
2. Login with the credentials from your `.env` file
3. View the dashboard with:
   - Real-time statistics
   - High-risk users list
   - Recent high-risk messages
   - Bot status and uptime

### Alert System

When high-risk content is detected:
1. The bot analyzes the message and calculates a risk score
2. If the score exceeds the high threshold (default 0.8), an alert is sent
3. Alerts are posted to the configured alert channel with:
   - User information
   - Risk scores
   - Detected flags (violence, hate, threats, etc.)
   - Message preview
   - Direct link to the message

### Risk Levels

- **Low Risk (0.0 - 0.3)**: Normal conversation, minimal concerns
- **Medium Risk (0.3 - 0.6)**: Elevated language, minor concerns
- **High Risk (0.6 - 0.8)**: Concerning content, requires monitoring
- **Critical Risk (0.8 - 1.0)**: Immediate attention required, automatic alerts

## Project Structure

```
extremismMonitorBot/
├── src/
│   ├── index.js              # Main bot entry point
│   ├── database.js           # Database operations
│   ├── ai/
│   │   └── riskAnalyzer.js   # AI risk analysis engine
│   ├── admin/
│   │   ├── server.js         # Admin panel web server
│   │   └── views/
│   │       └── dashboard.html # Admin dashboard UI
│   └── utils/
│       └── logger.js         # Logging utility
├── data/                     # Database storage (created automatically)
├── logs/                     # Log files (created automatically)
├── .env                      # Environment configuration
├── .env.example              # Example configuration
├── package.json              # Node.js dependencies
└── README.md                 # This file
```

## Development

### Running Tests
```bash
npm test
```

### Linting
```bash
npm run lint
```

### Adding New Risk Patterns

Edit `src/ai/riskAnalyzer.js` and add keywords to the `RISK_PATTERNS` object:

```javascript
const RISK_PATTERNS = {
    violence: ['keyword1', 'keyword2', ...],
    hate: ['keyword1', 'keyword2', ...],
    // Add more categories as needed
};
```

## Security Considerations

⚠️ **Important**: This bot processes potentially sensitive content. Please ensure:

1. **Secure the Admin Panel**: Use strong passwords
2. **Protect Your Token**: Never commit `.env` files or expose your Discord token
3. **Limit Bot Permissions**: Only grant necessary Discord permissions
4. **Review Data Storage**: Regularly audit stored messages and user data
5. **Privacy Compliance**: Ensure compliance with GDPR and other privacy regulations
6. **False Positives**: The AI may flag benign content; always have human review

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the GitHub Issues page.

## Disclaimer

This bot is designed to assist community managers in identifying potentially problematic content. It should not be the sole tool for moderation decisions. Always apply human judgment and context when taking action based on the bot's assessments.
