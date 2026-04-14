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

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON balance_transactions (user_id);

CREATE TABLE IF NOT EXISTS holdings (
    id          SERIAL          PRIMARY KEY,
    user_id     INT             NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    ticker      VARCHAR(20)     NOT NULL,
    quantity    DECIMAL(15, 4)  NOT NULL DEFAULT 0,
    UNIQUE (user_id, ticker)
);

CREATE INDEX IF NOT EXISTS idx_holdings_user_id ON holdings (user_id);