api_key = "d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g"

import requests
url = f'https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2025-05-15&to=2025-06-20&token=d376tm1r01qtvbtkcj00d376tm1r01qtvbtkcj0g'

response = requests.get(url)

if response.status_code == 200:
    news_data = response.json()
   
 print(news_data)