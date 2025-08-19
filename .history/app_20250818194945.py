import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd, convert_dt, check_quantity

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["convert_dt"] = convert_dt

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    context = {}
    context["shares"] = db.execute("SELECT * FROM shares_owned WHERE user_id = ?", session["user_id"])
    sum = db.execute("SELECT SUM(total_holdings) FROM shares_owned WHERE user_id = ?", session["user_id"])[0]["SUM(total_holdings)"]
    if not sum:
        sum = 0
    context["cash"] = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    context["total"] = context["cash"] + sum

    return render_template("index.html", context=context)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    balance = int(user_info["cash"])

    if request.method == "POST":
        symbol, quantity = request.form.get("symbol"), request.form.get("quantity")
        quantity = check_quantity(quantity)
        if not quantity or not symbol:
            return apology("Enter Valid quantity")
        symbol = symbol.upper()
        
        info = lookup(symbol)
        if not symbol or not info: # if symbol is wrong
            return apology("Enter Valid Symbol")
        

        #check if user can afford with available balance
        if info["price"] * quantity > balance:
            return apology("Insufficient Balance!")

        dt = int(datetime.now().timestamp())
        # record purchase with action = "P"
        db.execute("INSERT INTO history(user_id, company_name, company_symbol, action, quantity, price, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_info["id"], info["name"], symbol, "P", quantity, info["price"], dt)


        # add into users shares
        shares_owned = db.execute("SELECT * FROM shares_owned WHERE user_id = ?", user_info["id"]) # get current holdings

        if shares_owned: # if already have that type of shares
            db.execute("UPDATE shares_owned SET quantity = ?, total_holdings = ? WHERE user_id = ? AND symbol = ?", shares_owned[0]["quantity"] + quantity,
                       shares_owned[0]["total_holdings"] + (quantity * info["price"]), user_info["id"], symbol)
        else:
            db.execute("INSERT INTO shares_owned(user_id, symbol, quantity, total_holdings) VALUES(?, ?, ?, ?)", user_info["id"],
                       symbol, quantity, info["price"] * quantity)


        # decrease balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance - (info["price"] * quantity), user_info["id"])

        return redirect("/")
    return render_template("purchase.html", balance=balance)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    context = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
    return render_template("history.html", context=context)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        info = lookup(symbol)

        if not symbol or not info: # if input is wrong
            return apology("Enter Valid Symbol")
        return render_template("quote.html", info=info) # if request is post and input is correct
    return render_template("quote.html") # get request

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username, password, confirmation = request.form.get("username"), request.form.get("password"), request.form.get("confirmation")
        if not username or not password or not confirmation: # if any field is blank
            return apology("You must fill all fields correctly!")
        if password != confirmation:
            return apology("Passwords does not match")
        if db.execute("SELECT * FROM users WHERE username = ?", username):  # username already taken
            return apology("Username is already taken!")

        hash = generate_password_hash(password)
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", username, hash) # put into database

        return redirect("/login")
    return render_template("register.html") # get request

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    balance = int(user_info["cash"])
    # check if user owns the stock in particular quantity
    shares_owned = db.execute("SELECT * FROM shares_owned WHERE user_id = ?", user_info["id"])

    if request.method == "POST":
        symbol, quantity = request.form.get("symbol").upper(), request.form.get("quantity")
        quantity = check_quantity(quantity)
        if not quantity:
            return apology("Enter Valid quantity")
        
        info = lookup(symbol)
        if not symbol or not info: # if symbol is wrong
            return apology("Enter Valid Symbol")

        if not shares_owned or shares_owned[0]["quantity"] < quantity:
            return apology("No shares available to sell")

        # if everything is okay
        dt = int(datetime.now().timestamp())
        # record sell with action = "S"
        db.execute("INSERT INTO history(user_id, company_name, company_symbol, action, quantity, price, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_info["id"], info["name"], symbol, "S", quantity, info["price"], dt)

        # change shares owned
        if shares_owned[0]["quantity"] > quantity: # update quantity if more available
            db.execute("UPDATE shares_owned SET quantity = ?, total_holdings = ? WHERE user_id = ? AND symbol = ?",
                       shares_owned[0]["quantity"] - quantity, shares_owned[0]["total_holdings"] - (info["price"] * quantity), user_info["id"], symbol)

        elif shares_owned[0]["quantity"] == quantity: # remove from list if quantity match
            db.execute("DELETE FROM shares_owned WHERE user_id = ? AND symbol = ?", user_info["id"], symbol)

        # increase balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance + (info["price"] * quantity), user_info["id"])

        return redirect("/")
    return render_template("sell.html", balance=balance, shares=shares_owned)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    ''' Users can change password when logged in'''
    if request.method == "POST":
        current_password, new_password = request.form.get("current_password"), request.form.get("new_password")
        if not current_password or not new_password or not request.form.get("confirm_new_password"): # check all fields are filled
            return apology("Enter Valid Credentials")

        # current password is not correct
        if not check_password_hash((db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"]), current_password):
            return apology("Current password is incorrect")

        # if old and new are same
        if current_password == new_password:
            return apology("Passwords cannot be same")

        # new passwords does not match
        if new_password != request.form.get("confirm_new_password"):
            return apology("Passwords does not match")

        # change the passowrd in db
        db.execute("UPDATE users SET hash=? WHERE id = ?", generate_password_hash(new_password), session["user_id"])
        return redirect("/")
    return render_template("change_password.html")

@app.route("/lookup", methods=["GET"])
def lookup_api():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400

    info = lookup(symbol)  # returns dict like {"name": "...", "symbol": "...", "price": ...}
    if not info:
        return jsonify({"error": "Symbol not found"}), 404

    return jsonify(info)

@app.route("/add_cash", methods=["GET", "POST"])
def add_cash():
    user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    if request.method == "POST":
        cash = int(request.form.get("cash", default=0))
        # if field is empty or number is less than 100
        if cash < 100:
            return apology("Enter amount greater than 100")
        elif cash > 100000: # for fun
            return apology("Be in your limits")

        db.execute("UPDATE users SET cash=? WHERE id=?", cash + user_info[0]["cash"], user_info[0]["id"])
        return redirect("/buy")
    return render_template("add_cash.html", balance=user_info[0]["cash"])
