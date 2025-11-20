const { analyzeMessage, updateRiskProfile, getRiskLevel, RISK_PATTERNS } = require('../src/ai/riskAnalyzer');

describe('Risk Analyzer', () => {
    describe('analyzeMessage', () => {
        test('should return zero risk for empty message', () => {
            const result = analyzeMessage('');
            expect(result.riskScore).toBe(0);
            expect(result.flags).toEqual([]);
        });

        test('should return zero risk for benign message', () => {
            const result = analyzeMessage('Hello, how are you today?');
            expect(result.riskScore).toBeLessThan(0.3);
            expect(result.flags.length).toBe(0);
        });

        test('should detect violence keywords', () => {
            const result = analyzeMessage('I want to kill and destroy everything');
            expect(result.riskScore).toBeGreaterThan(0);
            expect(result.flags).toContain('violence');
            expect(result.categories).toHaveProperty('violence');
        });

        test('should detect hate speech keywords', () => {
            const result = analyzeMessage('I hate those people, they are subhuman');
            expect(result.riskScore).toBeGreaterThan(0);
            expect(result.flags).toContain('hate');
        });

        test('should detect threats', () => {
            const result = analyzeMessage('Watch out, I am coming for you');
            expect(result.riskScore).toBeGreaterThan(0);
            expect(result.flags).toContain('threats');
        });

        test('should detect excessive caps', () => {
            const result = analyzeMessage('THIS IS ALL CAPS MESSAGE');
            expect(result.flags).toContain('excessive_caps');
        });

        test('should detect spam patterns', () => {
            const result = analyzeMessage('hellooooooo');
            expect(result.flags).toContain('spam_pattern');
        });

        test('should have all required properties', () => {
            const result = analyzeMessage('test message');
            expect(result).toHaveProperty('riskScore');
            expect(result).toHaveProperty('sentiment');
            expect(result).toHaveProperty('flags');
            expect(result).toHaveProperty('categories');
            expect(result).toHaveProperty('analyzedAt');
        });

        test('should normalize risk score to max 1.0', () => {
            const result = analyzeMessage('kill destroy hate attack bomb weapon gun shoot murder');
            expect(result.riskScore).toBeLessThanOrEqual(1.0);
        });

        test('should calculate negative sentiment risk', () => {
            const result = analyzeMessage('I hate everything terrible awful bad horrible');
            expect(result.sentiment).toBeLessThan(0);
            expect(result.riskScore).toBeGreaterThan(0);
        });
    });

    describe('updateRiskProfile', () => {
        test('should create new profile if none exists', () => {
            const analysis = { riskScore: 0.5, flags: ['violence'] };
            const profile = updateRiskProfile(null, analysis);
            
            expect(profile).toHaveProperty('messageCount', 1);
            expect(profile).toHaveProperty('totalRiskScore');
            expect(profile).toHaveProperty('averageRiskScore');
            expect(profile).toHaveProperty('highRiskCount');
            expect(profile).toHaveProperty('flagHistory');
            expect(profile).toHaveProperty('trendingUp');
        });

        test('should increment message count', () => {
            const existingProfile = {
                messageCount: 5,
                totalRiskScore: 2.5,
                averageRiskScore: 0.5,
                highRiskCount: 0,
                flagHistory: {},
                trendingUp: false
            };
            const analysis = { riskScore: 0.5, flags: [] };
            const updated = updateRiskProfile(existingProfile, analysis);
            
            expect(updated.messageCount).toBe(6);
        });

        test('should track high risk messages', () => {
            const existingProfile = {
                messageCount: 5,
                totalRiskScore: 2.5,
                averageRiskScore: 0.5,
                highRiskCount: 1,
                flagHistory: {},
                trendingUp: false
            };
            const analysis = { riskScore: 0.85, flags: ['violence'] };
            const updated = updateRiskProfile(existingProfile, analysis);
            
            expect(updated.highRiskCount).toBe(2);
        });

        test('should update flag history', () => {
            const existingProfile = {
                messageCount: 5,
                totalRiskScore: 2.5,
                averageRiskScore: 0.5,
                highRiskCount: 0,
                flagHistory: { violence: 2 },
                trendingUp: false
            };
            const analysis = { riskScore: 0.5, flags: ['violence', 'hate'] };
            const updated = updateRiskProfile(existingProfile, analysis);
            
            expect(updated.flagHistory.violence).toBe(3);
            expect(updated.flagHistory.hate).toBe(1);
        });

        test('should detect trending up risk', () => {
            const existingProfile = {
                messageCount: 10,
                totalRiskScore: 3.0,
                averageRiskScore: 0.3,
                highRiskCount: 0,
                flagHistory: {},
                trendingUp: false
            };
            const analysis = { riskScore: 0.8, flags: ['violence'] };
            const updated = updateRiskProfile(existingProfile, analysis);
            
            expect(updated.trendingUp).toBe(true);
        });

        test('should have lastAnalyzed timestamp', () => {
            const analysis = { riskScore: 0.5, flags: [] };
            const profile = updateRiskProfile(null, analysis);
            
            expect(profile.lastAnalyzed).toBeTruthy();
            expect(new Date(profile.lastAnalyzed).getTime()).toBeLessThanOrEqual(Date.now());
        });
    });

    describe('getRiskLevel', () => {
        test('should return Low for score below low threshold', () => {
            expect(getRiskLevel(0.1)).toBe('Low');
            expect(getRiskLevel(0.29)).toBe('Low');
        });

        test('should return Medium for score between low and medium threshold', () => {
            expect(getRiskLevel(0.3)).toBe('Medium');
            expect(getRiskLevel(0.5)).toBe('Medium');
        });

        test('should return High for score between medium and high threshold', () => {
            expect(getRiskLevel(0.6)).toBe('High');
            expect(getRiskLevel(0.75)).toBe('High');
        });

        test('should return Critical for score above high threshold', () => {
            expect(getRiskLevel(0.8)).toBe('Critical');
            expect(getRiskLevel(0.95)).toBe('Critical');
            expect(getRiskLevel(1.0)).toBe('Critical');
        });
    });

    describe('RISK_PATTERNS', () => {
        test('should have all expected categories', () => {
            expect(RISK_PATTERNS).toHaveProperty('violence');
            expect(RISK_PATTERNS).toHaveProperty('hate');
            expect(RISK_PATTERNS).toHaveProperty('radicalization');
            expect(RISK_PATTERNS).toHaveProperty('threats');
            expect(RISK_PATTERNS).toHaveProperty('toxicity');
        });

        test('should have arrays of keywords', () => {
            expect(Array.isArray(RISK_PATTERNS.violence)).toBe(true);
            expect(RISK_PATTERNS.violence.length).toBeGreaterThan(0);
        });
    });
});
