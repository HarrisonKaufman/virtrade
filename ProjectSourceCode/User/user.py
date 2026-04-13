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
        """Load a user from the database by ID (used by Flask API for trades)."""
        conn = get_db()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            return cls(row["username"], row["password_hash"], row["email"], float(row["balance"]), user_id=row["id"])
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
                    cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                    cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                                (self.user_id, -total_cost, self.balance))
                    conn.commit()
                finally:
                    conn.close()
            return self.balance
        else:
            return "Insufficient Balance"

    def sell(self, amount, stock):
        # If loaded from DB, skip in-memory holdings check (holdings not yet persisted)
        if not self.user_id and self.holdings.get(stock.ticker, 0) < amount:
            return "Insufficient Holdings"
        self.holdings[stock.ticker] = max(0, self.holdings.get(stock.ticker, 0) - amount)
        self.balance += amount * stock.price
        # Persist to DB if this user was loaded from DB
        if self.user_id:
            total_gain = amount * stock.price
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("UPDATE users SET balance = %s WHERE id = %s", (self.balance, self.user_id))
                cur.execute("INSERT INTO balance_transactions (user_id, amount, balance_after) VALUES (%s, %s, %s)",
                            (self.user_id, total_gain, self.balance))
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