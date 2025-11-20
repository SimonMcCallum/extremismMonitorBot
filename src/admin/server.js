const express = require('express');
const rateLimit = require('express-rate-limit');
const path = require('path');
const logger = require('../utils/logger');

let app = null;
let server = null;
let discordClient = null;
let database = null;

/**
 * Start the admin panel web server
 * @param {Object} client - Discord client instance
 * @param {Object} db - Database instance
 */
function start(client, db) {
    discordClient = client;
    database = db;

    app = express();
    const port = process.env.ADMIN_PANEL_PORT || 3000;

    // Rate limiting to prevent abuse
    const limiter = rateLimit({
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 100, // Limit each IP to 100 requests per windowMs
        message: 'Too many requests from this IP, please try again later.'
    });

    // Middleware
    app.use(limiter);
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));
    app.use(express.static(path.join(__dirname, 'public')));

    // Simple authentication middleware
    app.use((req, res, next) => {
        // Skip auth for static files and login page
        if (req.path.startsWith('/public') || req.path === '/login' || req.path === '/api/login') {
            return next();
        }

        const auth = req.headers.authorization;
        if (auth) {
            const credentials = Buffer.from(auth.split(' ')[1], 'base64').toString().split(':');
            const username = credentials[0];
            const password = credentials[1];

            if (username === process.env.ADMIN_PANEL_USERNAME && 
                password === process.env.ADMIN_PANEL_PASSWORD) {
                return next();
            }
        }

        res.setHeader('WWW-Authenticate', 'Basic realm="Admin Panel"');
        res.status(401).send('Authentication required');
    });

    // Routes
    app.get('/', (req, res) => {
        res.sendFile(path.join(__dirname, 'views', 'dashboard.html'));
    });

    // API: Get dashboard statistics
    app.get('/api/stats', (req, res) => {
        try {
            const stats = database.getStats();
            const botStatus = {
                status: discordClient.isReady() ? 'online' : 'offline',
                guilds: discordClient.guilds.cache.size,
                uptime: process.uptime()
            };

            res.json({
                ...stats,
                bot: botStatus
            });
        } catch (error) {
            logger.error('Error getting stats:', error);
            res.status(500).json({ error: 'Failed to get statistics' });
        }
    });

    // API: Get high-risk users
    app.get('/api/users/high-risk', (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const users = database.getHighRiskUsers(limit);
            res.json(users);
        } catch (error) {
            logger.error('Error getting high-risk users:', error);
            res.status(500).json({ error: 'Failed to get high-risk users' });
        }
    });

    // API: Get user profile
    app.get('/api/users/:userId', (req, res) => {
        try {
            const profile = database.getUserProfile(req.params.userId);
            if (!profile) {
                return res.status(404).json({ error: 'User not found' });
            }
            res.json(profile);
        } catch (error) {
            logger.error('Error getting user profile:', error);
            res.status(500).json({ error: 'Failed to get user profile' });
        }
    });

    // API: Get user messages
    app.get('/api/users/:userId/messages', (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 100;
            const messages = database.getUserMessages(req.params.userId, limit);
            res.json(messages);
        } catch (error) {
            logger.error('Error getting user messages:', error);
            res.status(500).json({ error: 'Failed to get user messages' });
        }
    });

    // API: Get high-risk messages
    app.get('/api/messages/high-risk', (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const messages = database.getHighRiskMessages(limit);
            res.json(messages);
        } catch (error) {
            logger.error('Error getting high-risk messages:', error);
            res.status(500).json({ error: 'Failed to get high-risk messages' });
        }
    });

    // API: Get unacknowledged alerts
    app.get('/api/alerts', (req, res) => {
        try {
            const limit = parseInt(req.query.limit) || 50;
            const alerts = database.getUnacknowledgedAlerts(limit);
            res.json(alerts);
        } catch (error) {
            logger.error('Error getting alerts:', error);
            res.status(500).json({ error: 'Failed to get alerts' });
        }
    });

    // API: Acknowledge alert
    app.post('/api/alerts/:alertId/acknowledge', (req, res) => {
        try {
            database.acknowledgeAlert(parseInt(req.params.alertId));
            res.json({ success: true });
        } catch (error) {
            logger.error('Error acknowledging alert:', error);
            res.status(500).json({ error: 'Failed to acknowledge alert' });
        }
    });

    // Start server
    server = app.listen(port, () => {
        logger.info(`Admin panel started on http://localhost:${port}`);
        console.log(`Admin panel started on http://localhost:${port}`);
    });
}

/**
 * Stop the admin panel server
 */
function stop() {
    if (server) {
        server.close(() => {
            logger.info('Admin panel stopped');
        });
    }
}

module.exports = {
    start,
    stop
};
