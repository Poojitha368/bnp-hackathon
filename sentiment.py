import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import matplotlib.pyplot as plt
import numpy as np
import datetime

# --- 1. Fetch finance/business news from Finnhub ---
API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"  # <-- replace with real one
API_URL = "https://finnhub.io/api/v1/company-news"

today = datetime.date.today()
week_ago = today - datetime.timedelta(days=7)

params = {
    'symbol': 'AAPL',
    'from': str(week_ago),
    'to': str(today),
    'token': API_KEY
}

response = requests.get(API_URL, params=params)
data = response.json()

# Extract article summaries
texts = [article['summary'] for article in data if article.get('summary')]

if not texts:
    print("⚠ No news articles found for given symbol/date range.")
else:
    # --- 2. Load FinBERT model ---
    model_name = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

    # --- 3. Analyze sentiment ---
    results = sentiment_analyzer(texts)

    # --- 4. Print results ---
    for i, (text, res) in enumerate(zip(texts, results), 1):
        print(f"\nArticle {i}: {text}")
        print(f"Sentiment: {res['label']}, Confidence: {res['score']:.2f}")

    # --- 5. Plot line graph ---
    def sentiment_to_numeric(label):
        if label.lower() == 'negative': return 0
        if label.lower() == 'neutral': return 2.5
        if label.lower() == 'positive': return 5
        return 2.5

    numeric_scores = [sentiment_to_numeric(res['label']) for res in results]

    plt.figure(figsize=(12,6))
    x = np.arange(1, len(texts)+1)
    plt.plot(x, numeric_scores, marker='o', color='blue', linewidth=2)
    plt.xticks(x, [f"Article {i}" for i in x], rotation=45)
    plt.yticks([0,2.5,5], ['Negative','Neutral','Positive'])
    plt.title("Sentiment Line Graph for AAPL News")
    plt.xlabel("Articles")
    plt.ylabel("Sentiment Score (0-5)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()