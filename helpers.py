import requests

from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime

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
    """Look up quote for symbol."""
    if not symbol: return None
    url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
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
                    "Remember you are only allowed to output two things either stock name or sorry\n\n"
                    f"{company_name}"
                )
            }]
        }
    ]

    # Generate content
    response = model.generate_content(prompt)

    return response.text
