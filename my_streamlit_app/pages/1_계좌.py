import pandas as pd
import plotly.express as px

import streamlit as st

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from modules.utils import load_data, filter_by_date

#################################################################
# 데이터
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()

df = st.session_state["shared_df"]

df_account = df[['Acc_ID', 'Contract_Date_dt', 'Gender', 'Age', '연령대', 'Job', 'Family', 'Cancellation', 'Marketing', '상품코드', '상품명']]
df_account['Contract_Date_dt'] = pd.to_datetime(df_account['Contract_Date_dt'])
df_account['Cancellation'] = df_account['Cancellation'].map({'no': 0, 'yes': 1})

time_table = df_account.pivot_table(index='Contract_Date_dt', values = 'Acc_ID', aggfunc = 'count').reset_index()
account_number_graph = px.line(
    time_table,
    x='Contract_Date_dt',
    y='Acc_ID',
    title='계좌 개수 변화 추이'
)


# account_number_graph.show()
#################################################################

st.set_page_config(
    page_title="예·적금 상품 대시보드",
    layout="wide", 
    initial_sidebar_state="expanded"
)


st.title("계좌 정보")

tab1, tab2= st.tabs(['Overview' , 'Analysis'])

with tab1:
    st.header("Overview")
    num_prod = df["Acc_ID"].nunique()
    st.success(f"총 {num_prod}개의 계좌가 등록되어 있습니다.")
    
    today = date(2024, 6, 1) 

    def set_range(start_offset):
        st.session_state["start_date"] = today - relativedelta(months=start_offset)#timedelta(months=start_offset)
        st.session_state["end_date"] = today


    if "start_date" not in st.session_state:
        st.session_state["start_date"] = date(2023, 3, 1)
        st.session_state["end_date"] = date(2024, 6, 1)

    selected_range = st.date_input(
        "**📅 날짜 범위 선택**",
        value=(st.session_state["start_date"], st.session_state["end_date"]),
        #min_value=df["날짜"].min().date(),
        #max_value=today,
        key="date_range"  # key는 따로 지정
    )

    if (selected_range != (st.session_state["start_date"], st.session_state["end_date"])) and (len(selected_range) == 2):
        st.session_state["start_date"], st.session_state["end_date"] = selected_range

    c1, c2, c3, c4, _ = st.columns([1.5,1.5, 1.5, 1.5, 4])
    with c1:
        st.button("전체", on_click=set_range, args=[15], use_container_width=True)
    with c2:
        st.button("1년", on_click=set_range, args=[12], use_container_width=True)
    with c3:
        st.button("6개월", on_click=set_range, args=[6], use_container_width=True)
    with c4:
        st.button("3개월", on_click=set_range, args=[3], use_container_width=True)

    start_date, end_date = st.session_state["start_date"], st.session_state["end_date"]

    
    # TODO
    # 선택된 날짜 기반으로 데이터프레임 필터링
    filtered_num_graph = filter_by_date(time_table, start_date, end_date)
    account_number_graph = px.line(
        filtered_num_graph,
        x='Contract_Date_dt',
        y='Acc_ID',
        labels={
        'Contract_Date_dt': '개설일자',    # x축 이름
        'Acc_ID':            '계좌수 (개)' # y축 이름 + 단위
    }
    )
    st.markdown(
        """
        <style>
        #fixed-header {
            position: fixed;
            top: 0;
            left: 250px;                   
            width: 300px;     
            background: white;
            z-index: 999;
            padding: 8px 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: left;
            color: gray;
            font-size: 1.1em;
        }

        .app-wrapper > div.block-container {
            margin-top: 56px;  
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # 고정되는 날짜 기간
    st.markdown(
        f"""
        <div id="fixed-header">
        선택된 기간: {start_date} ~ {end_date}
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <hr style="
        border: none;
        border-top: 1px solid #ccc;
        margin: 4px 0 16px 0;
        ">
        """,
        unsafe_allow_html=True,
    )


    ############## 계좌 개수 ############## 
    st.subheader(f'계좌 개수 변화 추이')
    st.write(account_number_graph)


    ############## 계좌 세부 ##############
    
    filtered_account_info = filter_by_date(df_account, start_date, end_date)

    # 성별
    pie1 = (
        filtered_account_info['Gender']
        .value_counts()                   
        .reset_index(name='count')        
        .rename(columns={'index':'Gender'}) 
    )


    fig = px.pie(
        pie1,
        names='Gender',
        values='count',
        # title='성별 분포',
        hole=0.3,           
    )

    fig.update_traces(
    textposition='inside',
    textinfo='label+percent',
    showlegend=False
)
   
    # 연령
    age_group = filtered_account_info['연령대'].value_counts().reset_index()

    age_order = ['10대 이하', '20대', '30대', '40대', '50대', '60대 이상']

    age_bar = px.bar(
        age_group,
        x='연령대',
        y='count',
        category_orders={'연령대': age_order}
    )

    # 직업
    job_count = filtered_account_info['Job'].value_counts().reset_index()

    st.markdown(
        """
        <style>
        h5 {
        text-align: center !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    cols = st.columns(3)

    with cols[0]:
        st.markdown("##### 성별 ")  
        st.plotly_chart(fig, use_container_width=True)

    with cols[1]:
        st.markdown("##### 연령대")
        st.write(age_bar)

    with cols[2]:
        st.markdown("##### 직업")
        st.write(job_count)



with tab2:

    st.header("Analysis")

    col1, divider, col2 = st.columns([1, 0.1, 2])

    # 첫 번째 컨테이너: 드롭박스
    with col1:
        st.subheader("필터")


        # — 성별 처리 —
        st.markdown(
            "<div style='margin:0 0 0 0;'>성별</div>",
            unsafe_allow_html=True
        )
        genders = df_account['Gender'].unique().tolist()
        
        gender_cols = st.columns(len(genders))
        selected_genders = []
        for col, gender in zip(gender_cols, genders):
            with col:
                if st.checkbox(gender, value=False, key=f"gender_{gender}"):
                    selected_genders.append(gender)


        # — 연령대 처리 —
        age_order = ['10대 이하','20대','30대','40대','50대','60대 이상']
        ages = [a for a in age_order if a in df_account['연령대'].unique()]
        selected_ages = st.multiselect("연령대 선택", options=ages, default=[])

        # — 직업 처리 —
        jobs = df_account['Job'].unique().tolist()
        selected_jobs = st.multiselect("직업 선택", options=jobs, default=[])

        # - 결혼 처리 -
        st.markdown(
            "<div style='margin:0 0 0 0;'>결혼유무</div>",
            unsafe_allow_html=True
        )
        families = df_account['Family'].unique().tolist()
        family_cols = st.columns(len(families)-1)
        selected_families = []
        for col, family in zip(family_cols, families):
            with col:
                if st.checkbox(family, value=False, key=f'family_{family}'):
                    selected_families.append(family)

        # - 마케팅 동의 처리 - 
        st.markdown(
            "<div style='margin:0 0 0 0;'>마케팅 동의</div>",
            unsafe_allow_html=True
        )
        marketing_map = {1: '동의', 0: '비동의'}

        marketings = df_account['Marketing'].unique().tolist()

        marketing_cols = st.columns(len(marketings))
        selected_marketings = []
        for col, m in zip(marketing_cols, marketings):
            with col:
                if st.checkbox(marketing_map[m], value=False, key=f'marketing_{m}'):
                    selected_marketings.append(m)

    with divider:
        st.markdown(
            "<div style='border-left:1px solid #ccc; height:500px;'></div>",
            unsafe_allow_html=True
        )

    with col2:
        st.subheader("상품별 가입·해지 현황")

        # 1) 필터링
        df_f = df_account.copy()

        # 성별 필터
        if selected_genders:
            df_f = df_f[df_f['Gender'].isin(selected_genders)]
        # 연령대 필터
        if selected_ages:
            df_f = df_f[df_f['연령대'].isin(selected_ages)]
        # 직업 필터
        if selected_jobs:
            df_f = df_f[df_f['Job'].isin(selected_jobs)]
        # 마케팅 동의 필터
        if selected_marketings:
            df_f = df_f[df_f['Marketing'].isin(selected_marketings)]
        # 결혼유무 필터
        if selected_families:
            df_f = df_f[df_f['Family'].isin(selected_families)]

        # 2) 그룹별 집계
        summary = (
            df_f
            .groupby(['상품코드','상품명'])
            .agg(
                가입자수 = ('Acc_ID','nunique'),
                해지율   = ('Cancellation', lambda x: x.mean())  # cancellation이 1이면 해지
            )
            .reset_index()
            .set_index('상품코드')
        )

        # 3) 화면에 출력
        st.dataframe(
            summary.style.format({'해지율': '{:.1%}'}),
            use_container_width=True
        )






