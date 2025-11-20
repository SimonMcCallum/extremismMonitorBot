-- Database initialization script for Extremism Monitor Bot
-- This script sets up the database schema and extensions

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create servers table
CREATE TABLE IF NOT EXISTS servers (
    id BIGSERIAL PRIMARY KEY,
    discord_server_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id VARCHAR(20) NOT NULL,
    settings JSONB DEFAULT '{}',
    subscription_tier VARCHAR(50) DEFAULT 'basic',
    features_enabled JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_servers_discord_id ON servers(discord_server_id);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    discord_user_id VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(255) NOT NULL,
    joined_at TIMESTAMP,
    first_seen TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP DEFAULT NOW(),
    total_messages INTEGER DEFAULT 0,
    risk_score FLOAT DEFAULT 0,
    engagement_score FLOAT DEFAULT 0,
    churn_probability FLOAT DEFAULT 0,
    flags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_discord_id ON users(discord_user_id);
CREATE INDEX idx_users_risk_score ON users(risk_score DESC);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    discord_message_id VARCHAR(20) UNIQUE NOT NULL,
    server_id BIGINT REFERENCES servers(id),
    user_id BIGINT REFERENCES users(id),
    channel_id VARCHAR(20) NOT NULL,
    content TEXT,
    attachments JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_discord_id ON messages(discord_message_id);
CREATE INDEX idx_messages_server_id ON messages(server_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);

-- Create risk_assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES messages(id),
    user_id BIGINT REFERENCES users(id),
    server_id BIGINT REFERENCES servers(id),
    risk_score FLOAT NOT NULL,
    risk_category VARCHAR(100),
    indicators JSONB NOT NULL,
    ai_analysis TEXT,
    flagged BOOLEAN DEFAULT false,
    reviewed BOOLEAN DEFAULT false,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_risk_assessments_user_id ON risk_assessments(user_id);
CREATE INDEX idx_risk_assessments_flagged ON risk_assessments(flagged) WHERE flagged = true;
CREATE INDEX idx_risk_assessments_created_at ON risk_assessments(created_at DESC);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    server_id BIGINT REFERENCES servers(id),
    user_id BIGINT REFERENCES users(id),
    assessment_id BIGINT REFERENCES risk_assessments(id),
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    assigned_to BIGINT,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_server_id ON alerts(server_id);
CREATE INDEX idx_alerts_status ON alerts(status) WHERE status = 'open';
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for servers table
CREATE TRIGGER update_servers_updated_at
    BEFORE UPDATE ON servers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO extremism_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO extremism_user;

-- Insert sample data for testing (optional)
-- This will only run in development environments

-- Sample server
INSERT INTO servers (discord_server_id, name, owner_id)
VALUES ('123456789012345678', 'Test Server', '987654321098765432')
ON CONFLICT (discord_server_id) DO NOTHING;

COMMENT ON TABLE servers IS 'Discord servers/guilds registered with the bot';
COMMENT ON TABLE users IS 'Discord users being tracked across servers';
COMMENT ON TABLE messages IS 'Archived messages for analysis';
COMMENT ON TABLE risk_assessments IS 'AI and ML risk assessments for messages';
COMMENT ON TABLE alerts IS 'Alerts generated for moderators';
