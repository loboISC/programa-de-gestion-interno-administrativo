CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE app_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(80) NOT NULL UNIQUE,
    full_name VARCHAR(150),
    email VARCHAR(150) UNIQUE,
    master_password_hash TEXT NOT NULL,
    password_hint TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    session_token_hash TEXT NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ NOT NULL,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMPTZ
);

CREATE TABLE hosting_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    provider_name VARCHAR(120) NOT NULL,
    access_url TEXT NOT NULL,
    account_username VARCHAR(150) NOT NULL,
    account_email VARCHAR(150),
    encrypted_password BYTEA,
    notes TEXT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    last_accessed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE vault_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    service_name VARCHAR(150) NOT NULL,
    login_username VARCHAR(150) NOT NULL,
    login_url TEXT,
    encrypted_password BYTEA NOT NULL,
    encrypted_notes BYTEA,
    category VARCHAR(80),
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE technical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    title VARCHAR(180) NOT NULL,
    description TEXT,
    document_type VARCHAR(20) NOT NULL,
    file_path TEXT,
    file_name VARCHAR(255),
    mime_type VARCHAR(120),
    file_size_bytes BIGINT,
    content_text TEXT,
    tags TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    last_opened_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT technical_documents_type_chk
        CHECK (document_type IN ('PDF', 'TXT', 'NOTE'))
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    title VARCHAR(160) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ,
    CONSTRAINT notifications_severity_chk
        CHECK (severity IN ('info', 'warning', 'critical'))
);

CREATE TABLE access_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES app_users(id) ON DELETE SET NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    action VARCHAR(50) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    session_timeout_minutes INTEGER NOT NULL DEFAULT 10,
    theme VARCHAR(20) NOT NULL DEFAULT 'dark',
    locale VARCHAR(20) NOT NULL DEFAULT 'es_MX',
    api_base_url TEXT,
    auto_lock_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    clipboard_clear_seconds INTEGER NOT NULL DEFAULT 30,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT user_settings_timeout_chk CHECK (session_timeout_minutes BETWEEN 1 AND 240),
    CONSTRAINT user_settings_clipboard_chk CHECK (clipboard_clear_seconds BETWEEN 5 AND 300),
    CONSTRAINT user_settings_theme_chk CHECK (theme IN ('dark', 'light'))
);

CREATE UNIQUE INDEX ux_hosting_providers_user_name
    ON hosting_providers (user_id, provider_name);

CREATE UNIQUE INDEX ux_vault_credentials_user_service_login
    ON vault_credentials (user_id, service_name, login_username);

CREATE INDEX ix_user_sessions_user_active
    ON user_sessions (user_id, is_active, expires_at);

CREATE INDEX ix_hosting_providers_user_name
    ON hosting_providers (user_id, provider_name);

CREATE INDEX ix_vault_credentials_user_service
    ON vault_credentials (user_id, service_name);

CREATE INDEX ix_technical_documents_user_title
    ON technical_documents (user_id, title);

CREATE INDEX ix_notifications_user_read
    ON notifications (user_id, is_read, created_at DESC);

CREATE INDEX ix_access_logs_user_created
    ON access_logs (user_id, created_at DESC);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_app_users_updated_at
BEFORE UPDATE ON app_users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_hosting_providers_updated_at
BEFORE UPDATE ON hosting_providers
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_vault_credentials_updated_at
BEFORE UPDATE ON vault_credentials
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_technical_documents_updated_at
BEFORE UPDATE ON technical_documents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_user_settings_updated_at
BEFORE UPDATE ON user_settings
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO app_users (
    username,
    full_name,
    email,
    master_password_hash,
    password_hint
) VALUES (
    'irvingag',
    'Irving AG',
    'irving@example.com',
    '$argon2id$v=19$m=65536,t=3,p=4$demo$reemplazar_por_hash_real',
    'Solo para entorno local'
);

INSERT INTO user_settings (
    user_id,
    session_timeout_minutes,
    theme,
    locale,
    auto_lock_enabled,
    clipboard_clear_seconds
)
SELECT id, 10, 'dark', 'es_MX', TRUE, 30
FROM app_users
WHERE username = 'irvingag';
