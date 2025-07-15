import streamlit as st

from modules.utils import load_data


#################################################################
# 데이터가 세션에 없으면 불러와서 저장
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]
#################################################################


st.title("금융 상품")
st.write("여기에 예/적금 상품, 대출 상품 등의 정보를 넣으세요.")

st.success("총 35개의 금융 상품이 등록되어 있습니다. adfdsfdfdsf")
