from web import Search
from saved_tickers import Stocks
from pandas_api import Graphs


class Menu:
    def __init__(self, user, search, user_manager, stock_manager):
        self.user = user
        self.search = search
        self.user_manager = user_manager
        self.stock_manager = stock_manager
        self.not_logged_in = True
        self.exit = False

    def display(self):
        print('Hello and welcome to Stock Buddies!')

        while self.not_logged_in:
            login = input("""Would you like to:
    [1] Login
    [2] Create an account
    """).strip()

            if login == '1':
                self.handle_login()
            elif login == '2':
                self.handle_signup()
            else:
                print("Wrong input. Please only enter 1 or 2.")

    def handle_login(self):
        login_pass = self.user.login()
        if login_pass == 'wrong password':
            print("Please relogin either with your new password or with your current password.")
        elif login_pass:
            print(f"Hi {self.user.name}, you have successfully logged in. Welcome!")
            self.not_logged_in = False
        else:
            print("Your email is not in our system. Please create an account instead.")

    def handle_signup(self):
        self.not_logged_in = self.user.create_account()

    def create_menu(self):
        while not self.exit:
            print("\n--- Main Menu ---")
            print("1. Search for Stocks 🔍")
            print("2. Saved Stocks 💾")
            print("3. Get News 📰")
            print("4. Get Historical Price Graph 📈")
            print("5. Exit 👋")

            choice = input("Choose an option (1-5): ").strip()

            if choice == '1':
                self.search.stockMain()
            elif choice == '2':
                self.favourited_stocks()
            elif choice == '3':
                ticker = input("Please type the ticker that you want to search news for: ")
                news_searcher = Search(ticker)
                news_searcher.news_scrape()
            elif choice == '4':
                ticker = input("Please type the ticker that you want to make a graph for: ")
                graph = Graphs(ticker)
                graph.get_graph()
            elif choice == '5':
                print("Thank for using Stock Buddies GOODBYE!")
                self.exit = True
            else:
                print("Invalid choice. Please choose a valid option (1-5).")

    def favourited_stocks(self):
        print("Showing your saved stocks.")
        saved_stock = Stocks(self.stock_manager, self.user)
        stock_list = saved_stock.view_saved_stocks()
        print("\n")
        if len(stock_list) > 0:
            stay_on_sub_menu = True
            while stay_on_sub_menu:
                print("Select one of the options below to begin:")
                print("1. Export to csv")
                print("2 Delete saved stock")
                print("3. Exit back to main menu")
                option = input("To proceed enter the option number: ")
                if option == '1':
                    saved_stock.export_to_csv()
                elif option == '2':
                    delete_stock_index = input("Please key in the number of the stock you want to delete:")
                    try:
                        delete_stock_index = int(delete_stock_index)
                    except:
                        print('You have keyed a non-integer number, please try again\n')
                    else:
                        if delete_stock_index > len(stock_list):
                            print("Index not within range of favourited stocks, please try again\n")
                        else:
                            saved_stock.delete(stock_list[delete_stock_index-1][0])
                elif option =='3':
                    stay_on_sub_menu = False
                else:
                    print("You have entered an invalid number, please try again\n")
        else:
            print('You have no stocks saved yet! Please head to the search function first to save stocks!')


