from database import DatabaseManager, UserManager, StockManager
from users import User
from searcher import StockMarket
from web import Search
from saved_tickers import Stocks
from pandas_api import Graphs
from menu import Menu
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import re
import csv
import io

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
            session['email'] = email
            return redirect(url_for('home'))

    return render_template('login.html', error_message=error_message)


@app.route('/forgot_password', methods=["GET", "POST"])
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
    is_logged_in = session.get('is_logged_in', False)
    if not is_logged_in:
        flash("Please log in to access saved tickers", 'error')
        return redirect(url_for('login'))

    user_email = session.get('email')
    user_obj = User(user_manager)
    user_obj.email = user_email
    stocks_manager = Stocks(stock_manager, user_obj)

    if request.method == 'POST':
        # Handle delete stock
        if 'delete_stock' in request.form:
            ticker_to_delete = request.form.get("ticker", "").strip().upper()
            try:
                stocks_manager.delete(ticker_to_delete)
                flash(f"Stock {ticker_to_delete} deleted successfully!", 'success')
            except Exception as e:
                flash(f"Error deleting stock: {str(e)}", 'error')

        # Handle export to CSV
        elif 'export_stocks' in request.form:
            try:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["Ticker", "Company Name", "Market Cap", "Description"])

                stock_list = stock_manager.see_saved_stocks(user_email)
                writer.writerows(stock_list)

                output.seek(0)
                return Response(
                    output,
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=saved_stocks.csv"}
                )
            except Exception as e:
                flash(f"Error exporting to CSV: {str(e)}", 'error')

    # Get saved stocks for display
    stock_list = stock_manager.see_saved_stocks(user_email)
    stock_change_list = []
    for stock in stock_list:
        changes = search.get_stock_change(stock[0])
        stock_change_list.append(changes)

    return render_template("saved_tickers.html",
                           stocks=stock_list,
                           stock_change_list=stock_change_list,
                           is_logged_in=is_logged_in)


@app.route("/graph", methods=["GET", "POST"])
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


@app.route("/news", methods=["GET", "POST"])
def news():
    is_logged_in = session.get('is_logged_in', False)
    stock_symbol = None
    error_message = None
    articles = []
    if request.method == "POST":
        stock_symbol = request.form.get('stock_symbol').strip().upper()
        search_news = Search(stock_symbol)
        articles = search_news.news_scrape()

    return render_template('news.html', stock_symbol=stock_symbol, error_message=error_message,
                           is_logged_in=is_logged_in, articles=articles)


@app.route('/search_menu')
def search_menu():
    is_logged_in = session.get('is_logged_in', False)
    return render_template("search_menu.html", is_logged_in=is_logged_in)

@app.route('/basic_menu')
def basic_menu():
    is_logged_in = session.get('is_logged_in', False)
    return render_template("basic_menu.html", error_message=None, is_logged_in=is_logged_in)

@app.route('/advanced_menu')
def advanced_menu():
    is_logged_in = session.get('is_logged_in', False)
    return render_template("advanced_menu.html", sectors=search.sectors, exchanges=search.exchanges, error_message=None,
                           is_logged_in=is_logged_in)


@app.route('/basic_search', methods=['POST'])
def basic_search():
    is_logged_in = session.get('is_logged_in', False)
    try:
        data = search.nameSearch(request.form['keyword'], request.form['limit'])
        return render_template("basic_search.html", results=data, is_logged_in=is_logged_in)
    except:
        return render_template("basic_menu.html",
                               error_message="No results match your keyword. Please enter a different keyword.",
                               is_logged_in=is_logged_in)


@app.route('/advanced_search', methods=['GET','POST'])
def advanced_search():  # put application's code here
    is_logged_in = session.get('is_logged_in', False)
    try:
        data = search.advancedFilter(request.form['sectors'], request.form['exchanges'], request.form['mktmax'],
                                     request.form['mktmin'], request.form['limit'])
        data = [stock for stock in data if stock.get('price') is not None]
        data = [{**stock, 'sector': 'NA' if stock.get('sector') == '' else stock.get('sector')} for stock in data]
        return render_template("advanced_search.html", results=data, is_logged_in=is_logged_in)
    except Exception as e:
        print(e)
        return render_template("advanced_menu.html", error_message="No results found. Please try again.",
                               is_logged_in=is_logged_in)


@app.route('/more_info', methods=['POST'])
def more_info():
    is_logged_in = session.get('is_logged_in', False)
    try:
        info = search.getStockInfo(request.form['info'])
        return render_template("more_info.html", data=info, is_logged_in=is_logged_in)
    except:
        return render_template("more_info.html", data=[], error_message="Stock not found.", is_logged_in=is_logged_in)


@app.route('/save_stock', methods=['POST'])
def save_stock():
    is_logged_in = session.get('is_logged_in', False)
    info = search.getStockInfo(request.form['save'])
    search.saveStock(info)
    return render_template("successful_save.html", is_logged_in=is_logged_in)


if __name__ == '__main__':
    app.run(debug=True)
