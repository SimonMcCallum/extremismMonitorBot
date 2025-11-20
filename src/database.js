const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

let db = null;

/**
 * Initialize the database and create tables if they don't exist
 */
function initialize() {
    const dbPath = process.env.DATABASE_PATH || './data/monitor.db';
    const dbDir = path.dirname(dbPath);

    // Create data directory if it doesn't exist
    if (!fs.existsSync(dbDir)) {
        fs.mkdirSync(dbDir, { recursive: true });
    }

    db = new Database(dbPath);
    
    // Enable WAL mode for better concurrent access
    db.pragma('journal_mode = WAL');

    // Create tables
    createTables();

    console.log('Database initialized successfully');
}

/**
 * Create necessary database tables
 */
function createTables() {
    // User profiles table
    db.exec(`
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            message_count INTEGER DEFAULT 0,
            total_risk_score REAL DEFAULT 0,
            average_risk_score REAL DEFAULT 0,
            high_risk_count INTEGER DEFAULT 0,
            flag_history TEXT DEFAULT '{}',
            trending_up INTEGER DEFAULT 0,
            last_analyzed TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    `);

    // Message logs table
    db.exec(`
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            user_id TEXT,
            content TEXT,
            risk_score REAL,
            flags TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        )
    `);

    // Alerts table
    db.exec(`
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT,
            user_id TEXT,
            alert_type TEXT,
            risk_score REAL,
            details TEXT,
            acknowledged INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
        )
    `);

    // Create indexes for better query performance
    db.exec(`
        CREATE INDEX IF NOT EXISTS idx_message_logs_user_id ON message_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_message_logs_created_at ON message_logs(created_at);
        CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);
    `);
}

/**
 * Get user profile by user ID
 * @param {string} userId - Discord user ID
 * @returns {Object|null} User profile or null if not found
 */
function getUserProfile(userId) {
    const stmt = db.prepare('SELECT * FROM user_profiles WHERE user_id = ?');
    const row = stmt.get(userId);
    
    if (!row) {
        // Create new profile if doesn't exist
        return createUserProfile(userId);
    }

    return {
        userId: row.user_id,
        messageCount: row.message_count,
        totalRiskScore: row.total_risk_score,
        averageRiskScore: row.average_risk_score,
        highRiskCount: row.high_risk_count,
        flagHistory: JSON.parse(row.flag_history),
        trendingUp: row.trending_up === 1,
        lastAnalyzed: row.last_analyzed,
        createdAt: row.created_at,
        updatedAt: row.updated_at
    };
}

/**
 * Create a new user profile
 * @param {string} userId - Discord user ID
 * @returns {Object} New user profile
 */
function createUserProfile(userId) {
    const stmt = db.prepare(`
        INSERT OR IGNORE INTO user_profiles (user_id)
        VALUES (?)
    `);
    stmt.run(userId);

    return {
        userId,
        messageCount: 0,
        totalRiskScore: 0,
        averageRiskScore: 0,
        highRiskCount: 0,
        flagHistory: {},
        trendingUp: false,
        lastAnalyzed: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
    };
}

/**
 * Update user profile
 * @param {string} userId - Discord user ID
 * @param {Object} profile - Updated profile data
 */
function updateUserProfile(userId, profile) {
    const stmt = db.prepare(`
        UPDATE user_profiles
        SET message_count = ?,
            total_risk_score = ?,
            average_risk_score = ?,
            high_risk_count = ?,
            flag_history = ?,
            trending_up = ?,
            last_analyzed = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    `);

    stmt.run(
        profile.messageCount,
        profile.totalRiskScore,
        profile.averageRiskScore,
        profile.highRiskCount,
        JSON.stringify(profile.flagHistory),
        profile.trendingUp ? 1 : 0,
        profile.lastAnalyzed,
        userId
    );
}

/**
 * Log a message analysis
 * @param {string} messageId - Discord message ID
 * @param {string} userId - Discord user ID
 * @param {string} content - Message content
 * @param {number} riskScore - Risk score
 * @param {Array} flags - Risk flags
 */
function logMessage(messageId, userId, content, riskScore, flags) {
    const stmt = db.prepare(`
        INSERT OR IGNORE INTO message_logs (message_id, user_id, content, risk_score, flags)
        VALUES (?, ?, ?, ?, ?)
    `);

    stmt.run(messageId, userId, content, riskScore, JSON.stringify(flags));
}

/**
 * Get recent high-risk messages
 * @param {number} limit - Number of messages to retrieve
 * @returns {Array} Array of high-risk messages
 */
function getHighRiskMessages(limit = 50) {
    const stmt = db.prepare(`
        SELECT * FROM message_logs
        WHERE risk_score >= ?
        ORDER BY created_at DESC
        LIMIT ?
    `);

    const threshold = parseFloat(process.env.RISK_THRESHOLD_HIGH || 0.8);
    return stmt.all(threshold, limit);
}

/**
 * Get all user profiles ordered by risk
 * @param {number} limit - Number of profiles to retrieve
 * @returns {Array} Array of user profiles
 */
function getHighRiskUsers(limit = 100) {
    const stmt = db.prepare(`
        SELECT * FROM user_profiles
        ORDER BY average_risk_score DESC, high_risk_count DESC
        LIMIT ?
    `);

    return stmt.all(limit).map(row => ({
        userId: row.user_id,
        messageCount: row.message_count,
        totalRiskScore: row.total_risk_score,
        averageRiskScore: row.average_risk_score,
        highRiskCount: row.high_risk_count,
        flagHistory: JSON.parse(row.flag_history),
        trendingUp: row.trending_up === 1,
        lastAnalyzed: row.last_analyzed
    }));
}

/**
 * Get user message history
 * @param {string} userId - Discord user ID
 * @param {number} limit - Number of messages to retrieve
 * @returns {Array} Array of messages
 */
function getUserMessages(userId, limit = 100) {
    const stmt = db.prepare(`
        SELECT * FROM message_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    `);

    return stmt.all(userId, limit);
}

/**
 * Create an alert
 * @param {string} messageId - Discord message ID
 * @param {string} userId - Discord user ID
 * @param {string} alertType - Type of alert
 * @param {number} riskScore - Risk score
 * @param {Object} details - Alert details
 */
function createAlert(messageId, userId, alertType, riskScore, details) {
    const stmt = db.prepare(`
        INSERT INTO alerts (message_id, user_id, alert_type, risk_score, details)
        VALUES (?, ?, ?, ?, ?)
    `);

    stmt.run(messageId, userId, alertType, riskScore, JSON.stringify(details));
}

/**
 * Get unacknowledged alerts
 * @param {number} limit - Number of alerts to retrieve
 * @returns {Array} Array of alerts
 */
function getUnacknowledgedAlerts(limit = 50) {
    const stmt = db.prepare(`
        SELECT * FROM alerts
        WHERE acknowledged = 0
        ORDER BY created_at DESC
        LIMIT ?
    `);

    return stmt.all(limit);
}

/**
 * Acknowledge an alert
 * @param {number} alertId - Alert ID
 */
function acknowledgeAlert(alertId) {
    const stmt = db.prepare(`
        UPDATE alerts
        SET acknowledged = 1
        WHERE id = ?
    `);

    stmt.run(alertId);
}

/**
 * Get database statistics
 * @returns {Object} Database statistics
 */
function getStats() {
    const totalUsers = db.prepare('SELECT COUNT(*) as count FROM user_profiles').get().count;
    const totalMessages = db.prepare('SELECT COUNT(*) as count FROM message_logs').get().count;
    const totalAlerts = db.prepare('SELECT COUNT(*) as count FROM alerts').get().count;
    const unacknowledgedAlerts = db.prepare('SELECT COUNT(*) as count FROM alerts WHERE acknowledged = 0').get().count;

    return {
        totalUsers,
        totalMessages,
        totalAlerts,
        unacknowledgedAlerts
    };
}

/**
 * Close database connection
 */
function close() {
    if (db) {
        db.close();
        console.log('Database connection closed');
    }
}

module.exports = {
    initialize,
    getUserProfile,
    createUserProfile,
    updateUserProfile,
    logMessage,
    getHighRiskMessages,
    getHighRiskUsers,
    getUserMessages,
    createAlert,
    getUnacknowledgedAlerts,
    acknowledgeAlert,
    getStats,
    close
};
