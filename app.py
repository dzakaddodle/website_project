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


# Route for Home (Dashboard)
# @app.route('/')
# def home():
#     if 'user' not in session:
#         return redirect(url_for('login'))  # Redirect to login if the user is not logged in
#     # Initialize UserManager and StockManager only after login
#     user_manager = UserManager(db)
#     stock_manager = StockManager(db)
#     user = User(user_manager)
#     user.name = session['user']  # Retrieve user name from session
#     return render_template('index.html', user=user)
#
#
# # Route for Login
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#
#         user_manager = UserManager(db)  # Initialize UserManager
#         user = User(user_manager)
#
#         # Now call the login method without passing email and password as arguments
#         login_result = user.login()
#
#         if login_result == 'wrong password':
#             error_message = "Incorrect password. Please reset or try again."
#             return render_template('login.html', error_message=error_message)
#         elif login_result == True:
#             session['user'] = user.name  # Store user in session
#             return redirect(url_for('home'))
#         else:
#             error_message = "There was an error with your login. Please try again."
#             return render_template('login.html', error_message=error_message)
#     return render_template('login.html')
#
#
# # Route for Create Account
# @app.route('/create_account', methods=['GET', 'POST'])
# def create_account():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']
#
#         user_manager = UserManager(db)  # Initialize UserManager
#         user = User(user_manager)
#
#         if user_manager.add_user(name=name, email=email, password=password):
#             return redirect(url_for('login'))
#         else:
#             error_message = "An account with that email already exists. Please login instead."
#             return render_template('create_account.html', error_message=error_message)
#     return render_template('create_account.html')
#
#
# # Route for Search Stocks
# @app.route('/search', methods=['GET', 'POST'])
# def search_stocks():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         stock_query = request.form['stock_query']
#
#         # Initialize Search functionality
#         user_manager = UserManager(db)
#         stock_manager = StockManager(db)
#         search = StockMarket(stock_manager, user_manager)
#         search_results = search.search(stock_query)
#
#         return render_template('search_results.html', results=search_results)
#     return render_template('search.html')
#
#
# # Route for Saved Stocks
# @app.route('/saved_stocks', methods=['GET', 'POST'])
# def saved_stocks():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#
#     user_manager = UserManager(db)
#     stock_manager = StockManager(db)
#     user = User(user_manager)
#     user.name = session['user']  # Use session data to assign user
#     saved_stock = Stocks(stock_manager, user)
#     stock_list = saved_stock.view_saved_stocks()
#
#     if request.method == 'POST':
#         option = request.form['option']
#         if option == 'export':
#             saved_stock.export_to_csv()
#             return redirect(url_for('saved_stocks'))
#         elif option == 'delete':
#             delete_stock_index = int(request.form['stock_index'])
#             if delete_stock_index <= len(stock_list):
#                 saved_stock.delete(stock_list[delete_stock_index - 1][0])
#                 return redirect(url_for('saved_stocks'))
#     return render_template('saved_stocks.html', stock_list=stock_list)
#
#
# # Route for Stock News
# @app.route('/news', methods=['GET', 'POST'])
# def news():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         ticker = request.form['ticker']
#         news_searcher = Search(ticker)
#         news_searcher.news_scrape()
#         return render_template('news_results.html', ticker=ticker)
#     return render_template('news.html')
#
#
# # Route for Stock Graph
# @app.route('/graph', methods=['GET', 'POST'])
# def graph():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         ticker = request.form['ticker']
#         graph = Graphs(ticker)
#         graph.get_graph()
#         return render_template('graph.html', ticker=ticker)
#     return render_template('graph_form.html')
#
#
# # Route for Logout
# @app.route('/logout')
# def logout():
#     session.pop('user', None)
#     return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login', methods=["GET","POST"])
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
            return render_template('menu.html')

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


if __name__ == '__main__':
    app.run(debug=True)