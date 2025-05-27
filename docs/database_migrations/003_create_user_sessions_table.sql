-- Migration: 003_create_user_sessions_table.sql  
-- Description: Create user_sessions table for JWT token management and blacklisting
-- Created: 2025-01-28

BEGIN;

-- Create user_sessions table for token blacklisting and session management
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID for blacklisting
    token_type VARCHAR(20) DEFAULT 'access' NOT NULL CHECK (token_type IN ('access', 'refresh')),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    user_agent TEXT,
    ip_address INET,
    device_info JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT fk_user_sessions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_jti_length CHECK (length(token_jti) >= 10),
    CONSTRAINT valid_expires_at CHECK (expires_at > created_at),
    CONSTRAINT valid_revoked_at CHECK (revoked_at IS NULL OR revoked_at >= created_at),
    CONSTRAINT valid_device_info CHECK (jsonb_typeof(device_info) = 'object')
);

-- Create indexes for performance
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_user_sessions_token_type ON user_sessions(token_type);
CREATE INDEX idx_user_sessions_ip_address ON user_sessions(ip_address) WHERE ip_address IS NOT NULL;

-- Create partial index for active sessions that haven't expired
CREATE INDEX idx_user_sessions_active_unexpired ON user_sessions(user_id, token_jti) 
    WHERE is_active = TRUE AND expires_at > NOW();

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete sessions that expired more than 7 days ago
    DELETE FROM user_sessions 
    WHERE expires_at < NOW() - INTERVAL '7 days'
    AND (revoked_at IS NOT NULL OR is_active = FALSE);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Update expired but not revoked sessions
    UPDATE user_sessions 
    SET is_active = FALSE, revoked_at = NOW()
    WHERE expires_at < NOW() 
    AND is_active = TRUE 
    AND revoked_at IS NULL;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to revoke all user sessions (useful for security incidents)
CREATE OR REPLACE FUNCTION revoke_all_user_sessions(target_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    revoked_count INTEGER;
BEGIN
    UPDATE user_sessions 
    SET is_active = FALSE, revoked_at = NOW()
    WHERE user_id = target_user_id 
    AND is_active = TRUE 
    AND revoked_at IS NULL;
    
    GET DIAGNOSTICS revoked_count = ROW_COUNT;
    RETURN revoked_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to check if token is blacklisted
CREATE OR REPLACE FUNCTION is_token_blacklisted(jti VARCHAR(255))
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_sessions 
        WHERE token_jti = jti 
        AND (is_active = FALSE OR revoked_at IS NOT NULL OR expires_at < NOW())
    );
END;
$$ LANGUAGE plpgsql;

COMMIT; 