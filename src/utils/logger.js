const fs = require('fs');
const path = require('path');

// Create logs directory if it doesn't exist
const logsDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
}

const logFile = path.join(logsDir, `bot-${new Date().toISOString().split('T')[0]}.log`);

/**
 * Format log message
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} data - Additional data
 * @returns {string} Formatted log message
 */
function formatLog(level, message, data) {
    const timestamp = new Date().toISOString();
    let logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    if (data) {
        logMessage += ` ${JSON.stringify(data)}`;
    }
    
    return logMessage;
}

/**
 * Write log to file and console
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} data - Additional data
 */
function writeLog(level, message, data) {
    const logMessage = formatLog(level, message, data);
    
    // Write to file
    fs.appendFileSync(logFile, logMessage + '\n', 'utf8');
    
    // Also log to console based on level
    if (level === 'error') {
        console.error(logMessage);
    } else if (level === 'warn') {
        console.warn(logMessage);
    } else if (level === 'debug') {
        if (process.env.NODE_ENV === 'development') {
            console.log(logMessage);
        }
    } else {
        console.log(logMessage);
    }
}

module.exports = {
    info: (message, data) => writeLog('info', message, data),
    error: (message, data) => writeLog('error', message, data),
    warn: (message, data) => writeLog('warn', message, data),
    debug: (message, data) => writeLog('debug', message, data)
};
