import streamlit as st
import requests
import pandas as pd
import numpy as np
from pytrends.request import TrendReq

# ============================================
# Page Configuration & Title
# ============================================
st.set_page_config(
    page_title="Dashboard: Trends, News, Research, YouTube & Business Feasibility",
    page_icon="🚀",
    layout="wide"
)

st.title("Dashboard: Trends, News, Research & YouTube Videos")

st.write("E-MBA Cohort-2 Term-8 Final Project by Doshi Ghatana Mukeshkumar 23812027")

st.markdown("### (All sections use a single search input)")

# ============================================
# Global Unified Search Bar
# ============================================
search_query = st.text_input("Enter a topic to analyze:", "jewelry", key="general_search")

if search_query:
    # --- Prepare specialized queries ---
    news_search_term = f"{search_query} business"      # For business-focused news
    youtube_search_term = f"{search_query} business"     # For business-related YouTube videos
    sem_query = search_query                            # For research papers


    # ============================================
    # Data Acquisition
    # ============================================
    ## --- Google Trends for the Trends Section ---
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([search_query], cat=0, timeframe='now 1-d', geo='', gprop='')
        trends_df = pytrends.interest_over_time()
        if trends_df.empty:
            st.write("No trend data available for the selected term.")
        else:
            if "isPartial" in trends_df.columns:
                trends_df = trends_df.drop(columns=["isPartial"])
    except Exception as e:
        st.write(f"Error fetching Google Trends data: {e}")
        trends_df = pd.DataFrame()

    ## --- News Data from NewsAPI ---
    news_api_key = "9d59784ac92d47a8b26ac33a0dd75c77"  # Replace with your actual key if needed
    news_url = f"https://newsapi.org/v2/everything?q={news_search_term}&language=en&apiKey={news_api_key}"
    news_response = requests.get(news_url)
    news_data = news_response.json()

    ## --- Research Data from Semantic Scholar ---
    sem_api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    sem_params = {"query": sem_query, "limit": 5, "fields": "title,authors,url"}
    sem_response = requests.get(sem_api_url, params=sem_params)
    sem_data = sem_response.json()

    ## --- YouTube Videos from YouTube API ---
    youtube_api_key = "AIzaSyCO-Uu0S0ywGJKtNvbgB3MAC8WGReFtrnc"  # Replace with your key if needed
    youtube_url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=3"
        f"&q={youtube_search_term}&key={youtube_api_key}"
    )
    yt_response = requests.get(youtube_url)
    yt_data = yt_response.json()

    # ============================================
    # Layout: Two Columns
    # ============================================
    col1, col2 = st.columns(2)

    # ---------------- Column 1 ----------------
    with col1:
        # --- Google Trends Section ---
        st.header("Google Trends")
        if not trends_df.empty:
            st.line_chart(trends_df)
        else:
            st.write("No trend data available.")

        # --- Business News Section ---
        st.header("Business News")
        if news_data.get("status") == "ok":
            articles = news_data.get("articles", [])
            if articles:
                for article in articles[:5]:
                    st.subheader(article["title"])
                    st.write(article.get("description", "No description available"))
                    st.markdown(f"[Read More]({article['url']})")
                    st.write("---")
            else:
                st.write(f"No news articles found for '{news_search_term}'.")
        else:
            st.write("Error fetching news articles. Check your API key.")
    
        st.markdown("---")  # Divider within column 1

        # --- Business Opportunity & Feasibility Dashboard Section ---
        st.header("Business Opportunity & Feasibility Self-Assessment")
        st.markdown(f"#### Evaluating Business Idea: **{search_query}**")

        st.subheader("Self-Assessment")
        st.markdown("Rate the following factors on a scale of 1 to 10 (10 is best):")
        market_demand = st.slider("Market Demand", 1, 10, 5, key="slider_market_demand_feas")
        competition = st.slider("Competition Level (1 = Low, 10 = High)", 1, 10, 5, key="slider_competition_feas")
        financial_viability = st.slider("Financial Viability", 1, 10, 5, key="slider_financial_feas")
        founder_readiness = st.slider("Founder Readiness", 1, 10, 5, key="slider_founder_readiness_feas")

        st.subheader("Industry Trend Factor (via Google Trends)")
        # Use the same search_query to fetch trends for feasibility calculations.
        industry_trend_value = 5  # default value if trend unavailable
        trend_text = ""
        try:
            pytrends.build_payload([search_query], timeframe='today 12-m')
            trend_data = pytrends.interest_over_time()
            if not trend_data.empty:
                avg_interest = trend_data[search_query].mean()
                industry_trend_value = np.interp(avg_interest, [0, 100], [1, 10])
                trend_text = f"Google Trends Avg Interest: {avg_interest:.2f} (Scaled to {industry_trend_value:.1f}/10)"
            else:
                trend_text = "No trend data available; using default industry trend value."
        except Exception as e:
            trend_text = f"Error retrieving Google Trends data; using default value. ({e})"
        st.write(trend_text)

        if st.checkbox("Override Industry Trend manually", key="checkbox_override_feas"):
            industry_trend_value = st.slider("Industry Trend (Manual Input)", 1, 10, int(industry_trend_value), key="slider_manual_industry_feas")

        st.subheader("Calculating Feasibility Score")
        # Weighted scoring:
        # - Market Demand: weight = 2
        # - Competition: lower is better → invert using (11 - competition) with weight = 1
        # - Financial Viability: weight = 2
        # - Industry Trends: weight = 2
        # - Founder Readiness: weight = 3
        inverted_competition = 11 - competition
        raw_score = ((market_demand * 2) +
                     (inverted_competition * 1) +
                     (financial_viability * 2) +
                     (industry_trend_value * 2) +
                     (founder_readiness * 3))
        st.markdown(f"### Feasibility Score: **{raw_score:.1f} / 100**")

        st.subheader("Decision Insight")
        if raw_score >= 75:
            st.success("✅ This business idea appears highly viable! Proceed with confidence.")
        elif raw_score >= 50:
            st.warning("⚠️ Moderate viability. Consider further research and refining your strategy.")
        else:
            st.error("❌ Low feasibility. It might be wise to reconsider or pivot your approach.")

    # ---------------- Column 2 ----------------
    with col2:
        # --- Research Section ---
        st.header("Research Papers from Semantic Scholar")
        if "data" in sem_data:
            for paper in sem_data["data"]:
                title = paper.get("title", "No Title Available")
                st.subheader(title)
                authors_list = paper.get("authors", [])
                authors = ", ".join([author.get("name", "Unknown") for author in authors_list]) if authors_list else "No author information available"
                st.write(f"**Authors:** {authors}")
                url = paper.get("url", "#")
                st.markdown(f"[Read More]({url})")
                st.write("---")
        else:
            st.write(f"No research papers found for '{sem_query}'.")

        # --- YouTube Videos Section ---
        st.header("YouTube Videos related to Business Idea")
        if "items" in yt_data:
            for item in yt_data["items"]:
                video_id = item["id"]["videoId"]
                video_title = item["snippet"]["title"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.subheader(video_title)
                st.video(video_url)
                st.write("---")
        else:
            st.write("No YouTube videos found.")







#----Footter----
st.write("E-MBA Cohort-2 Term-8 Final Project by Doshi Ghatana Mukeshkumar 23812027")
