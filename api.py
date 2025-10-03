'''We can only fetch data in this way 
https://finnhub.io/api/v1/company-news?symbol=SYMBOL&from=YYYY-MM-DD&to=YYYY-MM-DD&token=YOUR_API_KEY
'''
from datetime import datetime, timedelta
import requests

API_KEY = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"
BASE_URL = "https://finnhub.io/api/v1/company-news"


def FetchDataViaApi(company):
    def getHeadlines(days):
        to_date = datetime.today()
        from_date = to_date - timedelta(days=days)
        params = {
            'description': company,
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'token': API_KEY
        }

        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            return f"Error fetching news for {company}: {response.status_code}"
        
        news_data = response.json()
        
        headlines = [record['headline'] for record in news_data]


        return headlines
    

    #try for 7 days
    headlines = getHeadlines(7)
    if not headlines:
        # if no data for 7 days then try for last 30 days
        headlines = getHeadlines(30)
    
    return headlines

    
    
