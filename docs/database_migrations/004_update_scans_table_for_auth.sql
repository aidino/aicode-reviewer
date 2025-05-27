-- Migration: 004_update_scans_table_for_auth.sql
-- Description: Update scans table to integrate with user authentication system
-- Created: 2025-01-28

BEGIN;

-- Add user_id column to scans table (assuming it exists from scan_models.py)
-- Note: This assumes scans table exists. If not, we'll need to create it first.

-- Check if scans table exists, if not create a basic version
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scans') THEN
        -- Create basic scans table if it doesn't exist
        CREATE TABLE scans (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255) UNIQUE NOT NULL,
            repository VARCHAR(500) NOT NULL,
            scan_type VARCHAR(20) NOT NULL CHECK (scan_type IN ('pr', 'project')),
            status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'error', 'cancelled')),
            pr_id INTEGER,
            branch VARCHAR(255),
            target_branch VARCHAR(255),
            source_branch VARCHAR(255),
            total_findings INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT
        );
        
        -- Create indexes for basic scans table
        CREATE INDEX idx_scans_scan_id ON scans(scan_id);
        CREATE INDEX idx_scans_repository ON scans(repository);
        CREATE INDEX idx_scans_status ON scans(status);
        CREATE INDEX idx_scans_created_at ON scans(created_at);
    END IF;
END
$$;

-- Add user_id column to scans table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scans' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE scans ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END
$$;

-- Add is_public column to allow public/private scans
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scans' AND column_name = 'is_public'
    ) THEN
        ALTER TABLE scans ADD COLUMN is_public BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;
END
$$;

-- Add visibility column for more granular control
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scans' AND column_name = 'visibility'
    ) THEN
        ALTER TABLE scans ADD COLUMN visibility VARCHAR(20) DEFAULT 'private' NOT NULL 
        CHECK (visibility IN ('private', 'public', 'organization', 'unlisted'));
    END IF;
END
$$;

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_is_public ON scans(is_public) WHERE is_public = TRUE;
CREATE INDEX IF NOT EXISTS idx_scans_visibility ON scans(visibility);
CREATE INDEX IF NOT EXISTS idx_scans_user_created ON scans(user_id, created_at);

-- Update existing scans to belong to admin user (user_id = 1)
UPDATE scans SET user_id = 1, visibility = 'public' WHERE user_id IS NULL;

-- Create scan_permissions table for shared access control
CREATE TABLE IF NOT EXISTS scan_permissions (
    id SERIAL PRIMARY KEY,
    scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    permission_type VARCHAR(20) DEFAULT 'view' NOT NULL CHECK (permission_type IN ('view', 'edit', 'admin')),
    granted_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    UNIQUE(scan_id, user_id),
    CONSTRAINT valid_expires_at CHECK (expires_at IS NULL OR expires_at > granted_at)
);

-- Create indexes for scan_permissions
CREATE INDEX idx_scan_permissions_scan_id ON scan_permissions(scan_id);
CREATE INDEX idx_scan_permissions_user_id ON scan_permissions(user_id);
CREATE INDEX idx_scan_permissions_type ON scan_permissions(permission_type);
CREATE INDEX idx_scan_permissions_expires ON scan_permissions(expires_at) WHERE expires_at IS NOT NULL;

-- Create function to check scan access for a user
CREATE OR REPLACE FUNCTION user_can_access_scan(
    target_user_id INTEGER, 
    target_scan_id INTEGER,
    required_permission VARCHAR(20) DEFAULT 'view'
)
RETURNS BOOLEAN AS $$
DECLARE
    scan_owner INTEGER;
    scan_visibility VARCHAR(20);
    user_role VARCHAR(20);
BEGIN
    -- Get scan info
    SELECT s.user_id, s.visibility INTO scan_owner, scan_visibility
    FROM scans s WHERE s.id = target_scan_id;
    
    -- Get user role
    SELECT u.role INTO user_role FROM users u WHERE u.id = target_user_id;
    
    -- Admin can access everything
    IF user_role = 'admin' THEN
        RETURN TRUE;
    END IF;
    
    -- Owner can access their own scans
    IF scan_owner = target_user_id THEN
        RETURN TRUE;
    END IF;
    
    -- Public scans can be viewed by anyone
    IF scan_visibility = 'public' AND required_permission = 'view' THEN
        RETURN TRUE;
    END IF;
    
    -- Check explicit permissions
    RETURN EXISTS (
        SELECT 1 FROM scan_permissions sp
        WHERE sp.scan_id = target_scan_id 
        AND sp.user_id = target_user_id
        AND (sp.expires_at IS NULL OR sp.expires_at > NOW())
        AND (
            (required_permission = 'view' AND sp.permission_type IN ('view', 'edit', 'admin')) OR
            (required_permission = 'edit' AND sp.permission_type IN ('edit', 'admin')) OR
            (required_permission = 'admin' AND sp.permission_type = 'admin')
        )
    );
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on scans table if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scans' AND column_name = 'updated_at'
    ) THEN
        DROP TRIGGER IF EXISTS trigger_scans_updated_at ON scans;
        CREATE TRIGGER trigger_scans_updated_at
            BEFORE UPDATE ON scans
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

-- Create view for user accessible scans
CREATE OR REPLACE VIEW user_accessible_scans AS
SELECT 
    s.*,
    u.username as owner_username,
    CASE 
        WHEN s.user_id = u.id THEN 'owner'
        WHEN u.role = 'admin' THEN 'admin'
        WHEN sp.permission_type IS NOT NULL THEN sp.permission_type
        WHEN s.visibility = 'public' THEN 'view'
        ELSE NULL
    END as user_permission
FROM scans s
LEFT JOIN users u ON s.user_id = u.id
LEFT JOIN scan_permissions sp ON s.id = sp.scan_id
WHERE s.visibility = 'public' 
   OR s.user_id = CURRENT_USER_ID() 
   OR sp.user_id = CURRENT_USER_ID()
   OR EXISTS (SELECT 1 FROM users WHERE id = CURRENT_USER_ID() AND role = 'admin');

COMMIT; 