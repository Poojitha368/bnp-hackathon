from ImpactHeadlines import findImpactfulHeadlines
from ollamaModel import FindLLMResponse
import streamlit as st

def BuySellRecommendation(sentiment,Sentimentresults,headlines):
    posImpact,neuImpact,negImpact = findImpactfulHeadlines(Sentimentresults,headlines)
    prompt = f"""
        You are a financial analyst. Analyze the following sentiment data and headlines:

        overall Sentiment is {sentiment} 

        Top Positive Headlines:
        {chr(10).join(posImpact)}

        Top Negative Headlines:
        {chr(10).join(negImpact)}

        Top Neutral Headlines:
        {chr(10).join(neuImpact)}

        Task:
        1. Provide a short summary (strictly 1-2 sentences) justifying the overall sentiment with the help of mentioned impactful headlines(include what headlines effected in resulting the final sentiment).
        2. Give a final investment recommendation: BUY, SELL, or HOLD.
        Note: Dont mention any irrelevant sentence (like "Sure, I'd be happy to help!") for any introduction just give me the recommendation, generate only needed ones.
        """

    response = FindLLMResponse(prompt)
    st.subheader(response)
