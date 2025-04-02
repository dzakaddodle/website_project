from database import DatabaseManager, UserManager, StockManager
from users import User
from searcher import StockMarket
from web import Search
from saved_tickers import Stocks
from pandas_api import Graphs
from menu import Menu
from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
import csv
import os

app = Flask(__name__)
app.secret_key = 'weloveprogramming:)'

db = DatabaseManager()
db.create_tables()

user_manager = UserManager(db)
stock_manager = StockManager(db)

user = User(user_manager)
search = StockMarket(stock_manager, user)

menu = Menu(user, search, user_manager, stock_manager)

# Email regex pattern
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


@app.route('/')
def home():
    is_logged_in = session.get('is_logged_in', False)
    user_name = session.get('user_name', '')
    return render_template('home.html', is_logged_in=is_logged_in, user_name=user_name)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if all fields are filled
        if not all([name, email, password, confirm_password]):
            error_message = 'All fields are required.'
            return render_template('register.html', error_message=error_message)
        
        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            error_message = 'Invalid email format. Please enter a valid email.'
            return render_template('register.html', error_message=error_message)

        # Check if passwords match
        if password != confirm_password:
            error_message = 'Passwords do not match. Please try again.'
            return render_template('register.html', error_message=error_message)
        
        # Check if email already exists in the database
        if user.create_account(name, email, password):
            error_message = 'You already have an account with us, please login instead'
            return render_template('register.html', error_message=error_message)
        
        else:
            flash("You have successfully created an account! Please login")
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    error_message = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        login_output = user.login(email=email, password=password)
        
        # Check if user already exists in the database
        if not login_output:
            error_message = 'You currently do not have an account with us, please register instead!'
        
        # Check if user entered the correct password
        elif login_output == 'wrong password':
            error_message = 'You have entered the wrong password. Please try again or change your password'
        
        # Successful login
        elif login_output:
            session['is_logged_in'] = True
            session['name'] = user.name
            return redirect(url_for('home'), name=user.name, is_logged_in=True)

    return render_template('login.html', error_message=error_message)


@app.route('/forgot_password', methods=["GET","POST"])
def forgot_password():
    error_message = None
    if request.method == "POST":
        email = request.form["email"]
        check = user_manager.email_check(email=email)
        if check == 0:
            error_message = 'There is no account linked to that email, please register instead!'
        else:
            return render_template('reset_password.html', given_email=email, error_message=None)

    return render_template('forgot_password.html', error_message=error_message)


@app.route('/reset_password', methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Ensure the new password and confirmation match
        if new_password != confirm_password:
            error_message = 'Passwords do not match. Please try again.'
            return render_template('reset_password.html', given_email=email, error_message=error_message)

        # If passwords match, update the user's password
        success = user.change_password(email, new_password)

        if success:
            flash("Your password has been successfully reset!")
            return redirect(url_for('login'))

        else:
            # If something went wrong while updating the password
            error_message = 'Failed to reset the password. Please try again.'
            return render_template('reset_password.html', given_email=email, error_message=error_message)

    # If it's a GET request, just display the form
    return render_template('reset_password.html')


@app.route('/navbar')
def navbar():
    return render_template('navbar.html')


@app.route('/logout')
def logout():
    session.pop('is_logged_in', None)
    return redirect(url_for('home'))


@app.route('/saved_tickers', methods=['GET', 'POST'])
def saved_tickers():
    if not session.get('is_logged_in'):
        flash("You must be logged in to access saved stocks.")
        return redirect(url_for('login'))

    user_email = session.get('email')
    user_obj = User(user_manager)
    user_obj.email = user_email
    stocks = Stocks(stock_manager, user_obj)

    if request.method == 'POST':
        if 'ticker' in request.form and 'name' in request.form:  # Adding stock
            ticker = request.form['ticker']
            name = request.form['name']
            market_cap = request.form['market_cap']
            description = request.form['description']
            stocks.save(ticker, name, market_cap, description)
            flash("Stock added successfully!")

        elif 'ticker' in request.form and 'delete' in request.form:  # Deleting stock
            ticker = request.form['ticker']
            stocks.delete(ticker)
            flash("Stock deleted successfully!")

        elif 'export' in request.form:  # Exporting stocks to CSV
            stocks.export_to_csv()
            flash("Stocks exported successfully!")

        return redirect(url_for('saved_tickers'))

    stock_list = stocks.view_saved_stocks()
    return render_template('saved_tickers.html', stocks=stock_list)


@app.route("/graph", methods=["GET","POST"])
def graph():
    is_logged_in = session.get('is_logged_in', False)
    stock_symbol = None
    plot_url = None
    error_message = None

    if request.method == "POST":
        stock_symbol = request.form.get("stock_symbol", "").strip().upper()
        graph = Graphs(stock_symbol)
        plot_url, error_message = graph.get_graph()

    return render_template("graph.html", plot_url=plot_url, error_message=error_message, stock_symbol=stock_symbol,
                           is_logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(debug=True)
