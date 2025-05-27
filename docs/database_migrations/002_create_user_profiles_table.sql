-- Migration: 002_create_user_profiles_table.sql
-- Description: Create user_profiles table for extended user information
-- Created: 2025-01-28

BEGIN;

-- Create user_profiles table
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC' NOT NULL,
    preferences JSONB DEFAULT '{}' NOT NULL,
    github_username VARCHAR(100),
    linkedin_url VARCHAR(500),
    website_url VARCHAR(500),
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Constraints
    CONSTRAINT fk_user_profiles_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT valid_avatar_url CHECK (avatar_url IS NULL OR avatar_url ~* '^https?://.*'),
    CONSTRAINT valid_linkedin_url CHECK (linkedin_url IS NULL OR linkedin_url ~* '^https?://.*linkedin\.com/.*'),
    CONSTRAINT valid_website_url CHECK (website_url IS NULL OR website_url ~* '^https?://.*'),
    CONSTRAINT valid_github_username CHECK (github_username IS NULL OR github_username ~* '^[a-zA-Z0-9]([a-zA-Z0-9-]){0,38}$'),
    CONSTRAINT valid_bio_length CHECK (bio IS NULL OR length(bio) <= 1000),
    CONSTRAINT valid_preferences CHECK (jsonb_typeof(preferences) = 'object')
);

-- Create indexes for performance
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_profiles_github_username ON user_profiles(github_username) WHERE github_username IS NOT NULL;
CREATE INDEX idx_user_profiles_location ON user_profiles(location) WHERE location IS NOT NULL;

-- Create trigger to automatically update updated_at on user_profiles table
CREATE TRIGGER trigger_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create default profile for admin user
INSERT INTO user_profiles (user_id, full_name, bio, preferences) VALUES 
(
    1, -- admin user id
    'System Administrator',
    'Default admin user for AI Code Reviewer system',
    '{
        "theme": "dark",
        "notifications": {
            "email": true,
            "browser": true,
            "scan_completion": true,
            "security_alerts": true
        },
        "dashboard": {
            "default_view": "overview",
            "items_per_page": 20
        },
        "scan_preferences": {
            "auto_analyze": true,
            "detailed_reports": true,
            "include_diagrams": true
        }
    }'::jsonb
);

COMMIT; 