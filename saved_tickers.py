import csv


class Stocks:
    def __init__(self, stock_manager, user):
        self.stock_manager = stock_manager
        self.user_email = user.email

    def save(self, ticker, name, market_cap, description, ):
        self.stock_manager.save_stock(ticker, name, market_cap, description, self.user_email)

    def delete(self, ticker):
        self.stock_manager.delete_stock(ticker, self.user_email)

    def view_saved_stocks(self):
        print(self.user_email)
        stock_list = self.stock_manager.see_saved_stocks(self.user_email)
        for n, stock in enumerate(stock_list):
            print(f"{n+1}. {stock[1]}, {stock[0]}")
            print(f"Market Cap: {stock[2]}")
            print(f"Description: {stock[3]}")
            print("\n")
        return stock_list

    def export_to_csv(self):
        with open('saved_stocks.csv', mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Ticker", "Company Name", "Market Cap", "Description"])
            stocks = self.stock_manager.see_saved_stocks(self.user_email)
            writer.writerows(stocks)

        print("Stocks exported successfully!")
