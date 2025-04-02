import requests
# import os
# from dotenv import load_dotenv
from web import Search
from saved_tickers import Stocks


# class for any functions related to the stock market
class StockMarket:
    def __init__(self, stock_manager, user):
        # load environment variables from .env file - specifically to get the api key
        # load_dotenv()
        self.api_key = "JM8zsFlJXYACHWl6qOYkMscHEAQ1FEmQ"

        # list of sectors in the stock market
        self.sectors = [
            "Technology",
            "Health Care",
            "Financials",
            "Consumer Discretionary",
            "Consumer Staples",
            "Energy",
            "Utilities",
            "Real Estate",
            "Materials",
            "Industrials",
            "Communication Services",
            "Information Technology",
            "Basic Materials",
            "Telecommunications",
            "Consumer Services"
        ]

        # list of exchanges that you can filter by
        self.exchanges = [
            "NASDAQ",
            "NYSE",
            "AMEX"
        ]
        self.user = user
        self.stock_manager = stock_manager

    # search stock market for company name's or tickers that contain keyword entered
    def nameSearch(self, keyword="", limit=None):
        url = f"https://financialmodelingprep.com/stable/search-symbol?query={keyword}&limit={limit}&apikey={self.api_key}"
        #listOfSearched = []
        response = requests.get(url)
        data = response.json()

        if not data:
            print("No results found")

        # for i, stock in enumerate(data):
        #     listOfSearched.append(stock['symbol'])
        #     print(f"Result: {i + 1}")
        #     print(f"Symbol: {stock['symbol']}")
        #     print(f"Name: {stock['name']}")
        #     print(f"Exchange: {stock['exchange']}\n")

        return data

    # More specific search for stocks that match sector, exchange, and market cap specified. Can also limit number of results given
    def advancedFilter(self, sector="", exchange="", mktCapMax=None, mktCapMin=None, limit=None):
        params = {
            "marketCapMoreThan": mktCapMin,
            "marketCapLowerThan": mktCapMax,
            "sector": sector,
            "exchange": exchange,
            "limit": limit
        }

        listOfSearched = []
        url = f"https://financialmodelingprep.com/stable/company-screener?apikey={self.api_key}"

        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            print("No results found")

        for i, stock in enumerate(data):
            listOfSearched.append(stock['symbol'])
            print(f"Result: {i + 1}")
            print(f"Symbol: {stock['symbol']}")
            print(f"Name: {stock['companyName']}")
            print(f"Market Cap: {stock['marketCap']}")
            print(f"Sector: {stock['sector']}")
            print(f"Price: {stock['price']}")
            print(f"Volume: {stock['volume']}")
            print(f"Exchange: {stock['exchange']}\n")

        return listOfSearched

    # get speicifc information on a stock
    def getStockInfo(self, ticker):
        news = Search(ticker)
        url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={self.api_key}"
        response = requests.get(url)
        stock = response.json()
        data = stock[0]

        print(f"Symbol: {data['symbol']}")
        print(f"Company Name: {data['companyName']}")
        print(f"Website: {data['website']}")
        print(f"Description: {data['description']}")
        print(f"Country: {data['country']}")
        print(f"Number of Full-Time Employees: {data['fullTimeEmployees']}")
        print(f"Price: {data['price']}")
        print(f"Market Cap: {data['marketCap']}")
        print(f"Beta: {data['beta']}")
        print(f"Last Dividend: {data['lastDividend']}")
        print(f"Range: {data['range']}")
        print(f"Change: {data['change']}")
        print(f"Change %: {data['changePercentage']}")
        print(f"Volume: {data['volume']}")
        print(f"Average Volume: {data['averageVolume']}")
        print(f"Currency: {data['currency']}")
        print(f"Sector: {data['sector']}")
        print(f"Industry: {data['industry']}")
        print(f"Exchange: {data['exchange']}\n")

        news.news_scrape()

        return data

    # method for stock market main menu
    def stockMain(self):
        session = StockMarket(self.stock_manager, self.user)
        print("Searching Stock Market...")
        print("Select one of the options below to begin: ")
        print(" 1. See Available Sectors")
        print(" 2. See Available Stock Exchanges to Filter By")
        print(" 3. Search By Ticker")
        print(" 4. Advanced Search Options")
        option = input("To proceed enter the option number: ")

        if option == "1" or option == "2":
            if option == "1":
                print("Here are a list of sectors:")
                for sector in session.sectors:
                    print(sector)
            else:
                print("Here is a list of stock exchanges that you can filter by:")
                for exchange in session.exchanges:
                    print(exchange)

            proceed = input("Would you like to continue (Y/N)?")
            if proceed == "Y" or proceed == "y":
                self.stockMain()
            else:
                pass
        elif option == "3" or option == "4":
            results = []
            if option == "3":
                keyword = input("Enter the Ticker: ")
                limit = input(
                    "If you want to limit the number of results enter a number (5 or below) or press enter to see all results.")
                try:
                    limit = int(limit)
                    if not 0 <= limit <= 5:
                        limit = None
                except:
                    limit = None
                results = session.nameSearch(keyword, limit)
            elif option == "4":
                print("Fill out the form below. If you do not want to specify an option then press enter.")
                sector = input("Enter the sector you would like to search: ")
                if sector not in session.sectors:
                    sector = ""
                exchange = input("Enter the exchange you would like to search: ")
                if exchange not in session.exchanges:
                    exchange = ""
                mktMaxCap = input("Enter the max market cap you would like to search: ")
                try:
                    mktMaxCap = int(mktMaxCap)
                except:
                    mktMaxCap = None
                mktMinCap = input("Enter the min market cap you would like to search: ")
                try:
                    mktMinCap = int(mktMinCap)
                except:
                    mktMinCap = None
                limit = input(
                    "If you want to limit the number of results enter a number (5 or below) or press enter to see all results.")
                try:
                    limit = int(limit)
                    if not 0 <= limit <= 5:
                        limit = None
                except:
                    limit = None
                results = session.advancedFilter(sector, exchange, mktMaxCap, mktMinCap, limit)
            print("What would you like to do next?")
            if not results:
                print("1. Go back to main menu")
                print("2. Quit")
                option = input("Type the option number you would like to do: ")
                if option == "1":
                    self.stockMain()
                else:
                    pass
            else:
                print("1. View more details on a stock listed")
                print("2. Go back to main menu")
                print("3. Quit")
                option = input("Type the option number you would like to do: ")
                if option == "1":
                    self.stockView(session, results)
                elif option == "2":
                    self.stockMain()
                else:
                    pass

    # method for viewing specific stock menu
    def stockView(self, session, stocks):
        stock = input("Enter the result number of the stock you want to view more information on: ")

        try:
            stock = int(stock)
            if 0 <= stock <= len(stocks):
                stockInfo = session.getStockInfo(stocks[stock - 1])
                print("\n What would you like to do now?")
                print("1. Save Stock")
                print("2. Search More Stocks")
                print("3. Quit")
                option = input("Enter the option number: ")
                if option == "1":
                    self.saveStock(stockInfo)
                elif option == "2":
                    self.stockMain()
                else:
                    pass
            else:
                print("Input is not valid. Try again")
                self.stockView(session, stocks)

        except:
            print("Input is not valid. Try again")
            self.stockView(session, stocks)

    def saveStock(self, stock):
        saved_stock = Stocks(self.stock_manager, self.user)
        saved_stock.save(stock["symbol"], stock["companyName"], stock["marketCap"], stock["description"])
        # stock will be dictionary in the form {'symbol': 'AAPL', 'price': 240.36, 'marketCap': 3610711956000, 'beta': 1.2, 'lastDividend': 1, 'range': '164.08-260.1', 'change': -6.68, 'changePercentage': -2.70402, 'volume': 0, 'averageVolume': 50169216, 'companyName': 'Apple Inc.', 'currency': 'USD', 'cik': '0000320193', 'isin': 'US0378331005', 'cusip': '037833100', 'exchangeFullName': 'NASDAQ Global Select', 'exchange': 'NASDAQ', 'industry': 'Consumer Electronics', 'website': 'https://www.apple.com', 'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, and HomePod. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts, as well as advertising services include third-party licensing arrangements and its own advertising platforms. In addition, the company offers various subscription-based services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV+, which offers exclusive original content; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers, wholesalers, retailers, and resellers. Apple Inc. was founded in 1976 and is headquartered in Cupertino, California.', 'ceo': 'Mr. Timothy D. Cook', 'sector': 'Technology', 'country': 'US', 'fullTimeEmployees': '150000', 'phone': '(408) 996-1010', 'address': 'One Apple Park Way', 'city': 'Cupertino', 'state': 'CA', 'zip': '95014', 'image': 'https://images.financialmodelingprep.com/symbol/AAPL.png', 'ipoDate': '1980-12-12', 'defaultImage': False, 'isEtf': False, 'isActivelyTrading': True, 'isAdr': False, 'isFund': False}


