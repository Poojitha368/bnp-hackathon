from flask import Flask
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/")  # default local MongoDB
    print("Connected to MongoDB!")
    db = client['finnhub_news_db']
    collection = db['company_news']
except Exception as e:
    print("Could not connect to MongoDB:", e)


# 2. Finnhub API setup
API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"
BASE_URL = "https://finnhub.io/api/v1/company-news"

# 3. Function to fetch news for a company
def fetch_company_news(symbol, days_back=7):
    to_date = datetime.today()
    from_date = to_date - timedelta(days=days_back)
    
    params = {
        'symbol': symbol,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'token': API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        news_list = response.json()
        # Prepare documents for MongoDB
        docs = []
        for news in news_list:
            docs.append({
                'company': symbol,
                'headline': news.get('headline'),
                'source': news.get('source'),
                'url': news.get('url'),
                'datetime': datetime.fromtimestamp(news.get('datetime'))
            })
        return docs
    else:
        print(f"Error fetching news for {symbol}: {response.status_code}")
        return []

# 4. Insert news into MongoDB
def store_news_in_db(symbol):
    news_docs = fetch_company_news(symbol)
    if news_docs:
        collection.insert_many(news_docs)
        print(f"Inserted {len(news_docs)} news items for {symbol}")
    else:
        print(f"No news found for {symbol}")

# Example usage
companies = ["AAPL", "MSFT", "GOOGL"]

for company in companies:
    store_news_in_db(company)



@app.route('/')
def home():
    return "hello flask"

if __name__ == '__main__':
    app.run(debug=True)