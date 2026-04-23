import os
import psycopg2
import psycopg2.extras

def get_db():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        port=5432,
        database=os.environ.get("POSTGRES_DB", "users_db"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "pwd")
    )

class Stock:
    def __init__(self, ticker, price):
        self.ticker = ticker
        self.price = price

class User:
    def __init__(self, username, password, email, balance=0.00, holdings=None, user_id=None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email = email
        self.balance = balance
        self.holdings = holdings if holdings is not None else {}

    @classmethod
    def load_from_db(cls, user_id):
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            cur.execute("SELECT ticker, quantity FROM holdings WHERE user_id = %s", (user_id,))
            holdings = {r["ticker"]: float(r["quantity"]) for r in cur.fetchall()}
            return cls(row["username"], row["password_hash"], row["email"], float(row["balance"]), holdings=holdings, user_id=row["id"])
        finally:
            conn.close()

    def buy(self, amount, stock):
        total_cost = amount * stock.price
        if self.balance < total_cost:
            return "Insufficient Balance"
        self.balance -= total_cost
        self.holdings[stock.ticker] = self.holdings.get(stock.ticker, 0) + amount
        if self.user_id:
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                            (self.user_id, -total_cost, self.balance))
                cur.execute("""
                    INSERT INTO holdings (user_id, ticker, quantity)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, ticker)
                    DO UPDATE SET quantity = holdings.quantity + EXCLUDED.quantity
                """, (self.user_id, stock.ticker, amount))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                conn.close()
        return self.balance

    def sell(self, amount, stock):
        owned = self.holdings.get(stock.ticker, 0)
        if owned < amount:
            return "Insufficient Holdings"
        self.holdings[stock.ticker] = owned - amount
        total_gain = amount * stock.price
        self.balance += total_gain
        if self.user_id:
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                            (self.user_id, total_gain, self.balance))
                cur.execute("""
                    UPDATE holdings SET quantity = quantity - %s
                    WHERE user_id = %s AND ticker = %s
                """, (amount, self.user_id, stock.ticker))
                cur.execute("""
                    DELETE FROM holdings
                    WHERE user_id = %s AND ticker = %s AND quantity <= 0
                """, (self.user_id, stock.ticker))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise
            finally:
                conn.close()
        return self.balance