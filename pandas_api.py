import requests
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

INTERVAL = "month"
DATE_TO = datetime.today().strftime("%Y-%m-%d")
DATE_FROM = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")


class Graphs:
    def __init__(self, stock_symbol):
        self.api_key = "hgVAQPj8NKeoMoaXKyVjI9cqontuWz18p7nGcsKj"
        self.stock_symbol = stock_symbol.strip().upper()
        self.url = (
            f"https://api.stockdata.org/v1/data/eod"
            f"?symbols={self.stock_symbol}"
            f"&api_token={self.api_key}"
            f"&interval={INTERVAL}"
            f"&date_from={DATE_FROM}"
            f"&date_to={DATE_TO}"
            f"&sort=asc"
        )

    def get_graph(self):
        response = requests.get(self.url)
        data = response.json()
        try:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            df = df.sort_values(by="date")
        except:
            print("Data not available on the stock ticker you have inputted, please try another stock")
        else:
            #unable to display past twelve months as latest data from API is from 2024-08-28
            plt.figure(figsize=(12, 6))
            plt.plot(df["date"], df["close"], label="Closing Price", color="blue")
            plt.xlabel("Date")
            plt.ylabel("Closing Price (USD)")
            plt.title(f"{self.stock_symbol} Historical Stock Prices")
            plt.show()
