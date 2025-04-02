import requests
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use Agg backend for non-interactive plots
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64

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

        # error handling
        if "data" not in data or not data["data"]:
            return None, "Invalid stock ticker, please try again."

        try:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
            df = df.sort_values(by="date")
        except Exception as e:
            return None, f"Error processing data: {str(e)}"
        else:
            plot_url = self.create_plot(df)
            return plot_url, None

    def create_plot(self, df):
        plt.figure(figsize=(10, 5))
        plt.plot(df["date"], df["close"], label="Closing Price", color="blue")
        plt.xlabel("Date")
        plt.ylabel("Closing Price (USD)")
        plt.title(f"{self.stock_symbol} Historical Stock Prices")
        plt.legend()
        plt.subplots_adjust(bottom=0.3)

        # base64-encoded image
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.clf()  # Clear the figure after saving it to avoid memory issues
        plt.close()  # Close the plot

        return plot_url
