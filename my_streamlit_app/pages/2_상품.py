import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from modules.utils import load_data, get_products_df, get_prime_df, get_prime_count, filter_by_date, get_bank_df


#################################################################

# 데이터 관련
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]

df_prime = get_prime_df(df)
prime_cnt = get_prime_count(df_prime)

df_bank = get_bank_df(df)

#################################################################

st.set_page_config(
    page_title="예·적금 상품 대시보드",
    layout="wide",  # ✅ 화면 최대한 활용하기 위해 wide로 지정!!!
    initial_sidebar_state="expanded"
)


st.title("예·적금 상품")

# 탭 생성
tab1, tab2= st.tabs(['Overview' , 'Analysis'])

with tab1:
    #### 레이아웃 1 #####################################################
    st.header("Overview")
    num_prod = df_bank["상품코드"].nunique()
    st.success(f"총 {num_prod}개의 상품이 등록되어 있습니다.")

    # 날짜 선택창 (오늘 날짜를 2024년 6월 1일로 가정)
    today = date(2024, 6, 1) # 현재 시점을 24년 6월 1일로 가정

    # ✅ 콜백 함수 정의
    def set_range(start_offset):
        st.session_state["start_date"] = today - relativedelta(months=start_offset)#timedelta(months=start_offset)
        st.session_state["end_date"] = today

    # ✅ 초기 세션값 설정
    if "start_date" not in st.session_state:
        st.session_state["start_date"] = date(2023, 3, 1)
        st.session_state["end_date"] = date(2024, 6, 1)

    # ✅ 날짜 선택 위젯
    selected_range = st.date_input(
        "**📅 날짜 범위 선택**",
        value=(st.session_state["start_date"], st.session_state["end_date"]),
        #min_value=df["날짜"].min().date(),
        #max_value=today,
        key="date_range"  # key는 따로 지정
    )
    # 사용자가 직접 변경한 경우에만 업데이트
    if (selected_range != (st.session_state["start_date"], st.session_state["end_date"])) and (len(selected_range) == 2):
        st.session_state["start_date"], st.session_state["end_date"] = selected_range

    c1, c2, c3, c4, _ = st.columns([1, 1, 1, 1, 6])
    with c1:
        st.button("전체", on_click=set_range, args=[15], use_container_width=True)
    with c2:
        st.button("1년", on_click=set_range, args=[12], use_container_width=True)
    with c3:
        st.button("6개월", on_click=set_range, args=[6], use_container_width=True)
    with c4:
        st.button("3개월", on_click=set_range, args=[3], use_container_width=True)

    start_date, end_date = st.session_state["start_date"], st.session_state["end_date"]


    # 선택된 날짜 기반으로 데이터프레임 필터링
    filtered_df = filter_by_date(df, start_date, end_date)
    df_cate = filtered_df.pivot_table(index="상품구분", values="상품코드", aggfunc="count").reset_index()

    churn_rate = filtered_df["Cancellation_bin"].mean()
    newbie_count = len(filtered_df)

    for_yuji_df = filter_by_date(df, date(2023, 3, 1), end_date)
    df_yuji = for_yuji_df[for_yuji_df["Cancellation_bin"] == 0]
    yuji_count = len(df_yuji)

    # 해지율 계산부
    churn_rate_df = filtered_df.pivot_table(index="상품코드", values="Cancellation_bin", aggfunc="mean").reset_index()
    churn_rate_df.columns = ["상품코드", "상품별해지율_filtered"]
    
    df_prod = get_products_df(df_bank, churn_rate_df)

    ####################################################################


    #### 레이아웃 2 #####################################################
    col2_1, _, col2_2, _, col2_3 = st.columns([1, 0.2, 1, 0.2, 1])
    with col2_1 :
        st.subheader(f'📊 상품구분 별 점유율')
        fig = px.pie(data_frame = df_cate, values='상품코드', names='상품구분')#, title="상품구분 별 점유율")
        st.plotly_chart(fig, use_container_width=True)

    with col2_2 :
        st.subheader(f'⚠️ 중도 해지율: {round(churn_rate*100, 2)} %')
        st.subheader(f'🆕 신규 고객수: {round(newbie_count)} 명')
        st.subheader(f'👨‍👩‍👧‍👦 유지 고객수: {round(yuji_count)} 명')

    with col2_3:
        st.subheader(f'🔥전체 상품 우대 조건 유형 수')
        df_prime_cnt = pd.DataFrame(prime_cnt).reset_index()    
        df_prime_cnt.columns = ["우대 조건_original", "Count"]
        df_prime_cnt['우대 조건'] = df_prime_cnt["우대 조건_original"].str.extract(r'우대금리조건_(.+?)_여부')
        st.dataframe(df_prime_cnt[["우대 조건", "Count"]], hide_index=True)

    ####################################################################


    #### 레이아웃 3 #####################################################
    st.markdown("---")

    st.subheader('세부 정보를 확인하시려면 체크박스를 선택해주세요.')
    st.markdown(f"**상품별 해지율 산정 기간**: {start_date} - {end_date}")

    event = st.dataframe(
        df_prod,
        key="df_select",
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True 
    )

    if event.selection.rows:
        idx = event.selection.rows[0]
        selected_row_code = df_prod.iloc[idx]["상품코드"]
        df_bank_filtered = df_bank[df_bank["상품코드"] == selected_row_code]
        df_prime_filtered = df_prime[df_prime["상품코드"] == selected_row_code].drop(columns=['은행코드', '은행명', '상품명', '상품코드', '상품일련번호'])

        df_prod_info = pd.merge(df_bank_filtered, df_prime_filtered, on="Deposit_Code", how="outer")
        one_row = df_prod_info.iloc[0]

        st.subheader(f'상품 세부 정보:')
        st.markdown(f"> **{one_row["상품명"]}**")
        st.markdown(f"{one_row["상품개요_설명"]}")

        base_row = ["상품구분", "상품코드", "은행명", "은행코드", "신규채널", "해지채널", "만기여부", "예금자보호대상여부"]

        if not pd.isnull(one_row["판매한도금액"]):
            base_row.append('판매한도금액')

        if not pd.isnull(one_row["회전식_정기예금_회전주기_개월수"]):
            base_row.append('회전식_정기예금_회전주기_개월수')

        base_row.append("예금입출금방식")

        if one_row["예금입출금방식"] == "2:거치식(목돈운용)":
            base_row.append("통장거치식_신규가입금액_단위")
        elif one_row["예금입출금방식"] == "3:적립식(목돈마련)":
            base_row.append("적립식_월부금_단위")

        if one_row['가입제한_조건여부'] == "있음":
            base_row.append("가입제한_조건")

        base_row.append("만기후이율")
        base_row.append("중도해지이율")
        base_row.append("기타_상품가입_고려사항")
        base_row.append("추가내용")

        #st.dataframe(one_row[base_row].rename("Value", inplace=True).reset_index(), hide_index=True)
        st.data_editor(
            one_row[base_row].rename("Value", inplace=True).reset_index(),
            column_config={
                "index": st.column_config.TextColumn(width="small"),
                "Value": st.column_config.TextColumn(width="large"),
            },
            use_container_width=True,
            hide_index=True,
            disabled=True
        )


        st.markdown(f'**상세:**')
        base_col2 = ["Deposit_Code", "상품일련번호", "계약기간개월수_최소구간", "계약기간개월수_최대구간", "가입금액_최소구간", "가입금액_최대구간", "이자지급방법", "이자계산방법", "가입대상고객_조건", "세제혜택_비과세종합저축_조건"]
        if one_row["예금입출금방식"] == "3:적립식(목돈마련)":
            base_col2.append("적립식_부금납입방식")
            base_col2.append("적립식_부금납입주기")
            base_col2.append("적립식_부금금액한도_조건")
        
        st.dataframe(df_prod_info[base_col2].sort_values(by="상품일련번호"), hide_index=True)


        st.markdown(f'**금리:**')
        base_inte = round(max(df_prod_info["기본금리"]), 2)
        max_inte = round( max(df_prod_info["기본금리"] + df_prod_info["최대우대금리"]), 2)

        if pd.isnull(max_inte):
            st.markdown(f'- 최대 금리: {base_inte}')
        else:
            st.markdown(f'- 최대 금리: {max_inte}')

        base_col3 = ["Deposit_Code", "상품일련번호", "기본금리"]
        prime_conditions = [item for item in df_prod_info.columns if (item.startswith("우대금리조건_") and item.endswith("_여부"))]

        if not pd.isnull(one_row["우대금리조건_개수"]):
            base_col3.append("우대금리조건_개수")
            base_col3.append("최대우대금리")

            for cond in prime_conditions:
                if one_row[cond] == 1:
                    prime_str = cond.split("_")[1]
                    if (prime_str == "예금자동이체") or (prime_str == "보험료자동이체") or (prime_str == "연금자동이체"):
                        base_col3.append("우대금리조건_" + prime_str + "_여부_조건")
                        base_col3.append("우대금리조건_" + prime_str + "_우대금리")
                    else:
                        base_col3.append("우대금리조건_" + prime_str + "_조건")
                        base_col3.append("우대금리조건_" + prime_str + "_우대금리")

        st.dataframe(df_prod_info[base_col3].sort_values(by="상품일련번호"), hide_index=True)

        #TODO
        st.markdown(f'**타행 유사 상품:** (TODO)')



















    col1,col2 = st.columns([1, 1])
    with col1 :
        pass
    #with col2 :
        # 선택된 행의 정보를 가져와 처리
        # event.selection.rows는 선택된 행의 인덱스 리스트를 반환합니다.

    ####################################################################




        
with tab2:
    #tab B를 누르면 표시될 내용 
    st.write('hi 아아아아아아아ㅏ아아아아아아 언제하지')





















#st.dataframe(df_prod)
