import streamlit as st
import pandas as pd

from modules.utils import load_data


#################################################################
# 데이터가 세션에 없으면 불러와서 저장
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]
#################################################################


st.set_page_config(page_title="은행 대시보드", layout="wide")

st.title("상품개발 부서 대시보드")
st.write("왼쪽 사이드바에서 페이지를 선택해 주세요.")


