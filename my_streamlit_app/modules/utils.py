import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_data(path="data/df_.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    df = pd.read_excel(full_path, index_col=0)
    return df


def get_products_df(df):
    df["상품별해지율[%]"] = round(df['상품별해지율'] * 100, 2)
    return df[['상품코드', "상품명", "상품구분", "상품별해지율[%]", "은행코드", "은행명"]].drop_duplicates().sort_values(by='상품별해지율[%]', ascending=False)





"""
df.drop(columns=["Acc_ID", "Contract_Date", "New_trsc_Amt", "Gender", "Age", "Job",	"Family", "Cancellation", "Card", 'Overdue', 
                            'Unsubscribe', 'Telecom', 'Marketing', '연령대', 'Cancellation_bin']).drop_duplicates()
"""