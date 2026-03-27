CREATE TABLE IF NOT EXISTS hosting_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES hosting_providers(id) ON DELETE CASCADE,
    domain_name VARCHAR(180) NOT NULL,
    domain_url TEXT,
    expiration_date TIMESTAMPTZ,
    last_payment_date TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hosting_mailboxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES hosting_providers(id) ON DELETE CASCADE,
    email_address VARCHAR(180) NOT NULL,
    encrypted_password BYTEA,
    owner_name VARCHAR(150),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_hosting_domains_provider
    ON hosting_domains (provider_id, domain_name);

CREATE INDEX IF NOT EXISTS ix_hosting_mailboxes_provider
    ON hosting_mailboxes (provider_id, email_address);

DROP TRIGGER IF EXISTS trg_hosting_domains_updated_at ON hosting_domains;
CREATE TRIGGER trg_hosting_domains_updated_at
BEFORE UPDATE ON hosting_domains
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_hosting_mailboxes_updated_at ON hosting_mailboxes;
CREATE TRIGGER trg_hosting_mailboxes_updated_at
BEFORE UPDATE ON hosting_mailboxes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
