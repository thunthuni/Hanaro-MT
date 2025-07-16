import streamlit as st

from modules.utils import load_data


#################################################################
# 데이터가 세션에 없으면 불러와서 저장
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]
#################################################################


# account_df = 
st.title("계좌 정보")

tab1, tab2= st.tabs(['Overview' , 'Analysis'])

