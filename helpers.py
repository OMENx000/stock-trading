import yfinance as yf # stock info
from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
from requests import get

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol using Yahoo Finance"""
    if not symbol: return None
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        # Some symbols may not return valid info
        if not info or "longName" not in info or "currentPrice" not in info:
            return None
        return {
            "name": info["longName"],
            "price": info["currentPrice"],
            "symbol": symbol.upper(),
            "domain": info.get("website")
        }
    except Exception:
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def convert_dt(dt):
    ''' convert date and time into right format '''
    return datetime.fromtimestamp(dt)

def check_quantity(quantity):
    ''' Check numerical inputs '''
    if quantity and quantity.isdigit():
        quantity = int(quantity)
        if quantity < 1:
            return False
    else:
            return False
    return quantity

def symbol_api(company_name):
    ''' User can search company symbol through name'''
    import google.generativeai as genai

    # Initialize the generative model
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Correct prompt structure
    prompt = [
        {
            "role": "user",
            "parts": [{
                "text": (
                    "This is an api for finance app. You are placed on a stock searching button. "
                    "Each person will just type the company name and you should only answer in its respect. "
                    "Each user is only allowed to enter only a company name that should be listed on stock exchange, "
                    "if user types anything else, reply sorry."
                    "Else if user typed correct company name just reply with one word company symbol(Upper case) of the stock exchange."
                    "The api i am using to get the stock from your provided symbol is yahoo finance (yfinance library in python),"
                    "so make sure to provide a symbol that corresponds to the yfinance. Like if user is searching US stock like apple,"
                    "apple is available on yfinance only as AAPL, but if user searched RELIANCE that is indian company it is listed on yfinance"
                    "as RELIANCE.NS or RELIANCE.BS you should give anyone but the name as valid in yfinance"
                    "Remember you are only allowed to output two things either stock name or sorry\n\n"
                    f"{company_name}"
                )
            }]
        }
    ]

    # Generate content
    response = model.generate_content(prompt)

    return response.text

def verify_email(email):
    load_dotenv()
    api_key = getenv("MAIL_API_KEY")
    url = f"http://apilayer.net/api/check?access_key={api_key}&email={email}&format=1"
    response = get(url)
    data =  response.json()
    return (
            data.get('format_valid') and
            data.get('mx_found')
        )
