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
def load_data(path="data/df_.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    df = pd.read_excel(full_path, index_col=0)
    return df


def get_products_df(df):
    df["상품별해지율[%]"] = round(df['상품별해지율'] * 100, 2)
    return df[['상품코드', "상품명", "상품구분", "상품별해지율[%]", "은행코드", "은행명"]].drop_duplicates().sort_values(by='상품별해지율[%]', ascending=False)



def get_bank_df(df):
    bank_cols = ['은행코드',	'은행명',	'상품코드',	'상품명',	'상품일련번호',	'계약기간개월수_최소구간',	'계약기간개월수_최대구간',	'가입금액_최소구간',	'가입금액_최대구간',
                '통장거치식_신규가입금액_단위',	'적립식_월부금_단위',	'상품개요_설명',	'신규채널',	'해지채널',	'상품그룹코드',	'상품그룹명',	'예금입출금방식',	'만기여부',	'이자지급방법',
                '이자계산방법',	'적립식_부금납입방식',	'적립식_부금납입주기',	'적립식_부금금액한도_여부',	'적립식_부금금액한도_조건',	'가입대상고객_조건여부',	'가입대상고객_조건',
                '가입제한_조건여부',	'가입제한_조건',	'기본금리',	'예금자보호대상여부',	'판매한도금액',	'만기후이율',	'중도해지이율',	'세제혜택_비과세종합저축_여부',
                '세제혜택_비과세종합저축_조건',	'회전식_정기예금_여부',	'회전식_정기예금_회전주기_개월수',	'기타_상품가입_고려사항',	'추가내용',	'Deposit_Code',	'상품구분',	'상품구분출처',
                '계약기간개월수_최소구간_new',	'계약기간개월수_최대구간_new',	'가입금액_최소구간_new',	'가입금액_최대구간_new',	'신규채널_모바일웹뱅킹',	'신규채널_스마트뱅킹',	
                '신규채널_영업점',	'신규채널_인터넷뱅킹',	'신규채널_콜센타',	'신규채널_개수',	'해지채널_계좌이체',	'해지채널_모바일웹뱅킹',	'해지채널_스마트뱅킹',	'해지채널_영업점',
                    '해지채널_인터넷뱅킹',	'해지채널_콜센타',	'해지채널_개수',	'고정계약기간여부']
    return df[bank_cols].copy().drop_duplicates().reset_index(drop=True)

def get_prime_df(df):
    prime_cols = ['은행코드',	'은행명',	'상품코드',	'상품명',	'상품일련번호',	'우대금리조건여부',	'우대금리조건_개수',	'최대우대금리',	'우대금리조건_고객예금실적_여부',	
                  '우대금리조건_고객예금실적_조건',	'우대금리조건_고객예금실적_우대금리',	'우대금리조건_우수고객우대제도_여부',	'우대금리조건_우수고객우대제도_조건',	
                  '우대금리조건_우수고객우대제도_우대금리',	'우대금리조건_가입금액우대_여부',	'우대금리조건_가입금액우대_조건',	'우대금리조건_가입금액우대_우대금리',	
                  '우대금리조건_아파트관리비이체_여부',	'우대금리조건_아파트관리비이체_조건',	'우대금리조건_아파트관리비이체_우대금리',	'우대금리조건_공과금이체_여부',	
                  '우대금리조건_공과금이체_조건',	'우대금리조건_공과금이체_우대금리',	'우대금리조건_급여이체_여부',	'우대금리조건_급여이체_조건',	'우대금리조건_급여이체_우대금리',	
                  '우대금리조건_예금자동이체_여부',	'우대금리조건_예금자동이체_여부_조건',	'우대금리조건_예금자동이체_우대금리',	'우대금리조건_보험료자동이체_여부',	
                  '우대금리조건_보험료자동이체_여부_조건',	'우대금리조건_보험료자동이체_우대금리',	'우대금리조건_연금자동이체_여부',	'우대금리조건_연금자동이체_여부_조건',	
                  '우대금리조건_연금자동이체_우대금리',	'우대금리조건_신용카드가맹점결제계좌_여부',	'우대금리조건_신용카드가맹점결제계좌_조건',	'우대금리조건_신용카드가맹점결제계좌_우대금리',
                  '우대금리조건_신용카드결제계좌_여부',	'우대금리조건_신용카드결제계좌_조건',	'우대금리조건_신용카드결제계좌_우대금리',	'우대금리조건_신용카드사용금액_여부',
                    '우대금리조건_신용카드사용금액_조건',	'우대금리조건_신용카드사용금액_우대금리',	'우대금리조건_체크카드연계_여부',	'우대금리조건_체크카드연계_조건',
                    '우대금리조건_체크카드연계_우대금리',	'우대금리조건_제휴카드연계_여부',	'우대금리조건_제휴카드연계_조건',	'우대금리조건_제휴카드연계_우대금리',	'우대금리조건_재유치_여부',
                    '우대금리조건_재유치_조건',	'우대금리조건_재유치_우대금리',	'우대금리조건_카드사용실적_여부',	'우대금리조건_카드사용실적_조건',	'우대금리조건_카드사용실적_우대금리',
                    '우대금리조건_퇴직금예치_여부',	'우대금리조건_퇴직금예치_조건',	'우대금리조건_퇴직금예치_우대금리',	'우대금리조건_고객특성우대_여부',	'우대금리조건_고객특성우대_조건',
                    '우대금리조건_고객특성우대_우대금리',	'우대금리조건_장병우대_여부',	'우대금리조건_장병우대_조건',	'우대금리조건_장병우대_우대금리',	'우대금리조건_농어민우대_여부',
                    '우대금리조건_농어민우대_조건',	'우대금리조건_농어민우대_우대금리',	'우대금리조건_어린이우대_여부',	'우대금리조건_어린이우대_조건',	'우대금리조건_어린이우대_우대금리',	
                    '우대금리조건_학생우대_여부',	'우대금리조건_학생우대_조건',	'우대금리조건_학생우대_우대금리',	'우대금리조건_첫거래우대_여부',	'우대금리조건_첫거래우대_조건',
                    '우대금리조건_첫거래우대_우대금리',	'우대금리조건_고객연령우대_여부',	'우대금리조건_고객연령우대_조건',	'우대금리조건_고객연령우대_우대금리',	'우대금리조건_비대면채널_여부',
                    '우대금리조건_비대면채널_조건',	'우대금리조건_비대면채널_우대금리',	'우대금리조건_인터넷뱅킹_여부',	'우대금리조건_인터넷뱅킹_조건',	'우대금리조건_인터넷뱅킹_우대금리',
                    '우대금리조건_모바일뱅킹_여부',	'우대금리조건_모바일뱅킹_조건',	'우대금리조건_모바일뱅킹_우대금리',	'우대금리조건_모바일앱_여부', '우대금리조건_모바일앱_조건',	
                    '우대금리조건_모바일앱_우대금리',	'우대금리조건_오픈뱅킹_여부',	'우대금리조건_오픈뱅킹_조건',	'우대금리조건_오픈뱅킹_우대금리',	'우대금리조건_마이데이터_여부',
                    '우대금리조건_마이데이터_조건',	'우대금리조건_마이데이터_우대금리',	'우대금리조건_상품미보유_여부',	'우대금리조건_상품미보유_조건',	'우대금리조건_상품미보유_우대금리',
                    '우대금리조건_만기금액우대_여부', '우대금리조건_만기금액우대_조건',	'우대금리조건_만기금액우대_우대금리',	'우대금리조건_마케팅활용동의_여부',	'우대금리조건_마케팅활용동의_조건',
                    '우대금리조건_마케팅활용동의_우대금리',	'우대금리조건_위치인증_여부',	'우대금리조건_위치인증_조건',	'우대금리조건_위치인증_우대금리',	'우대금리조건_기타1_여부',	
                    '우대금리조건_기타1_조건',	'우대금리조건_기타1_우대금리',	'우대금리조건_기타2_여부',	'우대금리조건_기타2_조건',	'우대금리조건_기타2_우대금리',	'우대금리조건_기타3_여부',
                    '우대금리조건_기타3_조건',	'우대금리조건_기타3_우대금리',	'우대금리조건_기타4_여부',	'우대금리조건_기타4_조건',	'우대금리조건_기타4_우대금리',	'우대금리조건_기타5_여부',
                    '우대금리조건_기타5_조건',	'우대금리조건_기타5_우대금리',	'Deposit_Code']
    return df[prime_cols].copy().drop_duplicates().reset_index(drop=True)

def get_prime_count(df):
    # input_df는 prime_df이여야함. (using `get_prime_df()`)
    
    prime_conditions = [item for item in df.columns if (item.startswith("우대금리조건_") and item.endswith("_여부"))]
    sorted_prime_cnt = df.pivot_table(index="상품코드", values=prime_conditions).sum().sort_values(ascending=False)
    etc = ['우대금리조건_기타1_여부','우대금리조건_기타2_여부','우대금리조건_기타3_여부','우대금리조건_기타4_여부','우대금리조건_기타5_여부']
    etc_sum = sorted_prime_cnt[etc].sum()
    sorted_prime_cnt.drop(etc, inplace=True)
    sorted_prime_cnt["우대금리조건_기타_여부"] = etc_sum # 기타 1-5는 맨 마지막에 하나로 통합

    return sorted_prime_cnt


"""


"""


"""
df.drop(columns=["Acc_ID", "Contract_Date", "New_trsc_Amt", "Gender", "Age", "Job",	"Family", "Cancellation", "Card", 'Overdue', 
                            'Unsubscribe', 'Telecom', 'Marketing', '연령대', 'Cancellation_bin']).drop_duplicates()
"""


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