import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from models import Article #Calls a custom class for the correct organization of data for storage and finiancial analysis

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY") 
BASE_URL = "https://finnhub.io/api/v1/company-news"
TICKERS = ["AAPL", "NVDA", "GOOGL", "AMZN", "NFLX", "MSFT", "IBM", "META", "SNOW"]


#This Function scrapes and converts all of the raw data from the API to the Article Class
def parse_article (raw: dict) -> Article:
    return Article(
        url= raw.get("url", ""),
        headline= raw.get("headline", ""),
        body= raw.get("summary", ""),   #Body of text used for analysis
        author= raw.get("source"),  #Finnhub only gives source
        published_at= datetime.utcfromtimestamp(
                        raw["datetime"]
                      ).isoformat() if raw.get("datetime") else None, #Converts the standard UTC time to an ISO String
        section= raw.get("category"),
    )

#This Function is for single-ticker scraping
def fetch_news(symbol: str, from_date: str, to_date: str) -> list[Article]:
    params = {
    "symbol": symbol,
    "from":   from_date,
    "to":     to_date,
    "token":  API_KEY,
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status() #Raises Alarm for HTTP Errors
    return [parse_article(item) for item in response.json()]

#This Function is for multi-ticker scraping
def fetch_all(tickers: list[str], from_date: str, to_date: str) -> list[Article]:
    all_articles = []
    for ticker in tickers:
        print(f"[INFO] Fetching {ticker}...")
        try:    #Try/Except so the entire code doesn't break due to one ticker information mishap   
            articles = fetch_news(ticker, from_date, to_date)
            print(f"    Got {len(articles)} articles")
            all_articles.extend(articles)
        except Exception as e:
            print(f"[ERROR] {ticker} failed: {e}")
        time.sleep(1) #To not go over the 60 calls per minute threshold
    return all_articles


#Developer Test Block to make sure single-ticker data is valid
# if __name__ == "__main__":
#     articles = fetch_news("SNOW", "2025-07-01", "2025-08-17")
#     print(f"Got {len(articles)} articles")
#     print(articles[0])


#Developer Test Block to make sure multi-ticker data is valid
if __name__ == "__main__":
    results = fetch_all(
        tickers= TICKERS,
        from_date= "2025-07-01",
        to_date= "2025-08-17",
    )
    print(f"\n Total articles fetched: {len(results)}")
    for a in results[:3]:
        print(f"\nHeadline : {a.headline}")
        print(f"Source : {a.author}")
        print(f"Date : {a.published_at}")
        print(f"Summary : {a.body[:100]}...")