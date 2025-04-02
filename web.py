import requests
from bs4 import BeautifulSoup


class Search:
    def __init__(self, ticker):
        self.ticker = ticker.lower()
        self.url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'
        self.soup = self.get_soup()

    def get_soup(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def get_news(self, tagname, classname):
        result = []
        for each in self.soup.find_all(tagname, class_=classname):
            result.append(each.text.strip())
        return result

    def news_scrape(self):
        news = self.get_news('a', 'tab-link-news')
        if news:
            print(f'RECENT NEWS HEADLINES FOR {self.ticker.upper()}')
            for i, headline in enumerate(news[:20], 1):
                print(f'{i}. {headline}')
        else:
            print(f'No news found for {self.ticker}')
