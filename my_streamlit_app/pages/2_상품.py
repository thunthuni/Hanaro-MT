import streamlit as st
import plotly.express as px

from modules.utils import load_data, get_products_df


#################################################################
# 데이터 관련
if "shared_df" not in st.session_state:
    st.session_state["shared_df"] = load_data()
# 세션에서 꺼내쓰기
df = st.session_state["shared_df"]

df_prod = get_products_df(df)
df_yuji = df[df["Cancellation_bin"] == 1]
df_cate = df_yuji.pivot_table(index="상품구분", values="상품코드", aggfunc="count").reset_index()

churn_rate = df["Cancellation_bin"].mean()
yuji_count = len(df[df["Cancellation_bin"] == 0])
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
    #st.write("여기에 예/적금 상품, 대출 상품 등의 정보를 넣으세요.")

    num_prod = df_prod["상품코드"].nunique()
    st.success(f"총 {num_prod}개의 상품이 등록되어 있습니다.")
    ####################################################################


    #### 레이아웃 2 #####################################################
    col2_1, _, col2_2, _, col2_3 = st.columns([1, 0.2, 1, 0.2, 1])
    with col2_1 :
        st.subheader(f'상품구분 별 점유율')
        fig = px.pie(data_frame = df_cate, values='상품코드', names='상품구분')#, title="상품구분 별 점유율")
        st.plotly_chart(fig, use_container_width=True)

    with col2_2 :
        st.subheader(f'⚠️ 중도 해지율: {round(churn_rate*100, 2)} %')
        st.subheader(f'👨‍👩‍👧‍👦 유지 고객수: {round(yuji_count)} 명')

    with col2_3:
        # TODO
        st.subheader(f'전체 상품 우대 조건 유형 수')


    ####################################################################


    #### 레이아웃 3 #####################################################
    col1,col2 = st.columns([1, 1])
    with col1 :
        st.subheader('세부 정보를 확인하시려면 체크박스를 선택해주세요.')
        event = st.dataframe(
            df_prod,
            key="df_select",
            on_select="rerun",
            selection_mode="single-row",
            hide_index=True 
        )
    with col2 :
        # 선택된 행의 정보를 가져와 처리
        # event.selection.rows는 선택된 행의 인덱스 리스트를 반환합니다.
        if event.selection.rows:
            st.subheader(f'{event.selection.rows[0]} 상품 세부 정보:')

            print(event.selection.rows)
            selected_row_index = event.selection.rows[0]
            selected_row_data = df_prod.iloc[selected_row_index]

            st.write(selected_row_data)

    ####################################################################




        
with tab2:
    #tab B를 누르면 표시될 내용 
    st.write('hi')






















#st.dataframe(df_prod)
