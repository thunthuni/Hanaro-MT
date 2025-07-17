import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from modules.utils import load_data
from modules.model import load_model, generate_derived_vars, get_economics_info

#################################################################
# 데이터가 세션에 없으면 불러와서 저장
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]

# 모델 데이터
if "shared_model" not in st.session_state:
    st.session_state["shared_model"] = load_model()
# 세션에서 꺼내쓰기
model = st.session_state["shared_model"]
_meta = model["meta"]
_cat_cols = _meta["cat_cols"]
_thres = _meta["threshold"]

#################################################################

st.set_page_config(
    page_title="대시보드",
    layout="wide",  # ✅ 화면 최대한 활용하기 위해 wide로 지정!!!
    initial_sidebar_state="expanded"
)

#st.sidebar.title("📂 분석 메뉴")
#st.sidebar.write("사이드바 내용입니다.")

st.title("중도해지 RISK 예측")
# TODO
st.write("어쩌구저쩌구 변수를 입력 하고 외부 데이터를 참조하여.. 해당 특성을 가진 고객+상품의 이탈 risk를 예측할 수 있습니다.")
st.markdown("---")




#####################################################################################
########## 화면 분할하여 왼쪽은 선택 창 #################################################

col1, divider, col2 = st.columns([1, 0.1, 2])


# 첫 번째 컨테이너: 드롭박스
with col1:

    # 날짜 선택창 (오늘 날짜를 2024년 6월 1일로 가정)
    today = date(2024, 6, 1) # 현재 시점을 24년 6월 1일로 가정

    # ✅ 콜백 함수 정의
    def set_range(start_offset):
        st.session_state["model_date"] = today

    # ✅ 초기 세션값 설정
    if "model_date" not in st.session_state:
        st.session_state["model_date"] = date(2024, 6, 1)

    # ✅ 날짜 선택 위젯
    selected_range = st.date_input(
        "**📅 분석 대상 계약의 가입일을 입력해주세요.**",
        value=st.session_state["model_date"],
        #min_value=df["날짜"].min().date(),
        max_value=today,  # TODO
        key="date_model"  # key는 따로 지정
    )
    # 사용자가 직접 변경한 경우에만 업데이트
    if (selected_range != st.session_state["model_date"]):
        st.session_state["model_date"] = selected_range
        
    model_date = st.session_state["model_date"]

    st.subheader("고객군 선택")
    # — 성별 처리 —
    st.markdown(
        "<div style='margin:0 0 0 0;'>성별</div>",
        unsafe_allow_html=True
    )
    genders = df['Gender'].unique().tolist()
    
    gender_cols = st.columns(len(genders))
    selected_genders = []
    for col, gender in zip(gender_cols, genders):
        with col:
            if st.checkbox(gender, value=False, key=f"gender_{gender}"):
                selected_genders.append(gender)


    # — 연령대 처리 —
    age_order = ['10대 이하','20대','30대','40대','50대','60대 이상']
    ages = [a for a in age_order if a in df['연령대'].unique()]
    selected_ages = st.multiselect("연령대 선택", options=ages, default=[])

    # — 직업 처리 —
    jobs = df['Job'].unique().tolist()
    selected_jobs = st.multiselect("직업 선택", options=jobs, default=[])

    # - 결혼 처리 -
    st.markdown(
        "<div style='margin:0 0 0 0;'>결혼유무</div>",
        unsafe_allow_html=True
    )
    families = df['Family'].unique().tolist()
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

    marketings = df['Marketing'].unique().tolist()

    marketing_cols = st.columns(len(marketings))
    selected_marketings = []
    for col, m in zip(marketing_cols, marketings):
        with col:
            if st.checkbox(marketing_map[m], value=False, key=f'marketing_{m}'):
                selected_marketings.append(m)

    # - 알림 처리 - 
    st.markdown(
        "<div style='margin:0 0 0 0;'>알림 서비스 여부</div>",
        unsafe_allow_html=True
    )
    unsubscribe_map = {1: '거절', 0: '허용'}

    unsubscribes = df['Unsubscribe'].unique().tolist()

    unsubscribe_cols = st.columns(len(unsubscribes))
    selected_unsubscribes = []
    for col, m in zip(unsubscribe_cols, unsubscribes):
        with col:
            if st.checkbox(unsubscribe_map[m], value=False, key=f'unsubscribe_{m}'):
                selected_unsubscribes.append(m)


    # - 연체 처리 - 
    st.markdown(
        "<div style='margin:0 0 0 0;'>연체 여부</div>",
        unsafe_allow_html=True
    )
    overdue_map = {1: '있음', 0: '없음'}

    overdues = df['Overdue'].unique().tolist()

    overdue_cols = st.columns(len(overdues))
    selected_overdues = []
    for col, m in zip(overdue_cols, overdues):
        with col:
            if st.checkbox(overdue_map[m], value=False, key=f'overdue_{m}'):
                selected_overdues.append(m)

    # New_trsc_Amt
    trsc_amount = st.number_input(
        "신규 계좌 개설 입금액 (원)",     # 라벨
        min_value=0,                # 최소값
        max_value=10000000,            # 최대값
        step=100,                   # 증감 단위
        value=10000                  # 기본값
    )

    # Card
    card_count = st.number_input(
        "계좌 연결 카드 수",     # 라벨
        min_value=0,                # 최소값
        max_value=10,            # 최대값
        step=1,                   # 증감 단위
        value=0                  # 기본값
    )


    st.subheader("상품 타입 선택")
    # 기본금리
    rate = st.number_input(
        "기본금리 (%)",
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        value=2.5
    )

    # 우대금리조건_개수
    prime_count = st.number_input(
        "우대금리조건 개수",     # 라벨
        min_value=0,                # 최소값
        max_value=10,            # 최대값
        step=1,                   # 증감 단위
        value=0                  # 기본값
    )

    # 최대우대금리
    # 조건에 따라 disabled + 값 고정
    if prime_count == 0:
        max_prime_rate = st.number_input(
            "최대우대금리 (%)",
            min_value=0.0,
            max_value=0.0,
            step=0.1,
            value=0.0,
            disabled=True,
            key="max_prime_rate"
        )
    else:
        max_prime_rate = st.number_input(
            "최대우대금리 (%)",
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            value=0.1,
            key="max_prime_rate"
        )


    # 완료 버튼 누르면 모델쪽으로
    if st.button("완료", type="primary"):
        if not selected_genders or not selected_ages or not selected_jobs\
        or not selected_families or not selected_marketings or not selected_unsubscribes\
        or not selected_overdues:
            st.warning("❗하나 이상의 값을 선택해주세요.")
        else:
            with st.spinner("예측 모델을 실행 중입니다... 잠시만 기다려주세요 ⏳"):


                model_cols = ['New_trsc_Amt', 'Gender', 'Age', 'Job', 'Family', 'Card', 'Overdue', 
                            'Unsubscribe', 'Marketing', '기본금리', '우대금리조건여부', '우대금리조건_개수', '최대우대금리',
                            '코스피 종가_mean_3m', '코스닥 종가_mean_3m', 'S&P 종가_mean_3m', '나스닥 종가_mean_3m',
                            '비트코인 종가_mean_3m', '금 종가_mean_3m', '달러 환율_mean_3m', '미국 국채_mean_3m',
                            '일본 국채_mean_3m', '유로 국채_mean_3m', '영국 국채_mean_3m', '코스피 종가_std_3m',
                            '코스닥 종가_std_3m', 'S&P 종가_std_3m', '나스닥 종가_std_3m', '비트코인 종가_std_3m',
                            '금 종가_std_3m', '달러 환율_std_3m', '미국 국채_std_3m', '일본 국채_std_3m',
                            '유로 국채_std_3m', '영국 국채_std_3m', '코스피 종가_slope_3m', '코스닥 종가_slope_3m',
                            'S&P 종가_slope_3m', '나스닥 종가_slope_3m', '비트코인 종가_slope_3m',
                            '금 종가_slope_3m', '달러 환율_slope_3m', '미국 국채_slope_3m', '일본 국채_slope_3m',
                            '유로 국채_slope_3m', '영국 국채_slope_3m', 'New_trsc_Amt_log', 'Age_group',
                            '금리차이', '금액변동성', '금리x연령']
                model_df = pd.DataFrame(columns=model_cols)
                deri_vars = generate_derived_vars(ages=selected_ages, trsc_amount=trsc_amount, rate=rate, max_prime_rate=max_prime_rate)
                eco_vars = get_economics_info(model_date)

                prime_yn = "Y"
                if prime_count == 0:
                    prime_yn = "N"
                for _gender in selected_genders:
                    for _job in selected_jobs:
                        for _fam in selected_families:
                            for _market in selected_marketings:
                                for _unsub in selected_unsubscribes:
                                    for _over in selected_overdues:
                                        for 연령대 in selected_ages:
                                            if 연령대 == "10대 이하":
                                                rng = range(0, 20)
                                            elif 연령대 == "20대":
                                                rng = range(20, 30)
                                            elif 연령대 == "30대":
                                                rng = range(30, 40)
                                            elif 연령대 == '40대':
                                                rng = range(40, 50)
                                            elif 연령대 == "50대":
                                                rng = range(50, 60)
                                            else:
                                                rng = range(60, 100)
                                            
                                            for _age in rng:
                                                for _age_group in deri_vars["Age_group"]:
                                                    for _rate_age in deri_vars["금리연령"]:
                                                        row1 = [trsc_amount, _gender, _age, _job, _fam, card_count, _over, _unsub, _market, rate, prime_yn, prime_count,
                                                            max_prime_rate]
                                                        row2 = list(eco_vars.values[0])
                                                        row3 = [deri_vars["New_trsc_Amt_log"], _age_group, deri_vars["금리차이"], deri_vars["금액변동성"], _rate_age] 
                                                        row = row1+row2+row3
                                                        model_df.loc[len(model_df)] = row

                prob = model["model"].predict_proba(model_df)[:, 1]
                prob_mean = prob.mean()
                #label = int(prob_mean >= _thres) 
                level1 = (0+_thres)/2
                level2 = (1-_thres)/2
                level = "저위험군" if prob_mean < level1 else ("중위험군" if prob_mean < level2 else "고위험군")

                with col2:
                    # TODO
                    st.header(f"입력한 데이터를 기반으로 추정한{level}")


with divider:
    st.markdown(
        "<div style='border-left:1px solid #ccc; height:1200px;'></div>",
        unsafe_allow_html=True
    )

