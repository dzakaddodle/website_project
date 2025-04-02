from database import DatabaseManager, UserManager, StockManager
from users import User
from searcher import StockMarket
from web import Search
from saved_tickers import Stocks
from pandas_api import Graphs
from menu import Menu
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Database
db = DatabaseManager()
db.create_tables()

user_manager = UserManager(db)
stock_manager = StockManager(db)

user = User(user_manager)
search = StockMarket(stock_manager, user)

menu = Menu(user, search, user_manager, stock_manager)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            error_message = 'Passwords do not match. Please try again.'
            return render_template('register.html', error_message=error_message)
        else:
            if user.create_account(name, email, password):
                error_message = 'You already have an account with us, please login instead'
                return render_template('register.html', error_message=error_message)
            else:
                flash("You have successfully created an account! Please login")
                return render_template('login.html')
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    error_message = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        login_output = user.login(email=email, password=password)
        if not login_output:
            error_message = 'You currently do not have an account with us, please register instead!'
        elif login_output == 'wrong password':
            error_message = 'You have entered the wrong password. Please try again or change your password'
        elif login_output:
            return render_template('menu.html', name=user.name)

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


@app.route('/main_menu')
def main_menu():
    return render_template('menu.html')

@app.route('/search_menu')
def search_menu():
    return render_template("search_menu.html")

@app.route('/basic_menu')
def basic_menu():
    return render_template("basic_menu.html", error_message=None)

@app.route('/advanced_menu')
def advanced_menu():
    return render_template("advanced_menu.html", sectors=search.sectors, exchanges=search.exchanges)

@app.route('/basic_search', methods=['POST'])
def basic_search():
    try:
        data = search.nameSearch(request.form['keyword'], request.form['limit'])
        return render_template("basic_search.html", results=data)
    except:
        return render_template("basic_menu.html", error_message="No results match your keyword. Please enter a different keyword.")

@app.route('/advanced_search', methods=['POST'])
def advanced_search():  # put application's code here
    #if request.method == "POST":
    data = search.advancedFilter(request.form['sectors'], request.form['exchanges'], request.form['mktmax'], request.form['mktmin'], request.form['limit'])
    return render_template("advanced_search.html", results=data)

@app.route('/more_info', methods=['POST'])
def more_info():
    info = search.getStockInfo(request.form['info'])
    return render_template("more_info.html", data=info)

@app.route('/save_stock', methods=['POST'])
def save_stock():
    info = search.getStockInfo(request.form['save'])
    search.saveStock(info)
    return "Stock has been saved"

if __name__ == '__main__':
    app.run(debug=True)
