CREATE DATABASE IF NOT EXISTS user_accounts;

 
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL          PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,      
    balance         DECIMAL(15, 2)  NOT NULL DEFAULT 0.00,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE
);
 
CREATE TABLE IF NOT EXISTS balance_transactions (
    id               SERIAL          PRIMARY KEY,
    user_id          INT             NOT NULL REFERENCES users (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    amount           DECIMAL(15, 2)  NOT NULL,  
    balance_after    DECIMAL(15, 2)  NOT NULL
);
 

 
CREATE INDEX idx_sessions_user_id       ON sessions             (user_id);
CREATE INDEX idx_sessions_expires_at    ON sessions             (expires_at);
CREATE INDEX idx_transactions_user_id   ON balance_transactions (user_id);
CREATE INDEX idx_transactions_created   ON balance_transactions (created_at);
 
 
INSERT INTO users (username, email, password_hash, salt, balance) VALUES
    ('alice',   'alice@example.com', '<hashed_password>', '<salt>', 1500.00),
    ('bob',     'bob@example.com',   '<hashed_password>', '<salt>',  250.75),
    ('charlie', 'charlie@example.com','<hashed_password>','<salt>',    0.00);
 