from wordcloud import WordCloud
from collections import Counter



def wordCloudImage(headlines):
    words = [w for h in headlines for w in h.split() if w.isalnum()]
    freqs = Counter(words)
    wordcloud = WordCloud(width=400, height=300, background_color="white").generate_from_frequencies(freqs)
    return wordcloud.to_image()

    