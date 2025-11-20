# Extremism Monitor Bot - Setup Guide

This guide will walk you through setting up the Extremism Monitor Bot from scratch.

## Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"**
3. Give your application a name (e.g., "Extremism Monitor Bot")
4. Click **"Create"**

## Step 2: Configure the Bot

1. In the left sidebar, click **"Bot"**
2. Click **"Add Bot"** and confirm
3. Under the bot username, click **"Reset Token"** and copy the token
4. Save this token securely - you'll need it for your `.env` file

### Enable Required Intents

Scroll down to **"Privileged Gateway Intents"** and enable:
- ✅ **Server Members Intent**
- ✅ **Message Content Intent**

Click **"Save Changes"**

## Step 3: Get Your Application IDs

1. Go to the **"General Information"** tab
2. Copy your **"Application ID"** (this is your CLIENT_ID)
3. Go to your Discord server, right-click the server icon and click **"Copy ID"** (this is your GUILD_ID)
   - If you don't see this option, enable Developer Mode in Discord settings under Advanced

## Step 4: Invite the Bot to Your Server

1. Go to the **"OAuth2"** > **"URL Generator"** tab
2. Select the following scopes:
   - ✅ `bot`
3. Select the following bot permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Embed Links
4. Copy the generated URL and open it in your browser
5. Select your server and click **"Authorize"**

## Step 5: Create Alert Channel

1. In your Discord server, create a new text channel (e.g., `#security-alerts`)
2. Right-click the channel name and click **"Copy ID"**
3. Save this as your ALERT_CHANNEL_ID

## Step 6: Configure the Bot

1. Clone the repository:
```bash
git clone https://github.com/SimonMcCallum/extremismMonitorBot.git
cd extremismMonitorBot
```

2. Install dependencies:
```bash
npm install
```

3. Copy the example environment file:
```bash
cp .env.example .env
```

4. Edit `.env` with your values:
```env
DISCORD_TOKEN=your_bot_token_from_step_2
DISCORD_CLIENT_ID=your_application_id_from_step_3
DISCORD_GUILD_ID=your_server_id_from_step_3
ALERT_CHANNEL_ID=your_alert_channel_id_from_step_5

ADMIN_PANEL_PORT=3000
ADMIN_PANEL_USERNAME=admin
ADMIN_PANEL_PASSWORD=YourSecurePassword123!

RISK_THRESHOLD_LOW=0.3
RISK_THRESHOLD_MEDIUM=0.6
RISK_THRESHOLD_HIGH=0.8

DATABASE_PATH=./data/monitor.db

MESSAGE_SCAN_ENABLED=true
USER_TRACKING_ENABLED=true
```

## Step 7: Run the Bot

Start the bot:
```bash
npm start
```

You should see:
```
Bot is ready! Logged in as YourBotName#1234
Admin panel started on http://localhost:3000
Database initialized successfully
```

## Step 8: Access the Admin Panel

1. Open your browser and go to `http://localhost:3000`
2. Login with the username and password from your `.env` file
3. You should see the dashboard with statistics and monitoring panels

## Step 9: Test the Bot

1. In your Discord server, send a test message with concerning content
2. Check the admin panel to see if it was analyzed
3. If the message exceeds the high threshold, an alert should appear in your alert channel

## Troubleshooting

### Bot is not responding
- Check that the bot is online in your server member list
- Verify your DISCORD_TOKEN is correct
- Ensure Privileged Gateway Intents are enabled

### Messages not being analyzed
- Verify MESSAGE_SCAN_ENABLED=true in .env
- Check that the bot has "Read Message History" permission
- Ensure Message Content Intent is enabled in the Developer Portal

### Admin panel won't load
- Check that the port (default 3000) is not in use
- Verify ADMIN_PANEL_PORT in .env
- Check the console for any error messages

### Database errors
- Ensure the data directory exists or can be created
- Check file permissions for the database path

## Production Deployment

For production use:

1. **Use a process manager** like PM2:
```bash
npm install -g pm2
pm2 start src/index.js --name extremism-bot
pm2 save
pm2 startup
```

2. **Use environment variables** instead of .env file

3. **Set up HTTPS** for the admin panel using a reverse proxy (nginx/Apache)

4. **Configure firewall rules** to restrict admin panel access

5. **Set up automated backups** of the database

6. **Enable logging rotation** to manage log file sizes

7. **Monitor the bot** with health checks and alerting

## Updating Risk Thresholds

You can adjust the sensitivity by modifying these values in `.env`:

- **RISK_THRESHOLD_LOW**: Default 0.3 (30%)
- **RISK_THRESHOLD_MEDIUM**: Default 0.6 (60%)
- **RISK_THRESHOLD_HIGH**: Default 0.8 (80%)

Lower values = more sensitive (more alerts)
Higher values = less sensitive (fewer alerts)

Restart the bot after making changes.

## Next Steps

- Customize risk patterns in `src/ai/riskAnalyzer.js`
- Set up regular database backups
- Configure additional monitoring channels
- Train your moderation team on the admin panel
- Review and refine alert thresholds based on your community

## Support

For issues and questions, please open an issue on GitHub.