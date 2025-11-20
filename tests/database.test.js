const fs = require('fs');
const path = require('path');
const database = require('../src/database');

// Use a test database
process.env.DATABASE_PATH = path.join(__dirname, 'test.db');

describe('Database', () => {
    beforeAll(() => {
        // Initialize database before tests
        database.initialize();
    });

    afterAll(() => {
        // Clean up database after tests
        database.close();
        const dbPath = process.env.DATABASE_PATH;
        if (fs.existsSync(dbPath)) {
            fs.unlinkSync(dbPath);
        }
        // Clean up WAL files
        const walPath = dbPath + '-wal';
        const shmPath = dbPath + '-shm';
        if (fs.existsSync(walPath)) fs.unlinkSync(walPath);
        if (fs.existsSync(shmPath)) fs.unlinkSync(shmPath);
    });

    describe('User Profiles', () => {
        test('should create a new user profile', () => {
            const userId = 'test-user-1';
            const profile = database.createUserProfile(userId);
            
            expect(profile.userId).toBe(userId);
            expect(profile.messageCount).toBe(0);
            expect(profile.totalRiskScore).toBe(0);
            expect(profile.averageRiskScore).toBe(0);
            expect(profile.highRiskCount).toBe(0);
        });

        test('should get existing user profile', () => {
            const userId = 'test-user-2';
            database.createUserProfile(userId);
            
            const profile = database.getUserProfile(userId);
            expect(profile).toBeTruthy();
            expect(profile.userId).toBe(userId);
        });

        test('should create profile if user does not exist', () => {
            const userId = 'test-user-3';
            const profile = database.getUserProfile(userId);
            
            expect(profile).toBeTruthy();
            expect(profile.userId).toBe(userId);
            expect(profile.messageCount).toBe(0);
        });

        test('should update user profile', () => {
            const userId = 'test-user-4';
            const profile = database.getUserProfile(userId);
            
            profile.messageCount = 10;
            profile.totalRiskScore = 5.0;
            profile.averageRiskScore = 0.5;
            profile.highRiskCount = 2;
            
            database.updateUserProfile(userId, profile);
            
            const updated = database.getUserProfile(userId);
            expect(updated.messageCount).toBe(10);
            expect(updated.totalRiskScore).toBe(5.0);
            expect(updated.highRiskCount).toBe(2);
        });

        test('should preserve flag history', () => {
            const userId = 'test-user-5';
            const profile = database.getUserProfile(userId);
            
            profile.flagHistory = { violence: 3, hate: 1 };
            database.updateUserProfile(userId, profile);
            
            const updated = database.getUserProfile(userId);
            expect(updated.flagHistory.violence).toBe(3);
            expect(updated.flagHistory.hate).toBe(1);
        });
    });

    describe('Message Logs', () => {
        test('should log a message', () => {
            const messageId = 'msg-1';
            const userId = 'test-user-6';
            const content = 'Test message content';
            const riskScore = 0.5;
            const flags = ['violence', 'hate'];
            
            // Create user profile first
            database.createUserProfile(userId);
            database.logMessage(messageId, userId, content, riskScore, flags);
            
            const messages = database.getUserMessages(userId, 10);
            expect(messages.length).toBeGreaterThan(0);
        });

        test('should get user messages', () => {
            const userId = 'test-user-7';
            
            // Create user profile first
            database.createUserProfile(userId);
            database.logMessage('msg-2', userId, 'Message 1', 0.3, []);
            database.logMessage('msg-3', userId, 'Message 2', 0.5, ['violence']);
            
            const messages = database.getUserMessages(userId, 10);
            expect(messages.length).toBe(2);
        });

        test('should limit number of messages returned', () => {
            const userId = 'test-user-8';
            
            // Create user profile first
            database.createUserProfile(userId);
            for (let i = 0; i < 10; i++) {
                database.logMessage(`msg-${i}`, userId, `Message ${i}`, 0.5, []);
            }
            
            const messages = database.getUserMessages(userId, 5);
            expect(messages.length).toBe(5);
        });

        test('should get high risk messages', () => {
            const userId = 'test-user-9';
            
            // Create user profile first
            database.createUserProfile(userId);
            database.logMessage('msg-low', userId, 'Low risk', 0.2, []);
            database.logMessage('msg-high', userId, 'High risk', 0.85, ['violence']);
            
            const highRiskMessages = database.getHighRiskMessages(10);
            const hasHighRisk = highRiskMessages.some(m => m.message_id === 'msg-high');
            expect(hasHighRisk).toBe(true);
        });
    });

    describe('Alerts', () => {
        test('should create an alert', () => {
            const messageId = 'msg-alert-1';
            const userId = 'test-user-10';
            const alertType = 'high_risk';
            const riskScore = 0.9;
            const details = { flags: ['violence', 'threats'] };
            
            // Create user profile first
            database.createUserProfile(userId);
            database.createAlert(messageId, userId, alertType, riskScore, details);
            
            const alerts = database.getUnacknowledgedAlerts(10);
            expect(alerts.length).toBeGreaterThan(0);
        });

        test('should get unacknowledged alerts', () => {
            const messageId = 'msg-alert-2';
            const userId = 'test-user-11';
            
            // Create user profile first
            database.createUserProfile(userId);
            database.createAlert(messageId, userId, 'high_risk', 0.9, {});
            
            const alerts = database.getUnacknowledgedAlerts(10);
            const hasAlert = alerts.some(a => a.message_id === messageId);
            expect(hasAlert).toBe(true);
        });

        test('should acknowledge alert', () => {
            const messageId = 'msg-alert-3';
            const userId = 'test-user-12';
            
            // Create user profile first
            database.createUserProfile(userId);
            database.createAlert(messageId, userId, 'high_risk', 0.9, {});
            
            const alertsBefore = database.getUnacknowledgedAlerts(100);
            const alert = alertsBefore.find(a => a.message_id === messageId);
            
            if (alert) {
                database.acknowledgeAlert(alert.id);
                
                const alertsAfter = database.getUnacknowledgedAlerts(100);
                const stillUnacknowledged = alertsAfter.find(a => a.id === alert.id);
                expect(stillUnacknowledged).toBeUndefined();
            }
        });
    });

    describe('Statistics', () => {
        test('should get database statistics', () => {
            const stats = database.getStats();
            
            expect(stats).toHaveProperty('totalUsers');
            expect(stats).toHaveProperty('totalMessages');
            expect(stats).toHaveProperty('totalAlerts');
            expect(stats).toHaveProperty('unacknowledgedAlerts');
            
            expect(typeof stats.totalUsers).toBe('number');
            expect(typeof stats.totalMessages).toBe('number');
        });

        test('should have users tracked', () => {
            const stats = database.getStats();
            expect(stats.totalUsers).toBeGreaterThan(0);
        });
    });

    describe('High Risk Users', () => {
        test('should get high risk users', () => {
            const userId = 'test-user-high-risk';
            const profile = database.getUserProfile(userId);
            
            profile.averageRiskScore = 0.9;
            profile.highRiskCount = 5;
            database.updateUserProfile(userId, profile);
            
            const highRiskUsers = database.getHighRiskUsers(10);
            expect(Array.isArray(highRiskUsers)).toBe(true);
        });

        test('should limit number of users returned', () => {
            const users = database.getHighRiskUsers(5);
            expect(users.length).toBeLessThanOrEqual(5);
        });
    });
});
