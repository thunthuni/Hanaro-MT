import streamlit as st
from modules.utils import crawling_news

st.set_page_config(page_title="Trends & News", layout="wide")
st.title("📈 Trends & News")
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
