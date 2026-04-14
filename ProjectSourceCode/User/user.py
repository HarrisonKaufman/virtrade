##creating User object to connect to the database and perform operations needed to track user info and balance
from fastapi import FastAPI, Form
import os, psycopg2, psycopg2.extras
app = FastAPI()
#app = FastAPI() — creates the actual web application instance

# In-memory "database" for demonstration (replace with real DB later)
users = {}
# gotta figure out how to instead of using this users array use the database

# DB connection helper — connects to the Postgres container
def get_db():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "db"),
        port=5432,
        database=os.environ.get("POSTGRES_DB", "users"),
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
        """Load a user from the database by ID, including their holdings."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Load user
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            # Load holdings from DB into dict {ticker: quantity}
            cur.execute("SELECT ticker, quantity FROM holdings WHERE user_id = %s", (user_id,))
            holdings_rows = cur.fetchall()
            holdings = {r["ticker"]: float(r["quantity"]) for r in holdings_rows}
            return cls(row["username"], row["password_hash"], row["email"], float(row["balance"]), holdings=holdings, user_id=row["id"])
        finally:
            conn.close()

    def buy(self, amount, stock):
        total_cost = amount * stock.price
        if self.balance >= total_cost:
            self.balance -= total_cost
            self.holdings[stock.ticker] = self.holdings.get(stock.ticker, 0) + amount
            # Persist to DB if this user was loaded from DB
            if self.user_id:
                conn = get_db()
                try:
                    cur = conn.cursor()
                    # Update balance
                    cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                    # Log transaction
                    cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                                (self.user_id, -total_cost, self.balance))
                    # Upsert holdings (insert or add to existing quantity)
                    cur.execute("""
                        INSERT INTO holdings (user_id, ticker, quantity)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, ticker)
                        DO UPDATE SET quantity = holdings.quantity + EXCLUDED.quantity
                    """, (self.user_id, stock.ticker, amount))
                    conn.commit()
                finally:
                    conn.close()
            return self.balance
        else:
            return "Insufficient Balance"

    def sell(self, amount, stock):
        # Check ownership — use DB holdings if loaded from DB, else in-memory dict
        owned = self.holdings.get(stock.ticker, 0)
        if owned < amount:
            return "Insufficient Holdings"
        self.holdings[stock.ticker] = owned - amount
        total_gain = amount * stock.price
        self.balance += total_gain
        # Persist to DB if this user was loaded from DB
        if self.user_id:
            conn = get_db()
            try:
                cur = conn.cursor()
                # Update balance
                cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                # Log transaction
                cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                            (self.user_id, total_gain, self.balance))
                # Reduce holdings (remove row if quantity reaches 0)
                cur.execute("""
                    UPDATE holdings SET quantity = quantity - %s
                    WHERE user_id = %s AND ticker = %s
                """, (amount, self.user_id, stock.ticker))
                cur.execute("""
                    DELETE FROM holdings
                    WHERE user_id = %s AND ticker = %s AND quantity <= 0
                """, (self.user_id, stock.ticker))
                conn.commit()
            finally:
                conn.close()
        return self.balance

#sign up route post method 
@app.post("/signup")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if username and email in users:
        return "Username or Email already exists"
    else:
        new_user= User(username, password, email)
        users[username] = new_user
        return "User created successfully"

# #deposit route
# @app.post("/deposit")
# def deposit(username: str = Form(...), amount: float = Form(...)):
#     user = users.get(username)
#     if not user:
#         return {"error": "User not found"}
#     user.deposit(amount)
#     return {"username": username, "new_balance": user.balance}

# #withdrawal route
# @app.post("/withdrawal")
# def withdrawal(username: str = Form(...), amount: float = Form(...)):
#     user = users.get(username)
#     if not user:
#         return {"error": "User not found"}
#     success = user.withdrawal(amount)
#     if not success:
#         return {"error": "Insufficient funds"}
#     return {"username": username, "new_balance": user.balance}

# Buy route
@app.post("/buy")
def buy(username: str = Form(...), ticker: str = Form(...), amount: float = Form(...)):
    user = users.get(username)
    if not user:
        return {"error": "User not found"}
    stock = stocks.get(ticker)
    if not stock:
        return {"error": "Stock not found"}
    success = user.buy(amount, stock)
    if success == "Insufficient Balance":
        return {"error": "Insufficient balance"}
    return {"username": username, "ticker": ticker, "new_balance": user.balance, "holdings": user.holdings}

# Sell route
@app.post("/sell")
def sell(username: str = Form(...), ticker: str = Form(...), amount: float = Form(...)):
    user = users.get(username)
    if not user:
        return {"error": "User not found"}
    stock = stocks.get(ticker)
    if not stock:
        return {"error": "Stock not found"}
    success = user.sell(amount, stock)
    if success == "Insufficient Holdings":
        return {"error": "Insufficient holdings"}
    return {"username": username, "ticker": ticker, "new_balance": user.balance, "holdings": user.holdings}
#gotta figure out how to now connect back to data base instead of using this users library