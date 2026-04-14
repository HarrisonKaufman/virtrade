CREATE TABLE IF NOT EXISTS users (
    id              SERIAL          NOT NULL,
    username        VARCHAR(50)     NOT NULL,
    email           VARCHAR(255)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    balance         DECIMAL(15, 2)  NOT NULL DEFAULT 0.00,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,

    PRIMARY KEY (id),
    UNIQUE (username),
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS balance_transactions (
    id               SERIAL          NOT NULL,
    user_id          INT             NOT NULL,
    amount           DECIMAL(15, 2)  NOT NULL,
    balance_after    DECIMAL(15, 2)  NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON balance_transactions (user_id);

CREATE TABLE IF NOT EXISTS holdings (
    id          SERIAL          NOT NULL,
    user_id     INT             NOT NULL,
    ticker      VARCHAR(20)     NOT NULL,
    quantity    DECIMAL(15, 4)  NOT NULL DEFAULT 0,

    PRIMARY KEY (id),
    UNIQUE (user_id, ticker),
    CONSTRAINT fk_holdings_user FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_holdings_user_id ON holdings (user_id);
