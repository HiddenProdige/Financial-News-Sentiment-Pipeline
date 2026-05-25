import streamlit as st
import pandas as pd
from collections import Counter
from sentiment import analyze_all, finbert
from cleaner import run_cleaner

# Page Configuration
st.set_page_config(
    page_title= "Financial Sentiment Dashboard",
    page_icon= "📈",
    layout= "wide"
)

# Cached data loader
@st.cache_data
def load_data() -> pd.DataFrame:
    # Runs the full pipleine once and caches the result
    # Streamlit will only re-run this function if the user manually clears the cache
    articles = run_cleaner()
    results = analyze_all(articles)
    return pd.DataFrame(results)

st.title("Financial News Sentiment Dashboard")
st.caption("Powered by Finnhub API + FinBERT")

with st.spinner("Running pipeline..."):
    df = load_data()

st.success(f"{len(df)} articles loaded and analyzed!")
# Pipeline Overview
st.header("Pipeline Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    label="Total Articles",
    value=len(df),
    )
col2.metric(
    label="Positive Sentiment",
    value= len(df[df['sentiment'] == 'positive']),
    delta= f"{len(df[df['sentiment'] == 'positive']) /len(df): .1%}",
    )

col3.metric(
    label="Negative Sentiment",
    value=len(df[df['sentiment'] == 'negative']),
    delta= f"{len(df[df['sentiment'] == 'negative']) /len(df): .1%}",
    delta_color="inverse", # Show negative changes in red
    )

col4.metric(
    label="Neutral Sentiment",
    value=len(df[df['sentiment'] == 'neutral']),
    delta= f"{len(df[df['sentiment'] == 'neutral']) /len(df): .1%}",
    delta_color="off", # Show neutral changes in gray
    )
# Sentiment Distribution Chart
st.header("Sentiment Distribution")

col_chart, colstats = st.columns([2, 1]) #Makes the chart take up 2 parts and the statistics take up 1 part of the available width
    
with col_chart:
    sentiment_counts = df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    import plotly.graph_objects as go       
    # Map of colors for each sentiment
    color_map = {
        "positive": "#2ecc71",
        "negative": "#e74c3c",
        "neutral": "#95a5a6"
        }
    # Plotly Chart due to a streamlit limitation
    fig = go.Figure(go.Bar(
        x= sentiment_counts['Sentiment'],
        y= sentiment_counts['Count'],
        marker_color= sentiment_counts['Sentiment'].map(color_map).tolist(),
        ))
    fig.update_layout(
        xaxis_title="Sentiment Distribution",
        yaxis_title="Article Count",
        showlegend= False,
        height= 350,
        )
    st.plotly_chart(fig, width= 'stretch')
    # Analysis of Confidence Scores
with colstats:
    st.subheader("Confidence Scores")
    avg_conf = df[["score_positive", "score_negative", "score_neutral"]].max(axis=1).mean()
    st.metric("Average Confidence", f"{avg_conf:.1%}")

    st.subheader("By Sentiment")
    for sentiment in ['positive', 'negative', 'neutral']:
        subset = df[df['sentiment'] == sentiment]
        if len(subset) > 0:
            avg = subset[["score_positive", "score_negative", "score_neutral"]].max(axis=1).mean()
            st.write(f"**{sentiment.capitalize()} :** {avg:.1%} average confidence")
# Ticker Breakdown
st.header("Sentiment by Ticker")
# Create a new dataframe with only the rows that have a ticker
ticker_df = df.dropna(subset=["ticker"])
        
ticker_sentiment = (
    ticker_df.groupby(["ticker", "sentiment"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
        )
for col in ["positive", "negative", "neutral"]:
        if col not in ticker_sentiment.columns:
            ticker_sentiment[col] = 0

ticker_sentiment = ticker_sentiment[[ "ticker", "positive", "negative", "neutral" ]]
st.dataframe(
        ticker_sentiment,
        width= 'stretch',
        hide_index=True
        )

# Article Explorer
st.header("Article Explorer")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
     sentiment_filter = st.multiselect(
          label="Filter by Sentiment",
          options=["positive", "negative", "neutral"],
          default=["positive", "negative", "neutral"]
     )
with col_f2:
     source_filter = st.multiselect(
          label="Filter by Source",
          options= sorted(df["author"].dropna().unique().tolist()),
          default= [],
     )
with col_f3:
     search = st.text_input(
          label= "Search Headlines",
          placeholder= "e.g. earnings, Fed, AI..."
     )
filtered = df[df["sentiment"].isin(sentiment_filter)]

if source_filter:
     filtered = filtered[filtered["author"].isin(source_filter)]

if search:
     filtered = filtered[ 
     filtered["headline"].str.contains(search, case=False, na=False)
     ]
st.caption(f"Showing {len(filtered)} of {len(df)} articles")
st.dataframe(
    filtered[["headline", "ticker", "sentiment", "score_positive", "score_negative", "score_neutral", "author", "published_at"]],
    width= 'stretch', 
    hide_index=True
)



                

