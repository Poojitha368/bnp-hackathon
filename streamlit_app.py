import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- NLTK VADER Setup ---
nltk.download('vader_lexicon')
sid = SentimentIntensityAnalyzer()

# --- MongoDB connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client['finnhub_news_db']
news_collection = db['company_news']
sentiment_collection = db['company_sentiment']

# --- Finnhub API ---
API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"
BASE_URL = "https://finnhub.io/api/v1/company-news"

# --- Fetch & store news with structured date fields ---
def fetch_and_store_news(symbol, days_back=7):
    to_date = datetime.today()
    from_date = to_date - timedelta(days=days_back)

    params = {
        'symbol': symbol,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'token': API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        st.error(f"Error fetching news for {symbol}: {response.status_code}")
        return pd.DataFrame()

    news_list = response.json()
    docs = []
    for news in news_list:
        news_datetime = datetime.fromtimestamp(news.get('datetime')) if news.get('datetime') else None
        if news_datetime:
            docs.append({
                'company': symbol,
                'headline': news.get('headline'),
                'source': news.get('source'),
                'url': news.get('url'),
                'datetime': news_datetime,
                'day': news_datetime.day,
                'month': news_datetime.month,
                'year': news_datetime.year,
                'weekday': news_datetime.strftime('%A')
            })

    if docs:
        # Replace old news
        news_collection.delete_many({"company": symbol})
        news_collection.insert_many(docs)

    return pd.DataFrame(docs)

# --- Sentiment score 0-5 ---
def sentiment_score(text):
    compound = sid.polarity_scores(text)['compound']  # -1 to +1
    scaled = ((compound + 1) / 2) * 5                # scale 0-5
    return round(scaled, 2)

# --- Process sentiment and store ---
def process_sentiment(symbol, period="day"):
    cursor = news_collection.find({"company": symbol})
    df = pd.DataFrame(list(cursor))
    if df.empty:
        return pd.DataFrame()

    df['sentiment_score'] = df['headline'].apply(sentiment_score)

    # Aggregate based on period
    if period == "day":
        grouped = df.groupby(df['datetime'].dt.date)['sentiment_score'].mean()
    elif period == "week":
        grouped = df.groupby('weekday')['sentiment_score'].mean()
    elif period == "month":
        grouped = df.groupby('month')['sentiment_score'].mean()
    elif period == "year":
        grouped = df.groupby('year')['sentiment_score'].mean()
    else:
        grouped = df['sentiment_score']

    # Replace old sentiment
    sentiment_collection.delete_many({"company": symbol, "period": period})

    docs = []
    for date, score in grouped.items():
        docs.append({
            "company": symbol,
            "period": period,
            "date": str(date),
            "avg_sentiment_score": round(score, 2)
        })
    if docs:
        sentiment_collection.insert_many(docs)

    return pd.DataFrame(docs)

# --- Streamlit Dashboard ---
st.set_page_config(layout="wide")
st.title("📊 Stock Sentiment Dashboard (0-5)")

companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "NFLX", "DIS"]

# Automatically fetch, store, and process sentiment
for company in companies:
    fetch_and_store_news(company, days_back=7)
    process_sentiment(company, period="day")
    process_sentiment(company, period="week")
    process_sentiment(company, period="month")
    process_sentiment(company, period="year")

# --- Company selection and period filter ---
company = st.selectbox("Select Company", companies)
period = st.radio("Select Period", ["day", "week", "month", "year"], horizontal=True)

# --- Fetch sentiment data ---
cursor = sentiment_collection.find({"company": company, "period": period})
df_sentiment = pd.DataFrame(list(cursor)).sort_values("date") if cursor else pd.DataFrame()

# --- Fetch latest news ---
cursor_news = news_collection.find({"company": company}).sort("datetime", -1).limit(20)
df_news = pd.DataFrame(list(cursor_news))

# --- Layout: Donut Chart + WordCloud + Trend ---
col1, col2, col3 = st.columns([1,1,2])

# --- Column 1: Donut Chart ---
# --- Column 1: Sentiment Distribution ---
# --- Column 1: Sentiment Distribution ---
with col1:
    st.subheader("📊 Sentiment Distribution")
    if not df_news.empty:
        # Compute sentiment for each headline
        df_news['sentiment_score'] = df_news['headline'].apply(sentiment_score)

        # Filter based on selected period
        today = datetime.today()
        if period == "day":
            from_date = today - timedelta(days=1)
        elif period == "week":
            from_date = today - timedelta(days=7)
        elif period == "month":
            from_date = today - timedelta(days=30)
        elif period == "year":
            from_date = today - timedelta(days=365)

        df_filtered = df_news[df_news['datetime'] >= from_date]

        # Count headlines by sentiment
        pos_count = df_filtered[df_filtered['sentiment_score'] > 3].shape[0]
        neu_count = df_filtered[(df_filtered['sentiment_score'] >= 2) & (df_filtered['sentiment_score'] <= 3)].shape[0]
        neg_count = df_filtered[df_filtered['sentiment_score'] < 2].shape[0]

        total_headlines = len(df_filtered)

        # Donut chart
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [pos_count, neu_count, neg_count]
        colors = ['green', 'yellow', 'red']

        fig1, ax1 = plt.subplots()
        wedges, texts, autotexts = ax1.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90
        )
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.axis('equal')

        # Add total in the center of the donut
        plt.text(0, 0, f"{total_headlines}\nTotal", ha='center', va='center', fontsize=12, fontweight='bold')

        st.pyplot(fig)

        # Show counts breakdown
        st.markdown(f"### 📰 Total Headlines: **{total_headlines}**")
        st.markdown(f"- ✅ Positive: **{pos_count}**")
        st.markdown(f"- 😐 Neutral: **{neu_count}**")
        st.markdown(f"- ❌ Negative: **{neg_count}**")
    else:
        st.warning("No sentiment data available.")



# --- Column 2: Word Cloud ---
with col2:
    st.subheader("☁️ Word Cloud of Headlines")
    if not df_news.empty:
        text = " ".join(df_news['headline'].dropna())
        wc = WordCloud(width=400, height=400, background_color="white").generate(text)
        fig_wc, ax_wc = plt.subplots()
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)
    else:
        st.warning("No news to generate word cloud.")

# --- Column 3: Sentiment Trend ---
with col3:
    st.subheader("📈 Sentiment Trend")
    if not df_sentiment.empty:
        st.line_chart(df_sentiment.set_index("date")["avg_sentiment_score"])
        st.dataframe(df_sentiment)
    else:
        st.warning("No sentiment data to show trend.")

# # --- Latest News Table ---
# st.subheader("📰 Latest News")
# if not df_news.empty:
#     st.dataframe(df_news[['datetime', 'headline', 'source', 'url']])
# else:
#     st.warning("No news found.")

# gemini api key : AIzaSyAUtK59EUEclp9nlbsVP7iIcZpRkvLuENc

# --- Gemini API ---

