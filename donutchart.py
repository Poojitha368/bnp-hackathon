import streamlit as st
import plotly.graph_objects as go

def createDonutChart(sentiment,pos_count,neu_count,neg_count,final_score,company):
    labels = ['Positive', 'Neutral', 'Negative']
    values = [pos_count, neu_count, neg_count]
    colors = ['#2E8B57', '#FFA500', '#DC143C']

    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.4,
        marker_colors=colors
    )])

    # Add center text showing overall sentiment
    fig.add_annotation(
        text=f"<b>{sentiment.upper()}</b><br>Score: {final_score:.1f}/5",
        x=0.5, y=0.5,
        font_size=16,
        showarrow=False
    )

    fig.update_layout(title=f"Sentiment Distribution for {company}")
    st.plotly_chart(fig, use_container_width=True)

    