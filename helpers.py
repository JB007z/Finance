import os
import requests
import urllib.parse
import csv
import datetime
import pytz
import requests
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps


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
    """Look up quote for symbol using Alpha Vantage API."""

    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("ALPHA_VANTAGE_API_KEY environment variable not set. Please set it before running the app.")
        return None

    try:
        url = (
            f"https://www.alphavantage.co/query?"
            f"function=GLOBAL_QUOTE&"
            f"symbol={urllib.parse.quote_plus(symbol)}&"
            f"apikey={api_key}"
        )
        response = requests.get(url)
        response.raise_for_status() 
    except requests.RequestException as e:
        print(f"Error fetching data from Alpha Vantage: {e}")
        return None

    # Parse response
    try:
        quote_data = response.json()
        # Alpha Vantage returns data under a "Global Quote" key if successful
        global_quote = quote_data.get("Global Quote")

        if global_quote and "05. price" in global_quote and "01. symbol" in global_quote:
            price = float(global_quote["05. price"])
            symbol = global_quote["01. symbol"]
            name = global_quote.get("02. open") 
                                                 
                                                 
            return {
                "name": name, 
                "price": price,
                "symbol": symbol
            }
        else:
            # Check for API call frequency limits or invalid symbol messages
            error_message = quote_data.get("Note") or quote_data.get("Error Message")
            if error_message:
                print(f"Alpha Vantage API Error/Note: {error_message}")
            return None  # No valid quote data returned for the symbol
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error parsing Alpha Vantage response: {e}")
        return None



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
