CREATE TABLE IF NOT EXISTS users (
    id              SERIAL          PRIMARY KEY, 
    username        VARCHAR(50)     NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,      
    balance         DECIMAL(15, 2)  NOT NULL DEFAULT 0.00,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
  
    CONSTRAINT uq_username UNIQUE (username),
    CONSTRAINT uq_email    UNIQUE (email)
);
 
CREATE TABLE IF NOT EXISTS balance_transactions (
    id               SERIAL          PRIMARY KEY,
    transaction_name VARCHAR(50)     NOT NULL,
    user_id          INTEGER         NOT NULL,
    amount           DECIMAL(15, 2)  NOT NULL,  
    balance_after    DECIMAL(15, 2)  NOT NULL,   

    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
 
CREATE INDEX idx_transactions_user_id   ON balance_transactions (user_id);
-- CREATE INDEX idx_sessions_user_id       ON sessions             (user_id);
-- CREATE INDEX idx_sessions_expires_at    ON sessions             (expires_at);
-- CREATE INDEX idx_transactions_created   ON balance_transactions (created_at);
 
 
INSERT INTO users 
    (username, email, password_hash, balance) 
VALUES
    ('alice',   'alice@example.com', '<hashed_password>',  1500.00),
    ('bob',     'bob@example.com',   '<hashed_password>',  250.75),
    ('charlie', 'charlie@example.com','<hashed_password>', 0.00);
 
INSERT INTO balance_transactions
    (transaction_name, user_id, amount, balance_after)
VALUES
    ('AMZN',1,50,500),
    ('TSLA',1,150,200),
    ('QRTY',2,75,750),
    ('ZZZZ',3,10,100);