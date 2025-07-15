import streamlit as st
import pandas as pd
import altair as alt
import os
from dotenv import load_dotenv

from modules.utils import crawling_news, fetch_google_related_queries, fetch_google_trends_graph





st.set_page_config(page_title="Trends & News", layout="wide")
st.title("📈 Trends & News")

################ 금융뉴스
st.subheader("📰 최신 금융 뉴스")
news_list = crawling_news()  # [['제목', '링크'], ...]
news_list = [item for item in news_list if isinstance(item, list) and len(item) == 2]


st.markdown("""
    <style>
    .scroll-box {
        height: 300px;
        overflow-y: scroll;
        padding: 10px;
        border: 1px solid #DDD;
        border-radius: 8px;
        background-color: #f9f9f9;
        font-family: sans-serif;
    }
    .scroll-box::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-box::-webkit-scrollbar-thumb {
        background-color: #ccc;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)


news_html = "<div class='scroll-box'>"
for title, link in news_list:
    news_html += f"""
<p style='margin-bottom: 8px; font-size: 15px;'>
    • <a href="{link}" target="_blank" style="text-decoration: none; color: black;">
        {title}
    </a>
</p>
    """
news_html += "</div>"

st.markdown(news_html, unsafe_allow_html=True)


################ 키워드 검색량 

st.subheader("🔍 구글 트렌드 키워드 검색")

keyword = st.text_input("검색어를 입력하세요", value="하나은행")
search = st.button("확인")

if search and keyword:

    with st.spinner("🔄 구글 트렌드 데이터를 가져오는 중..."):
        # 관심도 추세 데이터
        trend_graph_data = fetch_google_trends_graph(keyword)
        
        if trend_graph_data:
            st.success(f"📈 '{keyword}' 관심도 추이")
            df = pd.DataFrame(trend_graph_data)
            df = df.sort_values('date')

            
            chart = alt.Chart(df).mark_line(point=True).encode(
                x=alt.X('date:T', title='날짜'),
                y=alt.Y('value:Q', title='관심도'),
                color='query:N'
            ).properties(width=700, height=300)

            st.altair_chart(chart)

        # 관련 검색어
        trends = fetch_google_related_queries(keyword)

        if trends:
            st.success(f"🔍 '{keyword}' 관련 검색어 Top {len(trends)}")

            st.markdown("""
            <style>
            .scroll-box {
                max-height: 250px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: #f9f9f9;
                font-family: sans-serif;
            }
            .scroll-box::-webkit-scrollbar {
                width: 6px;
            }
            .scroll-box::-webkit-scrollbar-thumb {
                background-color: #bbb;
                border-radius: 4px;
            }
            </style>
            """, unsafe_allow_html=True)

            trend_html = "<div class='scroll-box'>"
            for i, t in enumerate(trends, 1):
                trend_html += f"<p style='margin-bottom: 8px; font-size: 15px;'>• {i}. {t}</p>"
            trend_html += "</div>"

            st.markdown(trend_html, unsafe_allow_html=True)
        else:
            st.warning("관련 검색어를 찾을 수 없습니다.")