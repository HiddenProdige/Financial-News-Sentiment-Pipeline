import re
import sqlite3
from models import Article
from db import get_db_connection, get_all_articles

# Loads all articles from the database
def load_articles() -> list[sqlite3.Row]:
    conn = get_db_connection()
    articles = get_all_articles(conn)
    conn.close()
    print(f"[INFO] Loaded {len(articles)} articles from the database.")
    return articles

# Removes duplicate articles based on their headlines
def deduplicate(articles: list[sqlite3.Row]) -> list[sqlite3.Row]:
    seen_headlines = set()
    unique = []
    for article in articles:
        headline = article['headline'].strip().lower() # To normalize the casing for every headline to ensure consistent comparison
        if article['headline'] not in seen_headlines:
            seen_headlines.add(headline)
            unique.append(article)
    removed = len(articles) - len(unique)
    print(f"[INFO] Deduplicated: {removed} duplicate articles removed | {len(unique)} articles remaining.")
    return unique

# Filters out articles with invalid or missing data
def filter_invalid(articles: list[sqlite3.Row]) -> list[sqlite3.Row]:
    valid = []
    # Checks if the article has a valid body
    for article in articles:
        body = article["body"]
        if body and body.strip():
            valid.append(article)

    removed = len(articles) - len(valid)
    print(f"[INFO] Filtered out {removed} | {len(valid)} remaining")
    return valid

# Normalizes text by removing extra whitespace and non-ASCII characters
def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text) # Replaces multiple whitespace characters with a single space
    text = re.sub(r"[^\x00-\x7F]", "", text) # Removes non-ASCII characters
    return text

# Applies text normalization to headlines, body, author, and section of every article
def normalize_article(articles: sqlite3.Row) -> list[dict]: #Switched from sqlite3.Row to list[dict] to be able to  fully modify the data
    normalized = []
    for article in articles:
        normalized.append({
            "url": article["url"],
            "headline": normalize_text(article["headline"]),
            "body": normalize_text(article["body"]),
            "author": normalize_text(article["author"]) if article["author"] else None, # Handles missing authors aka null values
            "published_at": article["published_at"],
            "section": normalize_text(article["section"]) if article["section"] and article["section"].strip() else None,
            "scraped_at": article["scraped_at"],
        })
    print(f"[INFO] Normalized {len(normalized)} articles.")
    return normalized

# Filters out articles with bodies too short to be meaningful for analysis
MIN_BODY_LENGTH = 100
def filter_too_short(articles: list[dict]) -> list[dict]:
    valid = []
    valid = [ a for a in articles if len(a["body"]) >= MIN_BODY_LENGTH ]
    removed = len(articles) - len(valid)
    print(f"[INFO] Filtered out {removed} articles with bodies shorter than {MIN_BODY_LENGTH} characters. {len(valid)} articles remaining.")
    return valid

# Full cleaning pipeline
def run_cleaner() -> list[dict]:
    articles = load_articles()
    articles = deduplicate(articles)
    articles = filter_invalid(articles)
    articles = normalize_article(articles)
    articles = filter_too_short(articles)

    print(f"\n[INFO] Cleaning complete - {len(articles)} articles are ready for FinBERT.")
    return articles

if __name__ == "__main__":
    clean_articles = run_cleaner()

  