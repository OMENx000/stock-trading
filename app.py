import secrets
from datetime import datetime
from os import getenv

import pytz
import pandas_market_calendars as mcal # check if the market is open
from authlib.integrations.flask_client import OAuth
from cs50 import SQL
from dotenv import load_dotenv
from flask import (Flask, abort, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import (apology, check_quantity, convert_dt, login_required,
                     lookup, symbol_api, usd)

# Loading environment variables
load_dotenv()

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["convert_dt"] = convert_dt

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = getenv("FLASK_SECRET_KEY")
Session(app)

# Instanciating oauth client
oauth = OAuth(app=app)

oauth.register(
    name="google",
    client_id=getenv("client_id_oauth"),
    client_secret=getenv("oauth_secret"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    # Boilerplate code necessary for oauth flask register work
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.before_request
def set_csrf_token():
    '''Generate csrf manual token for forms'''
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

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
    """Show portfolio of stocks, only update prices if market is open"""
    context = {}
    context["shares"] = db.execute("SELECT * FROM shares_owned WHERE user_id = ?", session["user_id"])
    sum = db.execute("SELECT SUM(total_holdings) FROM shares_owned WHERE user_id = ?", session["user_id"])[0]["SUM(total_holdings)"]
    if not sum:
        sum = 0
    context["cash"] = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    context["total"] = context["cash"] + sum
    
    # check if market is open or close (currently only for us market)
    # Get NYSE calendar
    nyse = mcal.get_calendar('NYSE')
  
    # Current datetime in Eastern Time
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    today = now.date()

    # Get today's schedule
    schedule = nyse.schedule(start_date=today, end_date=today)

    if schedule.empty: # if there is ne schedule (holiday or wwekend) 
        market_open = False
    else:
        # Check if market is open now
        market_open = nyse.open_at_time(schedule, now)

    return render_template("index.html", context=context, market_open=market_open)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    balance = int(user_info["cash"])

    if request.method == "POST":
        symbol, quantity = request.form.get("symbol").upper(), request.form.get("quantity")
        quantity = check_quantity(quantity)
        if not quantity:
            return apology("Enter Valid quantity")
        if not symbol:
            return apology("Enter Valid Symbol")
        
        '''
        info = lookup(symbol)
        if not symbol or not info: # if symbol is wrong
            return apology("Enter Valid Symbol")
        

        #check if user can afford with available balance
        if info["price"] * quantity > balance:
            return apology("Insufficient Balance!")

        dt = int(datetime.now().timestamp())

        # add into users shares
        shares_owned = db.execute("SELECT * FROM shares_owned WHERE user_id = ? AND symbol = ?", user_info["id"], symbol) # get current holdings

        if shares_owned: # if already have that type of shares
            db.execute("UPDATE shares_owned SET quantity = ?, total_holdings = ? WHERE user_id = ? AND symbol = ?", shares_owned[0]["quantity"] + quantity,
                       shares_owned[0]["total_holdings"] + (quantity * info["price"]), user_info["id"], symbol)
        else:
            db.execute("INSERT INTO shares_owned(user_id, symbol, quantity, total_holdings) VALUES(?, ?, ?, ?)", user_info["id"],
                       symbol, quantity, info["price"] * quantity)
            
        # decrease balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance - (info["price"] * quantity), user_info["id"])

        # record purchase with action = "P"
        db.execute("INSERT INTO history(user_id, company_name, company_symbol, action, quantity, price, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_info["id"], info["name"], symbol, "P", quantity, info["price"], dt)

        return redirect("/")
        '''
    
    user_company_symbol = request.args.get("symbol", default="")
    return render_template("purchase.html", balance=balance, user_symbol=user_company_symbol)
    
@app.route("/company/stock", methods=["GET", "POST"])
@login_required
def company_stock():
    """Renders main page for any particular stock"""
    symbol = request.form.get("symbol")
    if not symbol:
        return apology("No symbol provided")

    info = lookup(symbol)
    if not info:
        return apology("No data available")

    return render_template("company_stock.html", info=info)

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
    session.pop("user_id", None)
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        token = request.form.get("csrf_token")
        print(f"Form - {token}, session_token = {session.get('csrf_token')}")
        if not token or token != session.get("csrf_token"):
            abort(403)
            
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

@app.route("/google_login")
def google_login():
    # Redirecting in oauth 
    redirect_uri = url_for('google_authorised', _external=True)
    print(redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/login/google/authorised")
def google_authorised():
    # Getting user info after he logged in with google
    # TODO: this lines are commented but will be used later
    token = oauth.google.authorize_access_token()
    userinfo = oauth.google.get('userinfo')
    # TODO: Extract user info and connect with the database
    print(userinfo.json())

    return 'foo foo foo'

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.pop("user_id", None)

    # Redirect user to login form
    return redirect("/")


@app.route("/stocks", methods=["GET", "POST"])
@login_required
def stocks():
    """Get stock quote."""
    # request from /get_symbol
    if request.method == "POST": # ai symbol search
        symbol = request.args.get("symbol")
        return redirect(url_for("stock")) if symbol else apology("Enter Valid Symbol")
    
    symbol = request.args.get("symbol", default="") # already being checked in get_symbol
    return render_template("stocks.html", symbol=symbol) # if request is post and input is correct

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
        symbol, quantity = request.form.get("symbol"), request.form.get("quantity")
        quantity = check_quantity(quantity)
        if not quantity:
            return apology("Enter Valid quantity")
          
        info = lookup(symbol)
        if not symbol or not info: # if symbol is wrong
            return apology("Enter Valid Symbol")

        symbol = symbol.upper()

        if not shares_owned or shares_owned[0]["quantity"] < quantity:
            return apology("No shares available to sell")

        # if everything is okay
        dt = int(datetime.now().timestamp())
                # change shares owned
        if shares_owned[0]["quantity"] > quantity: # update quantity if more available
            db.execute("UPDATE shares_owned SET quantity = ?, total_holdings = ? WHERE user_id = ? AND symbol = ?",
                       shares_owned[0]["quantity"] - quantity, shares_owned[0]["total_holdings"] - (info["price"] * quantity), user_info["id"], symbol)

        elif shares_owned[0]["quantity"] == quantity: # remove from list if quantity match
            db.execute("DELETE FROM shares_owned WHERE user_id = ? AND symbol = ?", user_info["id"], symbol)

        # increase balance
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance + (info["price"] * quantity), user_info["id"])

        # record sell with action = "S"
        db.execute("INSERT INTO history(user_id, company_name, company_symbol, action, quantity, price, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   user_info["id"], info["name"], symbol, "S", quantity, info["price"], dt)


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
        cash = int(request.form.get("amount", default=0))
        # if field is empty or number is less than 100
        if cash < 100:
            return apology("Enter amount greater than 100")
        elif cash > 100000: # for fun
            return apology("Be in your limits")

        db.execute("UPDATE users SET cash=? WHERE id=?", cash + user_info[0]["cash"], user_info[0]["id"])
        return redirect("/stocks")
    return render_template("add_cash.html", balance=user_info[0]["cash"])

@app.route("/get_symbol", methods=["GET", "POST"])
def get_symbol():
    ''' Finds symbol from with ai model and fill in the field (works for both purchase and stocks page)'''
    company_name = request.form.get("company_name")
    source = request.form.get("source") # which page has sent the request
    
    if not company_name:
        return redirect("/buy") if source == "purchase_page" else redirect("/stocks")
    
    symbol = symbol_api(company_name) # get symbol
    
    if "sorry" in symbol:  # if anything else entered other than company name
        return apology("Sorry! Enter Valid Company Name")
    
    return redirect(url_for("buy", symbol=symbol)) if source == "purchase_page" else redirect(url_for("stocks", symbol=symbol))