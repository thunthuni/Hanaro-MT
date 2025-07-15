import pandas as pd
import os
import streamlit as st

import requests
from bs4 import BeautifulSoup


@st.cache_data
def load_data(path="data/df_merged.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    df = pd.read_excel(full_path)
    return df


def crawling_news():
    url = 'https://news.naver.com/breakingnews/section/101/259'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 뉴스 링크와 제목 20개 가져오기
    news_list = soup.select('div.sa_text > a')[:20]

    results = []
    for item in news_list:
        title = item.text.strip()
        raw_link = item['href']
        
        # 링크 정제: 중복된 prefix 제거
        if raw_link.startswith("https://news.naver.comhttps://"):
            link = raw_link.replace("https://news.naver.com", "")
        elif raw_link.startswith("/mnews"):
            link = "https://news.naver.com" + raw_link
        else:
            link = raw_link
        
        results.append([title, link])

    return results