import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud

st.set_page_config(page_title="Dashboard Demo", layout="wide")

# Dummy data setup
mentions_data = [900, 1200, 1100, 1300, 800, 950, 1400]
date_labels = ["Aug 21", "Aug 23", "Aug 25", "Aug 18", "Aug 15", "Aug 22", "Aug 19"]
sentiment = {"Positive": 39.3, "Negative": 13.3}

language = {
    "English": 74.6,
    "Swedish": 14.4,
    "German": 4.8,
    "Afrikaans": 0.4,
    "Dutch": 0.8
}

sources = {
    "Twitter": 92.9,
    "News/blogs": 5.4,
    "Reddit": 1.5,
    "YouTube": 0.2
}

gender = {
    "Male": 62.7,
    "Female": 37.3
}

mentions_table = pd.DataFrame({
    "Title": ["Wikipedia", "Futurists Club", "JayZ Investment", "Oatly Hopes", "LPiate Vegan"],
    "Snippet": [
        "Oatly assessed - Quality rating changed...",
        "A Swedish oat company mentioned...",
        "Oatly gets the rap star treatment...",
        "Oatly hopes for frothy IPO market...",
        "Single cream SJL for vegan audience..."
    ]
})


mentions = [
    {
        "icon": "🌐",
        "title": "Wikipedia:Version 1.0 Editorial Team/Food and drink",
        "description": "Oatly reassessed. Quality rating changed from Stub-Class to Start-Class.",
        "link": "https://en.wikipedia.org/"
    },
    {
        "icon": "📰",
        "title": "What the plant?! - Futurists Club Team - Medium",
        "description": "A Swedish oat company who powered up its production by 1250%.",
        "link": "https://medium.com/"
    },
    {
        "icon": "💬",
        "title": "Oat milk gets the rap star treatment as JayZ invests",
        "description": "Oatly is provided by This Is Money. An alternative to cow's milk.",
        "link": "https://thisismoney.co.uk/"
    },
    {
        "icon": "🔗",
        "title": "Oatly Hopes For Frothy IPO Market in 2021",
        "description": "Oatly hopes for frothy IPO market in 2021.",
        "link": "https://fortune.com/"
    },
    {
        "icon": "🥛",
        "title": "O-LPiate Vegan - The Pocket Guide to Animal-Free",
        "description": "Single cream: Oatly oat-based single cream SJL.",
        "link": "https://veganguide.com/"
    }
]

map_placeholder_url = "https://via.placeholder.com/400x200.png?text=Map"
wordcloud_text = "oatly oat milk company fighting for attention swedish years barista vegan brand attitude"

st.title("Brand Sentiment Dashboard")
search = st.text_input("Search Brand/Company", "")

# First row: Mentions (line chart), Sentiment (donut), Gender (donut)
row1_col1, row1_col2, row1_col3 = st.columns(3)

with row1_col1:
    st.subheader("Mentions")
    fig, ax = plt.subplots()
    ax.plot(date_labels, mentions_data)
    ax.set_title("Mentions Over Time")
    st.pyplot(fig, use_container_width=True)

with row1_col2:
    st.subheader("Sentiment")
    fig, ax = plt.subplots()
    ax.pie(list(sentiment.values()), labels=list(sentiment.keys()), autopct='%1.1f%%',
           startangle=90, wedgeprops=dict(width=0.4))
    ax.set(aspect="equal")
    st.pyplot(fig, use_container_width=True)

with row1_col3:
    st.subheader("Gender")
    fig, ax = plt.subplots()
    ax.pie(list(gender.values()), labels=list(gender.keys()), autopct='%1.1f%%',
           startangle=90, wedgeprops=dict(width=0.4))
    ax.set(aspect="equal")
    st.pyplot(fig, use_container_width=True)

# Second row: Mentions table, Countries Map, Topic Wordcloud
row2_col1, row2_col2, row2_col3 = st.columns(3)

with row2_col1:
    st.subheader("Mentions List")
    st.table(mentions_table)

with row2_col2:
    st.subheader("Countries")
    st.image(map_placeholder_url, use_column_width=True)

with row2_col3:
    st.subheader("Topic Cloud")
    wc = WordCloud(width=400, height=200, background_color='white').generate(wordcloud_text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig, use_container_width=True)

# Third row: Languages (donut), Sources (donut), Placeholder for Influencers
row3_col1, row3_col2, row3_col3 = st.columns(3)

with row3_col1:
    st.subheader("Languages")
    fig, ax = plt.subplots()
    ax.pie(list(language.values()), labels=list(language.keys()), autopct='%1.1f%%',
           startangle=90, wedgeprops=dict(width=0.4))
    ax.set(aspect="equal")
    st.pyplot(fig, use_container_width=True)

with row3_col2:
    st.subheader("Sources")
    fig, ax = plt.subplots()
    ax.pie(list(sources.values()), labels=list(sources.keys()), autopct='%1.1f%%',
           startangle=90, wedgeprops=dict(width=0.4))
    ax.set(aspect="equal")
    st.pyplot(fig, use_container_width=True)

with row3_col3:
    st.markdown("### Mentions")
    st.markdown('<div style="background-color:#fff;border-radius:8px;padding:18px">', unsafe_allow_html=True)
    for idx, mention in enumerate(mentions):
        item = f"""
        <div style="margin-bottom:9px">
        <span style="font-size:22px;vertical-align:middle;">{mention['icon']}</span>
        <a href="{mention['link']}" target="_blank" style="font-weight:600;color:#2363d1;font-size:15px;vertical-align:middle;text-decoration:none;">{mention['title']}</a><br>
        <span style="color:#666;font-size:13px;">{mention['description']}</span>
        </div>
        """
        st.markdown(item, unsafe_allow_html=True)
        if idx < len(mentions) - 1:
            st.markdown("<hr style='border:1px solid #eee;margin:8px 0'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# No sidebar, full width, search bar at top.
