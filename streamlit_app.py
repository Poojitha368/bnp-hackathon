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
with col1:
    st.subheader("📊 Sentiment Distribution")
    if not df_sentiment.empty:
        pos_count = df_sentiment[df_sentiment['avg_sentiment_score'] > 3]['avg_sentiment_score'].count()
        neu_count = df_sentiment[(df_sentiment['avg_sentiment_score'] >= 2) & (df_sentiment['avg_sentiment_score'] <= 3)]['avg_sentiment_score'].count()
        neg_count = df_sentiment[df_sentiment['avg_sentiment_score'] < 2]['avg_sentiment_score'].count()

        labels = ['Positive (BUY)', 'Neutral (HOLD)', 'Negative (SELL)']
        sizes = [pos_count, neu_count, neg_count]
        colors = ['green', 'yellow', 'red']

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.axis('equal')
        st.pyplot(fig)

        # Latest recommendation
        latest_score = df_sentiment['avg_sentiment_score'].iloc[-1]
        if latest_score >= 3.5:
            rec = "BUY"
        elif latest_score >= 2.0:
            rec = "HOLD"
        else:
            rec = "SELL"
        st.markdown(f"### 💡 Latest Recommendation: **{rec}** (Score: {latest_score}/5)")
    else:
        st.warning("No sentiment data for donut chart.")

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

# --- Latest News Table ---
st.subheader("📰 Latest News")
if not df_news.empty:
    st.dataframe(df_news[['datetime', 'headline', 'source', 'url']])
else:
    st.warning("No news found.")


# gemini api key : AIzaSyAUtK59EUEclp9nlbsVP7iIcZpRkvLuENc

# --- Gemini API ---
GEMINI_API_KEY = "AIzaSyAUtK59EUEclp9nlbsVP7iIcZpRkvLuENc"
GEMINI_API_URL = "https://api.gemini.com/v1/ai/generate"  # replace with actual endpoint


def analyze_factors_and_recommendation(headlines, final_score):
    # ... prepare the prompt ...

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("text", "No response from Gemini API.")
    except Exception as e:
        return f"Gemini API error: {e}"



st.subheader("🤖 Analyze Factors & Recommendation (30 Days)")

if st.button("Analyze Sentiment Factors & Get Recommendation"):
    to_date = datetime.today()
    from_date = to_date - timedelta(days=30)

    # Fetch last 30 days headlines
    cursor_news_30 = news_collection.find({
        "company": company,
        "datetime": {"$gte": from_date, "$lte": to_date}
    }).sort("datetime", 1)
    headlines_last30 = [news['headline'] for news in cursor_news_30]

    # Compute final sentiment score over last 30 days
    cursor_sentiment_30 = sentiment_collection.find({
        "company": company,
        "period": "day",
        "date": {"$gte": str(from_date.date()), "$lte": str(to_date.date())}
    })
    sentiments_last30 = [s['avg_sentiment_score'] for s in cursor_sentiment_30]
    final_score = round(sum(sentiments_last30)/len(sentiments_last30), 2) if sentiments_last30 else None

    # Call Gemini LLM
    llm_analysis = analyze_factors_and_recommendation(headlines_last30, final_score)
    
    # Display the LLM analysis
    st.markdown("### 📄 LLM Analysis of Factors Affecting Sentiment")
    st.markdown(llm_analysis)

    # Optional: show headlines in collapsible container
    with st.expander("Show Headlines Affecting Sentiment"):
        for h in headlines_last30:
            st.write(f"- {h}")

    # --- Extract and show recommendation separately ---
    if llm_analysis:
        # Simple heuristic: look for BUY/HOLD/SELL in the text
        llm_text_upper = llm_analysis.upper()
        if "BUY" in llm_text_upper:
            rec_text = "BUY"
        elif "HOLD" in llm_text_upper:
            rec_text = "HOLD"
        elif "SELL" in llm_text_upper:
            rec_text = "SELL"
        else:
            rec_text = "No clear recommendation from LLM"

        st.markdown(f"### 💡 Overall Recommendation: **{rec_text}**")

