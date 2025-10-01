'''We can only fetch data in this way 
https://finnhub.io/api/v1/company-news?symbol=SYMBOL&from=YYYY-MM-DD&to=YYYY-MM-DD&token=YOUR_API_KEY
'''
from datetime import datetime, timedelta
import requests

API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"
BASE_URL = "https://finnhub.io/api/v1/company-news"


def FetchDataViaApi(company):
    to_date = datetime.today()
    from_date = to_date - timedelta(days=7)
    params = {
        'symbol': company,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d'),
        'token': API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return f"Error fetching news for {company}: {response.status_code}"
    
    news_data = response.json()
    
    if not news_data:
        return "No news data found for the company last week"
    
    headlines = [record['headline'] for record in news_data]

    return headlines

    
    
