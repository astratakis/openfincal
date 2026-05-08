BEGIN;

-- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id          UUID PRIMARY KEY,
    first_name  TEXT        NOT NULL,
    last_name   TEXT        NOT NULL,
    email       TEXT        NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE buckets (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT        NOT NULL,
    tickers     TEXT[]      NOT NULL DEFAULT '{}',
    ical_url    TEXT        NOT NULL UNIQUE
                  DEFAULT ('/calendars/' || gen_random_uuid()::text || '.ics'),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX buckets_user_id_idx ON buckets(user_id);

COMMIT;
