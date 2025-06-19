import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

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
    id = session["user_id"]
    stocks = db.execute("SELECT * FROM owned_stocks WHERE id = ?",id )
    stock_details=[]
    investments=0

    for stock in stocks:
       symbol = stock["symbol"]
       shares = stock["shares"]
       stock_price = lookup(symbol)["price"]
       total_stock = stock_price*shares
       investments +=total_stock
       stock_details.append({"symbol":symbol,"shares":shares,"stock_price":stock_price,"total_stock":total_stock})
    cash = db.execute("SELECT cash FROM users WHERE id=?",id)[0]['cash']
    total = cash+ investments
    return render_template("index.html", stock_details=stock_details, cash=cash,investments=investments, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method =="POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("We need all the informations to buy a stock",500)
        else:
            symbol=request.form.get("symbol")
            shares=int(request.form.get("shares"))
            user_id = session["user_id"]
            user_cash = db.execute("SELECT cash FROM users WHERE id = ?",user_id)[0]["cash"]
            stock_info = lookup(symbol)
            if stock_info == None: ##checking if stock exists
                return apology("Couldnt find symbol",503)
            else:
                stock_price = stock_info["price"]
                purchase_price = stock_price * shares
                if purchase_price > user_cash: ##checking if there is enough money
                    return apology("Not enough cash :(",501)
                else:
                    session["symbol"] = symbol
                    session["shares"] = shares
                    session["stock_price"] = stock_price
                    session["purchase_price"] = purchase_price
                    session["user_cash"]=user_cash
                    return render_template("confirm_buy.html",symbol=symbol,stock_price=stock_price,shares=shares,total_stock=purchase_price,)


    else:
        return render_template("buy.html")


@app.route("/confirm_buy",methods=["GET", "POST"])
@login_required
def confirm():
    if request.method=="POST":
        type="Buy"
        user_id=session["user_id"]
        symbol = session.get("symbol")
        shares = session.get("shares")
        user_cash = session.get("user_cash")
        purchase_price = session.get("purchase_price")

        user_cash -= purchase_price ##updating money
        db.execute("UPDATE users SET cash = ? WHERE id=?",user_cash,user_id) #inserting updated money
        stocks = db.execute("SELECT symbol FROM owned_stocks WHERE id =?",user_id)
        stock_exists=False
        for stock in stocks:
            if stock["symbol"] == symbol:
                db.execute("UPDATE owned_stocks SET shares = shares+? WHERE id =? AND symbol =?",shares,user_id,symbol)
                db.execute("INSERT INTO history(type,symbol,shares,value,id) VALUES(?,?,?,?,?)",type,symbol,shares,purchase_price,user_id)
                stock_exists=True
                break
        if not stock_exists:
            db.execute("INSERT INTO owned_stocks (id, symbol, shares) VALUES (?, ?, ?)", user_id, symbol, shares)
            db.execute("INSERT INTO history(type,symbol,shares,value,id) VALUES(?,?,?,?,?)",type,symbol,shares,purchase_price,user_id)
        return redirect("/")
    else:
        return render_template("confirm_buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    history = db.execute("SELECT * FROM history WHERE id=?",user_id)
    history_details=[]
    for action in history:
        type = action["type"]
        symbol = action["symbol"]
        shares = action["shares"]
        value = action["value"]
        history_details.append({"type":type,"symbol":symbol,"shares":shares,"value":value})

    return render_template("history.html",history_details=history_details)


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
    if request.method =="POST":
        symbol = request.form.get("symbol")
        result=lookup(symbol)
        if result != None:
            return render_template("quote_result.html",price=result["price"],symbol=result["symbol"])
        else:
            return apology("Symbol couldnt be found",403)

    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method=="POST":
        if not request.form.get("user"):
            return apology("No username :(")
        elif not request.form.get("password"):
            return apology("No password :(")
        elif not request.form.get("confirmed_password"):
            return apology("No confirmed password :(")
        else:
            username = request.form.get("user")
            password = request.form.get("password")
            confirmed_password = request.form.get("confirmed_password")
            if password != confirmed_password:
                return apology("Passwords dont match!")

            else:
                # Check if the username already exists
                existing = db.execute("SELECT * FROM users WHERE username = ?", (username,))
                if len(existing)>0:
                    return apology("Username is already taken!", 400)
                else:
                    # Insert the new user into the database

                    db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
                    user_id = db.execute("SELECT id FROM users WHERE username = ?", username)
                    session["user_id"] = user_id
                    return redirect("/login")


    else:
        return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method=="POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("You need to give all the informations in order to sell a stock",505)
        else:
            type="Sell"
            symbol = request.form.get("symbol")
            shares = int(request.form.get("shares"))
            user_id = session["user_id"]
            stock_price = lookup(symbol)["price"]
            if stock_price == None:
                return apology("Stock doesnt exist :(",506)
            else:
                stocks = db.execute("SELECT symbol,shares FROM owned_stocks WHERE id =?",user_id)
                stock_exist = False
                for stock in stocks:
                            if stock["symbol"] == symbol and stock["shares"] == shares:
                                db.execute("DELETE FROM owned_stocks WHERE id =? AND symbol =?",user_id,symbol)
                                stock_exist = True
                                break
                            if  stock["symbol"] == symbol and stock["shares"] > shares:
                                db.execute("UPDATE owned_stocks SET shares =shares-?",shares)
                                stock_exist=True
                                break
                if not stock_exist:
                    return apology("You dont have the quantity of shares you are trying to sell",506)

                sell_total = stock_price*shares
                db.execute("UPDATE users SET cash=cash+? WHERE id= ?",sell_total,user_id)
                db.execute("INSERT INTO history(type,symbol,shares,value,id) VALUES(?,?,?,?,?)",type,symbol,shares,sell_total,user_id)
                return redirect("/")
    else:
        return render_template("sell.html")







