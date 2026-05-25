# Financial-News-Sentiment-Pipeline

An end-to-end Python pipeline that ingests financial news articles, stores them in a database, cleans and validates the data, runs sentiment analysis using FinBERT, and visualizes the results in an interactive dashboard.

Built as a portfolio project to demonstrate data engineering, NLP, and full-stack Python skills.

---

## Pipeline Overview

```
Finnhub API → DB (SQLite) → Cleaning & Validation → FinBERT → Dashboard (Streamlit)
```

| Stage | File | Status |
|---|---|---|
| Data Models | `models.py` | ✅ Complete |
| API Ingestion | `finnhub_ingest.py` | ✅ Complete |
| Database Layer | `db.py` | ✅ Complete |
| Cleaning & Validation | `cleaner.py` | ✅ Complete |
| FinBERT Sentiment | `sentiment.py` | 🔧 In Progress |
| Dashboard | `dashboard.py` | 🔧 In Progress |

---

## Tech Stack

- **Data Ingestion** — [Finnhub API](https://finnhub.io/)
- **Database** — SQLite
- **NLP / Sentiment** — [FinBERT](https://huggingface.co/ProsusAI/finbert) (HuggingFace Transformers)
- **Dashboard** — Streamlit
- **Core Libraries** — `requests`, `python-dotenv`

---

## Project Structure

```
financial-sentiment-pipeline/
│
├── models.py            # Shared Article dataclass used across all pipeline stages
├── finnhub_ingest.py    # Finnhub API ingestion — fetches news by ticker
├── db.py                # SQLite database layer (in progress)
├── cleaner.py           # Data cleaning and validation (in progress)
├── sentiment.py         # FinBERT sentiment analysis (planned)
├── dashboard.py         # Streamlit visualization dashboard (planned)
│
├── .env                 # API keys — never committed (see .gitignore)
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/HiddenProdige/financial-sentiment-pipeline.git
cd financial-sentiment-pipeline
```

### 2. Install dependencies

```bash
pip install requests python-dotenv 

```

### 3. Set up your API key

Create a `.env` file in the root directory:

```
FINNHUB_API_KEY=your_key_here
```

Get a free API key at [finnhub.io](https://finnhub.io). The free tier provides 60 requests/minute and a 30-day rolling news window.

### 4. Run the ingestion

```bash
python finnhub_ingest.py
```

This fetches recent news articles for the configured tickers and prints a summary to the terminal.

---

## Tickers Tracked

The pipeline currently tracks the following companies:

| Ticker | Company |
|---|---|
| AAPL | Apple |
| NVDA | NVIDIA |
| GOOGL | Alphabet (Google) |
| AMZN | Amazon |
| NFLX | Netflix |
| MSFT | Microsoft |
| IBM | IBM |
| META | Meta |
| SNOW | Snowflake |

---

## Design Decisions

**Why Finnhub over other APIs?**
Finnhub was chosen for its generous free tier (60 req/min), finance-specific news that is already ticker-linked, and built-in sentiment scores that can be benchmarked directly against FinBERT output — making the comparison a meaningful part of the dashboard.

**Why a shared `models.py`?**
The `Article` dataclass is defined once in `models.py` and imported by every stage of the pipeline. This avoids circular imports and ensures a consistent data shape regardless of the data the API returns.

**Why sequential requests with a delay?**
A 1-second sleep between ticker requests keeps the pipeline well within Finnhub's free rate limit. An `asyncio.Semaphore` approach is planned for the scraper stage if parallelism becomes necessary.

---

## Roadmap

- [x] `models.py` — shared Article dataclass
- [x] `finnhub_ingest.py` — Finnhub API ingestion
- [X] `db.py` — SQLite schema and insert/query layer
- [X] `cleaner.py` — deduplication, null checks, text normalization
- [ ] `sentiment.py` — FinBERT inference pipeline
- [ ] `dashboard.py` — Streamlit dashboard with sentiment trends by ticker

---

## Author

Built by [Sam Walker](https://github.com/HiddenProdige)  

