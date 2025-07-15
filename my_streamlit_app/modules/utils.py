import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

import streamlit as st

import requests
from bs4 import BeautifulSoup

from serpapi import GoogleSearch



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

        

from datetime import datetime




def fetch_google_related_queries(keyword):

    params = {
        "q": keyword,
        "engine": "google_trends",
        "data_type": "RELATED_QUERIES",
        "api_key": SERPAPI_KEY, 
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    try:
        rising = results["related_queries"]["rising"]
        queries = [item["query"] for item in rising]
        return queries[:10]  
    except KeyError:
        return []
    

def fetch_google_trends_graph(keyword):
    params = {
        "q": keyword,
        "api_key": SERPAPI_KEY, 
        "engine": "google_trends"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    try:
        timeline = results["interest_over_time"]["timeline_data"]
        trend_data = []

        for entry in timeline:
            timestamp = entry.get("timestamp")  # 유닉스 타임스탬프 (str)
            if timestamp is None:
                continue

            # 🔧 timestamp를 datetime으로 변환
            parsed_date = datetime.utcfromtimestamp(int(timestamp))

            for item in entry.get("values", []):
                query = item.get("query")
                value = item.get("extracted_value")
                if query is not None and value is not None:
                    trend_data.append({
                        "date": parsed_date,
                        "query": query,
                        "value": value
                    })

        return trend_data

    except KeyError:
        return []