import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_data(path="data/df_merged.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    df = pd.read_excel(full_path)
    return df