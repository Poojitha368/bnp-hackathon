import pandas as pd
def findImpactfulHeadlines(Sentimentresults,headlines,top_n=5):
    df = pd.DataFrame({
        "headline":headlines,
        "label":[r["label"] for r in Sentimentresults],
        "score":[r["score"] for r in Sentimentresults]
    })

    posImpact = df[df["label"] == "positive"].nlargest(top_n,"score")["headline"].tolist()
    neuImpact = df[df["label"] == "neutral"].nlargest(top_n,"score")["headline"].tolist()
    negImpact = df[df["label"] == "negative"].nlargest(top_n,"score")["headline"].tolist()


    return posImpact,neuImpact,negImpact