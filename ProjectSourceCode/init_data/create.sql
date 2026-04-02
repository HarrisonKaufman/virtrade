CREATE TABLE IF NOT EXISTS users (
    id              SERIAL          PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,      
    balance         DECIMAL(15, 2)  NOT NULL DEFAULT 0.00,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS balance_transactions (
    id              SERIAL          PRIMARY KEY,
    user_id         INTEGER         NOT NULL REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    amount          DECIMAL(15, 2)  NOT NULL,  
    balance_after   DECIMAL(15, 2)  NOT NULL,
    transaction_type VARCHAR(50)    NOT NULL,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON balance_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created ON balance_transactions(created_at);

INSERT INTO users (username, email, password_hash, balance) VALUES
    ('alice',   'alice@example.com', '$2a$10$hash1', 1500.00),
    ('bob',     'bob@example.com',   '$2a$10$hash2',  250.75),
    ('charlie', 'charlie@example.com','$2a$10$hash3',    0.00)
ON CONFLICT (username) DO NOTHING;
 