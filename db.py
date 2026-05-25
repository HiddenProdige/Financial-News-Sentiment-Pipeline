import sqlite3
import os
from models import Article

# Ensures the database file is created in the same directory as this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "articles.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name instead of by indexing
    return conn


# Creates the articles table if it doesn't already exist.Safe to call every time the app starts.
def create_table(conn: sqlite3.Connection) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS articles (
                 url TEXT PRIMARY KEY,
                 headline TEXT NOT NULL,
                 body TEXT,
                 author TEXT,
                 published_at TEXT,
                 section TEXT,
                 scraped_at TEXT
                 )
    ''')
    conn.commit()
    print("Table created")

#Inserts a list of Article objects into the database
def insert_articles(conn: sqlite3.Connection, articles: list[Article]) -> None:
    inserted = 0
    skipped = 0
# Iterate through the list of articles and insert each one into the database and  it will be skipped if it already exists
    for article in articles:
        try:
            conn.execute('''
                INSERT OR IGNORE INTO articles 
                    (url, headline, body, author, published_at, scraped_at)
                VALUES 
                    (?, ?, ?, ?, ?, ?)
            ''', (article.url, 
                  article.headline, 
                  article.body, 
                  article.author, 
                  article.published_at, 
                  article.scraped_at))
            if conn.total_changes > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"[ERROR] Failed to insert {article.url}: {e}")

    conn.commit()
    print(f"Inserted {inserted} articles, skipped {skipped} articles.")

# Fetches all articles from the database
def get_all_articles(conn: sqlite3.Connection) -> list[Article]:
    cursor = conn.execute('SELECT * FROM articles')
    return cursor.fetchall()

# Prevents the code from running if the script is imported (i.e do not run automatically when imported)
if __name__ == "__main__":
    from finnhub_ingest import fetch_all
    conn = get_db_connection()
    create_table(conn)
    articles = fetch_all(
        tickers=["AAPL", "NVDA"],
        from_date="2025-07-01",
        to_date="2025-08-17"
    )
    # Inserts the fetched articles into the database
    conn = get_db_connection()
    rows = get_all_articles(conn)
    create_table(conn)
    insert_articles(conn, articles)
    print(f"Total articles in database: {len(rows)}")
    print(f"Sample: {rows[0]['headline']}") # Test Article
    conn.close()
