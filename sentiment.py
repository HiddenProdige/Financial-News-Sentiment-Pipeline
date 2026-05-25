from transformers import pipeline
from cleaner import run_cleaner

#Loads the FinBERT model from the Hugging Face model hub, caching it locally
print("[INFO] Loading FinBERT model...")
finbert = pipeline(
    task= "text-classification",
    model= "ProsusAI/finbert",
    top_k= None, # Returns all 3 scores (positive, negative, neutral)
)
print("[INFO] FinBERT model loaded successfully!")

if __name__ == "__main__":
    print("Model is ready for use.")

#Sentiment analysis function
def analyze_article(article: dict) -> dict:
    body = article["body"][:512]
    results = finbert(body)[0]
    scores = {r["label"]: round(r["score"], 4) for r in results}
    return {
        **article,
        "sentiment":      max(scores, key=scores.get),
        "score_positive": scores.get("positive", 0),
        "score_negative": scores.get("negative", 0),
        "score_neutral":  scores.get("neutral",  0),
    }

# Analyzes the sentiment of a single article
def analyze_single(ticker: str, from_date: str, to_date: str) -> dict:
    from finnhub_ingest import fetch_news
    articles = fetch_news(ticker, from_date, to_date)
    print(f"[INFO] Analyzing {len(articles)} articles for {ticker}")
    for article in articles[:5]:    # preview first 5
        result = analyze_article(article.__dict__ if hasattr(article, '__dict__') else article)
        print(f"\n  Headline  : {result['headline']}")
        print(f"  Sentiment : {result['sentiment']}")
        print(f"  Confidence: {max(result['score_positive'], result['score_negative'], result['score_neutral']):.2%}")


# Analyzes the sentiment of all extracted articles
def analyze_all(articles: list[dict]) -> list[dict]:
    
    results = []

    for i, article in enumerate(articles, 1):
        try: 
            enriched = analyze_article(article)
            results.append(enriched)
        except Exception as e:
            print(f"[ERROR] Failed to process article {i}: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to process article {i}: {e}")
        if i % 50 == 0:
                print(f"[INFO] Processed {i}/{len(articles)} articles...")

    print(f"\nSentiment analysis complete. Processed {len(results)}/{len(articles)} articles.")
    return results

# Prints the sentiment analysis of a single or all articles
if __name__ == "__main__":
    mode = "full"
# Mode can be "single" or "full"
    if mode == "single":
        analyze_single(
            ticker="NVDA", 
            from_date="2025-07-01", 
            to_date="2025-08-17",
            )
    else:
        articles = run_cleaner()
        results = analyze_all(articles)

        from collections import Counter
        distribution = Counter(r['sentiment'] for r in results)
        total = len(results)
        print(f"\nSentiment distribution:")
        print(f"  Positive : {distribution['positive']} ({distribution['positive']/total:.1%})")
        print(f"  Negative : {distribution['negative']} ({distribution['negative']/total:.1%})")
        print(f"  Neutral  : {distribution['neutral']} ({distribution['neutral']/total:.1%})")
        # Sample Results
        print(f"\nSample Results:")
        for r in results[:3]:  # Print the first 3 results as a sample
            print(f" Headline: {r['headline']}")
            print(f" Sentiment: {r['sentiment']}")
            print(f" Confidence: {max(r['score_positive'], r['score_negative'], r['score_neutral']): .2%}")
     
