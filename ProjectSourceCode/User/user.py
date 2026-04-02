##creating User object to connect to the database and perform operations needed to track user info and balance



# In-memory "database" for demonstration (replace with real DB later)
users = {}
# gotta figure out how to instead of using this users array use the database
class User: 
    def __init__(self, username, password, email, balance = 0.00):
        self.username = username
        self.password = password
        self.email = email
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

    def withdrawal(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            return self.balance
        else:
            return "Insufficient Balance"

#sign up route post method 
app.post("/sign up")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if username and email in users:
        return "Username or Email already exists"
    else:
        new_user= User(username, password, email)
        users[username] = new_user
        return "User created successfully"

#deposit route
app.post("/deposit")
def deposit(username: str = Form(...), amount: float = Form(...)):
    user = users.get(username)
    if not user:
        return {"error": "User not found"}
    user.deposit(amount)
    return {"username": username, "new_balance": user.balance}

#withdrawal route
app.post("/withdrawal")
def withdrawal(username: str = Form(...), amount: float = Form(...)):
    user = users.get(username)
    if not user:
        return {"error": "User not found"}
    success = user.withdrawal(amount)
    if not success:
        return {"error": "Insufficient funds"}
    return {"username": username, "new_balance": user.balance}

#gotta figure out how to now connect back to data base instead of using this users library