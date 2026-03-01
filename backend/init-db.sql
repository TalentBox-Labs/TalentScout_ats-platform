-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUID generation
CREATE EXTENSION IF NOT EXISTS vector;        -- For vector embeddings (AI matching)

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ats_platform TO ats_user;

-- Create initial schema comment
COMMENT ON DATABASE ats_platform IS 'TalentScout ATS Platform - AI-First Applicant Tracking System';
