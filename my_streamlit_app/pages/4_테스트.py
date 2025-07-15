import streamlit as st
import plotly.express as px

from modules.utils import load_data, get_products_df

st.set_page_config(
    page_title="테스트",
    layout="wide",  # ✅ 화면 최대한 활용하기 위해 wide로 지정!!!
    initial_sidebar_state="expanded"
)


st.title("테스트")
