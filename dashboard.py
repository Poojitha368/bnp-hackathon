import streamlit as st
import threading
from sentiment import FindSentiment
from api import FetchDataViaApi
from GenerateWordCloud import wordCloudImage
from FindCompanies import FetchCompanies
# from LLMrecommendation import BuySellRecommendation


st.set_page_config(
    page_title="Market Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.title("📈 Real-Time Market Sentiment Dashboard")

#selection of companies
st.header("Choose a Company")
# companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "NFLX", "DIS"]
companies = FetchCompanies()
search = st.text_input("search a company")
filtered = [company for company in companies if search.lower() in company.lower()]

company = st.selectbox("Matching Companies", filtered) if filtered else None

if company:
    st.write(f"You selected {company}")


#fetching news data via finhubb api
headlines = FetchDataViaApi(company)
# headlines = [
#     "Apple internally weighs bid for ChatGPT rival Perplexity, Bloomberg says",
#     "Apple (AAPL) Rises As Market Takes a Dip: Key Facts",
#     "Apple executives held internal talks about buying Perplexity, Bloomberg News reports",
#     "Stocks Settle Mostly Lower as Chip Makers Fall"
# ]

#using threading for simultaneous execution
if headlines:
    
    #finding the sentiment scores
    sentiment,pos_count,neu_count,neg_count,final_score = FindSentiment(headlines,company)
    st.write("The sentiment score for ",company," out of 5 is ",final_score)

    #count of headlines(postive,negative and neutral count)
    st.markdown(f"### 📰 Total Headlines: **{len(headlines)}**")
    st.markdown(f"- ✅ Positive: **{pos_count}**")
    st.markdown(f"- 😐 Neutral: **{neu_count}**")
    st.markdown(f"- ❌ Negative: **{neg_count}**")
    st.markdown(f"The overall sentiment is **{sentiment}**")


    #wordcloud
    wcImage = wordCloudImage(headlines)
    st.image(wcImage)

    # News gathers from various sources
    st.subheader("News gatherings from various sources")
    newsGathers = headlines[:5]
    news_text = "\n\n".join(newsGathers)
    if news_text:
        st.write(news_text)
    else:
        st.write("No news to show")

    

    














    #initialize the threads
     # Create threads
    thread1 = threading.Thread(target=FindSentiment)
    thread2 = threading.Thread(target=wordCloudImage)
    
    # Start all simultaneously
    thread1.start()
    thread2.start()
    
    # Wait for completion
    thread1.join()
    thread2.join()

