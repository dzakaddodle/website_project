import requests
from bs4 import BeautifulSoup


class Search:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.url = f'https://finviz.com/quote.ashx?t={self.ticker}&p=d'
        self.soup = self.get_soup()

    def get_soup(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.url, headers=headers)
        return BeautifulSoup(response.content, 'html.parser')

    def news_scrape(self):
        news_data = []
        try:
            table = self.soup.find('table', class_='fullview-news-outer')
            rows = table.find_all('tr')

            for row in rows[:50]:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue

                timestamp = cols[0].text.strip()
                link_tag = cols[1].find('a')
                if link_tag:
                    title = link_tag.text.strip()
                    url = link_tag['href']
                    if url.startswith('/'):
                        url = f'https://www.finviz.com{url}'

                    news_data.append({
                        'title': title,
                        'url': url,
                        'timestamp': timestamp,
                        'ticker': self.ticker
                    })

        except Exception as e:
            print(f"Error scraping news for {self.ticker}: {e}")

        return news_data