const Sentiment = require('sentiment');
const sentiment = new Sentiment();

// Keywords and patterns associated with different risk categories
const RISK_PATTERNS = {
    violence: [
        'kill', 'murder', 'attack', 'destroy', 'bomb', 'weapon', 'gun', 'shoot',
        'stab', 'assault', 'hurt', 'harm', 'fight', 'war', 'blood', 'death'
    ],
    hate: [
        'hate', 'racist', 'nazi', 'supremacist', 'genocide', 'ethnic cleansing',
        'inferior', 'subhuman', 'vermin', 'scum', 'trash'
    ],
    radicalization: [
        'jihad', 'crusade', 'holy war', 'martyr', 'extremist', 'radical',
        'revolution', 'uprising', 'overthrow', 'manifesto', 'propaganda'
    ],
    threats: [
        'threat', 'threaten', 'going to', 'will kill', 'watch out', 'pay for',
        'revenge', 'retaliate', 'get you', 'coming for'
    ],
    toxicity: [
        'kys', 'suicide', 'die', 'worthless', 'pathetic', 'loser', 'idiot',
        'stupid', 'dumb', 'trash', 'garbage', '废物'
    ]
};

/**
 * Analyze a message for risk indicators
 * @param {string} content - The message content to analyze
 * @returns {Object} Analysis result with risk score and flags
 */
function analyzeMessage(content) {
    if (!content || typeof content !== 'string') {
        return {
            riskScore: 0,
            sentiment: 0,
            flags: [],
            categories: {}
        };
    }

    const lowerContent = content.toLowerCase();
    const flags = [];
    const categories = {};
    let totalRisk = 0;

    // Analyze sentiment
    const sentimentResult = sentiment.analyze(content);
    const sentimentScore = sentimentResult.score;
    
    // Convert sentiment to risk (negative sentiment increases risk)
    const sentimentRisk = sentimentScore < 0 ? Math.min(Math.abs(sentimentScore) / 20, 0.3) : 0;
    totalRisk += sentimentRisk;

    // Check for risk patterns
    for (const [category, keywords] of Object.entries(RISK_PATTERNS)) {
        let matchCount = 0;
        const matchedWords = [];

        for (const keyword of keywords) {
            if (lowerContent.includes(keyword)) {
                matchCount++;
                matchedWords.push(keyword);
            }
        }

        if (matchCount > 0) {
            categories[category] = {
                count: matchCount,
                words: matchedWords
            };
            flags.push(category);
            
            // Each category match increases risk
            totalRisk += Math.min(matchCount * 0.15, 0.5);
        }
    }

    // Check for excessive caps (shouting)
    const capsRatio = (content.match(/[A-Z]/g) || []).length / content.length;
    if (capsRatio > 0.5 && content.length > 10) {
        flags.push('excessive_caps');
        totalRisk += 0.1;
    }

    // Check for repeated characters (spam-like behavior)
    if (/(.)\1{4,}/.test(content)) {
        flags.push('spam_pattern');
        totalRisk += 0.05;
    }

    // Normalize risk score to 0-1 range
    const riskScore = Math.min(totalRisk, 1);

    return {
        riskScore,
        sentiment: sentimentScore,
        flags: [...new Set(flags)], // Remove duplicates
        categories,
        analyzedAt: new Date().toISOString()
    };
}

/**
 * Update a user's risk profile based on new analysis
 * @param {Object} userProfile - Current user profile
 * @param {Object} analysis - Latest message analysis
 * @returns {Object} Updated user profile
 */
function updateRiskProfile(userProfile, analysis) {
    // Initialize profile if it doesn't exist
    if (!userProfile) {
        userProfile = {
            messageCount: 0,
            totalRiskScore: 0,
            averageRiskScore: 0,
            highRiskCount: 0,
            flagHistory: {},
            lastAnalyzed: null,
            trendingUp: false
        };
    }

    // Update message count
    userProfile.messageCount += 1;

    // Calculate weighted average (recent messages have more weight)
    const decayFactor = 0.95; // Previous messages decay slightly
    userProfile.totalRiskScore = 
        (userProfile.totalRiskScore * decayFactor) + analysis.riskScore;
    
    userProfile.averageRiskScore = 
        userProfile.totalRiskScore / (userProfile.messageCount * decayFactor + 1);

    // Track high-risk messages
    if (analysis.riskScore >= parseFloat(process.env.RISK_THRESHOLD_HIGH || 0.8)) {
        userProfile.highRiskCount += 1;
    }

    // Update flag history
    for (const flag of analysis.flags) {
        if (!userProfile.flagHistory[flag]) {
            userProfile.flagHistory[flag] = 0;
        }
        userProfile.flagHistory[flag] += 1;
    }

    // Determine if risk is trending up
    if (userProfile.messageCount > 5) {
        const recentRisk = analysis.riskScore;
        const historicalAverage = userProfile.averageRiskScore;
        userProfile.trendingUp = recentRisk > historicalAverage * 1.2;
    }

    userProfile.lastAnalyzed = new Date().toISOString();

    return userProfile;
}

/**
 * Get risk level description
 * @param {number} riskScore - Risk score (0-1)
 * @returns {string} Risk level description
 */
function getRiskLevel(riskScore) {
    const low = parseFloat(process.env.RISK_THRESHOLD_LOW || 0.3);
    const medium = parseFloat(process.env.RISK_THRESHOLD_MEDIUM || 0.6);
    const high = parseFloat(process.env.RISK_THRESHOLD_HIGH || 0.8);

    if (riskScore < low) return 'Low';
    if (riskScore < medium) return 'Medium';
    if (riskScore < high) return 'High';
    return 'Critical';
}

module.exports = {
    analyzeMessage,
    updateRiskProfile,
    getRiskLevel,
    RISK_PATTERNS
};
