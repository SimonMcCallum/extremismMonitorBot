require('dotenv').config();
const { Client, GatewayIntentBits, Events } = require('discord.js');
const database = require('./database');
const aiAgent = require('./ai/riskAnalyzer');
const adminPanel = require('./admin/server');
const logger = require('./utils/logger');

// Initialize Discord client with necessary intents
const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
});

// Initialize database
database.initialize();

// Bot ready event
client.once(Events.ClientReady, (c) => {
    logger.info(`Bot is ready! Logged in as ${c.user.tag}`);
    console.log(`Bot is ready! Logged in as ${c.user.tag}`);
});

// Message monitoring
client.on(Events.MessageCreate, async (message) => {
    // Ignore bot messages
    if (message.author.bot) return;

    // Skip if message scanning is disabled
    if (process.env.MESSAGE_SCAN_ENABLED !== 'true') return;

    try {
        // Analyze message content
        const analysis = aiAgent.analyzeMessage(message.content);
        
        // Get or create user risk profile
        const userProfile = database.getUserProfile(message.author.id);
        
        // Update risk profile
        const updatedProfile = aiAgent.updateRiskProfile(userProfile, analysis);
        database.updateUserProfile(message.author.id, updatedProfile);

        // Log the analysis
        database.logMessage(
            message.id,
            message.author.id,
            message.content,
            analysis.riskScore,
            analysis.flags
        );

        // Alert if risk is high
        if (analysis.riskScore >= parseFloat(process.env.RISK_THRESHOLD_HIGH || 0.8)) {
            await sendAlert(message, analysis, updatedProfile);
        }

        logger.debug(`Analyzed message from ${message.author.tag}: risk=${analysis.riskScore}`);
    } catch (error) {
        logger.error('Error analyzing message:', error);
    }
});

// Function to send alert to community managers
async function sendAlert(message, analysis, userProfile) {
    const alertChannelId = process.env.ALERT_CHANNEL_ID;
    if (!alertChannelId) return;

    try {
        const alertChannel = await client.channels.fetch(alertChannelId);
        if (alertChannel) {
            const embed = {
                color: 0xff0000,
                title: '⚠️ High Risk Content Detected',
                fields: [
                    {
                        name: 'User',
                        value: `<@${message.author.id}> (${message.author.tag})`,
                        inline: true
                    },
                    {
                        name: 'Risk Score',
                        value: `${(analysis.riskScore * 100).toFixed(1)}%`,
                        inline: true
                    },
                    {
                        name: 'User Total Risk',
                        value: `${(userProfile.totalRiskScore * 100).toFixed(1)}%`,
                        inline: true
                    },
                    {
                        name: 'Channel',
                        value: `<#${message.channel.id}>`,
                        inline: true
                    },
                    {
                        name: 'Flags',
                        value: analysis.flags.join(', ') || 'None',
                        inline: false
                    },
                    {
                        name: 'Message Preview',
                        value: message.content.substring(0, 200) + (message.content.length > 200 ? '...' : ''),
                        inline: false
                    },
                    {
                        name: 'Link',
                        value: `[Jump to Message](${message.url})`,
                        inline: false
                    }
                ],
                timestamp: new Date().toISOString(),
                footer: {
                    text: 'Extremism Monitor Bot'
                }
            };

            await alertChannel.send({ embeds: [embed] });
            logger.info(`Alert sent for message ${message.id}`);
        }
    } catch (error) {
        logger.error('Error sending alert:', error);
    }
}

// Member join event
client.on(Events.GuildMemberAdd, (member) => {
    if (process.env.USER_TRACKING_ENABLED === 'true') {
        database.createUserProfile(member.id);
        logger.info(`New member tracked: ${member.user.tag}`);
    }
});

// Error handling
client.on(Events.Error, (error) => {
    logger.error('Discord client error:', error);
});

// Start the admin panel
adminPanel.start(client, database);

// Login to Discord
client.login(process.env.DISCORD_TOKEN)
    .then(() => {
        logger.info('Bot successfully connected to Discord');
    })
    .catch((error) => {
        logger.error('Failed to connect to Discord:', error);
        process.exit(1);
    });

// Graceful shutdown
process.on('SIGINT', () => {
    logger.info('Shutting down bot...');
    client.destroy();
    database.close();
    process.exit(0);
});
