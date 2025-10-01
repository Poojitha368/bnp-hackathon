from transformers import pipeline
from donutchart import createDonutChart
from LLMrecommendation import BuySellRecommendation
from concurrent.futures import ThreadPoolExecutor

pipe = pipeline("text-classification", model="ProsusAI/finbert")

def decideSentiment(texts):
    results = pipe(texts)
    return results

def FindSentiment(texts,company):
    pos_count,neu_count,neg_count = 0,0,0
    results = decideSentiment(texts)
    positive=0
    neutral=0
    negative=0
    sentiment = ""

    for text, result in zip(texts, results):
    # print(f"Text: {text}")
    # print(f"Sentiment: {result['label']}, Confidence: {result['score']:.4f}\n")
        if result['label'] == "positive":
            positive += result['score']
            pos_count += 1
        elif result['label'] == "negative":
            negative += result['score']
            neg_count += 1
        else:
            neutral += result['score']
            neu_count += 1

    if positive > negative and positive > neutral:
        sentiment = "positive"
    elif neutral > negative and neutral > positive:
        sentiment =  "neutral"
    else:
        sentiment = "negative"

    normalised_score = (positive-negative)/(positive+neutral+negative)
    # print(normalised_score)
    final_score = ( (normalised_score+1)/2 *4)+1

    with ThreadPoolExecutor(max_workers=2) as executor:

        #donut chart for the pos,neu,neg ratio
        executor.submit(createDonutChart(sentiment,pos_count,neu_count,neg_count,final_score,company))
        #buy sell recommendation using llm
        executor.submit(BuySellRecommendation(sentiment,results,texts))

    return sentiment,pos_count,neu_count,neg_count,final_score


