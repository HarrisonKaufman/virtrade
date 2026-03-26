-- Hypothetical Data Tables for virtrade, will likely need to be edited

CREATE TABLE IF NOT EXISTS users (
    username    VARCHAR(50)     PRIMARY KEY     NOT NULL,
    password    VARCHAR(50)     NOT NULL

);

CREATE TABLE IF NOT EXISTS stats (
    stats_id        PRIMARY KEY     SERIAL,
    profit          INTEGER     NOT NULL,
    portfolio_value INTEGER     NOT NULL,

);

CREATE TABLE IF NOT EXISTS trades (
    trade_id    PRIMARY KEY     SERIAL,
    name        VARCHAR(30)     NOT NULL,
    profit      INTEGER         NOT NULL
);

CREATE TABLE IF NOT EXISTS users_to_stats (
    username    VARCHAR(50)     NOT NULL,
    stats_id    INTEGER         NOT NULL,
    CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES users(username),
    CONSTRAINT fk_stats_id FOREIGN KEY (stats_id) REFERENCES stats(stats_id)

);

CREATE TABLE IF NOT EXISTS users_to_trades (
    username    VARCHAR(50)     NOT NULL,
    trade_id    INTEGER     NOT NULL,
    CONSTRAINT fk_username FOREIGN KEY (username) REFERENCES  users(username),
    CONSTRAINT fk_trade_id FOREIGN KEY (trade_id) REFERENCES trades(trade_id)

);