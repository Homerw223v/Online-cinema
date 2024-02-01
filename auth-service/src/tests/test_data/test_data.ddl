CREATE SCHEMA IF NOT EXISTS tests;

CREATE TABLE IF NOT EXISTS tests.user (
    id uuid PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    surname TEXT,
    birthday DATE,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS tests.user_agent (
    id uuid PRIMARY KEY,
    fingerprint TEXT NOT NULL,
    user_id uuid NOT NULL REFERENCES tests.user (id) ON DELETE CASCADE,
    refresh_token uuid UNIQUE,
    expires_at DATE,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS tests.login_history (
    id uuid PRIMARY KEY,
    agent_id uuid NOT NULL REFERENCES tests.user_agent (id) ON DELETE CASCADE,
    time DATE NOT NULL,
    action TEXT NOT NULL,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS tests.role (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS tests.user_role (
    id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES tests.user (id) ON DELETE CASCADE,
    role_id uuid NOT NULL REFERENCES tests.role (id) ON DELETE CASCADE,
    created timestamp with time zone
);