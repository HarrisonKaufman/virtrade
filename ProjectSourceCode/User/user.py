##creating User object to connect to the database and perform operations needed to track user info and balance
from fastapi import FastAPI, Form
app = FastAPI()
#app = FastAPI() — creates the actual web application instance

# In-memory "database" for demonstration (replace with real DB later)
users = {}
# gotta figure out how to instead of using this users array use the database

class Stock:
    def __init__(self, ticker, price):
        self.ticker = ticker
        self.price = price

class User:
    def __init__(self, username, password, email, balance=0.00, holdings=None):
        self.username = username
        self.password = password
        self.email = email
        self.balance = balance
        self.holdings = holdings if holdings is not None else {}

    def buy(self, amount, stock):
        if self.balance >= amount:
            self.balance -= amount * stock.price
            self.holdings[stock.ticker] = self.holdings.get(stock.ticker, 0) + amount
            return self.balance
        else:
            return "Insufficient Balance"
        

    def sell(self, amount, stock):
        if self.holdings.get(stock.ticker, 0) >= amount:
            self.holdings[stock.ticker] -= amount
            self.balance += amount * stock.price
            return 1
        else:
            return "Insufficient Holdings"

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
    if not success:
        return {"error": "Insufficient holdings"}
    return {"username": username, "ticker": ticker, "new_balance": user.balance, "holdings": user.holdings}
#gotta figure out how to now connect back to data base instead of using this users library