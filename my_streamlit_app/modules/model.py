from catboost import CatBoostClassifier
import joblib
import os
import numpy as np
import pandas as pd

import streamlit as st
from datetime import datetime, date, timedelta


@st.cache_data
def load_model(path="data/model.pkl"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    model = joblib.load(full_path)
    return model


def generate_derived_vars(ages, trsc_amount, rate, max_prime_rate):
    # 연속형
    New_trsc_Amt_log = np.log1p(trsc_amount)
    금리차이 = max_prime_rate - rate
    금액변동성 = New_trsc_Amt_log # 의미없음

    # 범주형 포함
    금리연령 = []
    Age_group = []
    for 연령대 in ages:
        if 연령대 == "10대 이하":
            rng = range(0, 20)
            Age_group.append("20s")
        elif 연령대 == "20대":
            rng = range(20, 30)
            Age_group.append("20s")
        elif 연령대 == "30대":
            rng = range(30, 40)
            Age_group.append("30s")
        elif 연령대 == '40대':
            rng = range(40, 50)
            Age_group.append("40s")
        elif 연령대 == "50대":
            rng = range(50, 60)
            Age_group.append("50s")
        else:
            rng = range(60, 100)
            Age_group.append("60+")
        for i in rng:
            금리연령.append(rate * i)


    return {"New_trsc_Amt_log": New_trsc_Amt_log,
            "금리차이": 금리차이,
            "금액변동성": 금액변동성,
            "금리연령": 금리연령,
            "Age_group": Age_group}


def get_economics_info(today, path="data/economics.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)
    df = pd.read_excel(full_path)
    df_fill = df.set_index('Date').resample('D').asfreq().reset_index()
    df_fill.ffill(inplace = True)

    # 시작일: 90일 전
    start_date = today - timedelta(days=90)
    
    today = pd.to_datetime(today)
    start_date = pd.to_datetime(start_date)
    
    # 필터링
    df_filtered = df_fill[(df_fill['Date'] >= start_date) & (df_fill['Date'] <= today)]

    mean_3m = df_filtered.mean().drop("Date").to_frame().T
    mean_3m.columns = [col + '_mean_3m' for col in mean_3m.columns]
    std_3m = df_filtered.std().drop("Date").to_frame().T
    std_3m.columns = [col + '_std_3m' for col in std_3m.columns]

    df_pct = df_fill.select_dtypes(include='number').pct_change(periods=90)
    df_pct['Date'] = df_fill['Date']

    slope_3m = df_pct[df_pct["Date"] == today].reset_index()
    slope_3m.drop(columns=["index", "Date"], inplace=True)
    slope_3m.columns = [col + '_slope_3m' for col in slope_3m.columns]

    result = pd.concat([mean_3m, std_3m, slope_3m], axis=1)
    return result


if __name__ == "__main__":
    get_economics_info(date(2024, 6, 1))