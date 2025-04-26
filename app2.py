import streamlit as st
import openai
import os

# OpenAI 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🏢 퇴사연구소 Streamlit 앱 시작
st.set_page_config(page_title="퇴사연구소 - 재정 진단 & 추천", page_icon="🏢")

st.title("🏢 텅장연구소 - 재정 진단 & 고금리 금융상품 추천기")
st.write("**당신의 통장, 퇴사를 허락할까? 현실적인 재정 판단과 추천을 동시에 제공합니다.**")

# 사용자 입력
with st.container():
    st.header("1️⃣ 재정 상태 입력")

    monthly_expense = st.number_input("월 고정 생활비를 입력하세요 (만원)", min_value=0)
    loan_payment = st.number_input("월 대출 상환액을 입력하세요 (없으면 0)", min_value=0)
    current_savings = st.number_input("현재 통장 잔고를 입력하세요 (만원)", min_value=0)

# 버튼 - 진단 시작
if st.button("퇴사 가능성 진단하기"):
    with st.spinner("🔍 재정 상황 분석 중..."):

        emergency_months = 6
        emergency_fund = 300
        needed_money = (monthly_expense * emergency_months) + (loan_payment * emergency_months) + emergency_fund
        lack_money = needed_money - current_savings

        # 진단 결과 출력
        st.header("2️⃣ 진단 결과")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="필요 금액 (6개월 + 비상금)", value=f"{needed_money:,} 만원")
        with col2:
            st.metric(label="현재 보유 금액", value=f"{current_savings:,} 만원")

        st.write("---")

        if current_savings >= needed_money:
            st.success("🎉 충분한 재정 준비 완료! 퇴사를 고려해볼 수 있습니다.")
        else:
            st.error("🚫 아직 재정 준비가 부족합니다.")
            st.warning(f"💬 부족한 금액: **{lack_money:,} 만원** 더 필요합니다.")

            # 추가 기능: 고금리 상품 실시간 추천
            st.write("---")
            st.subheader("💰 부족한 당신을 위한 고금리 예적금 상품 추천 (실시간 검색)")

            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    tools=[{
                        "type": "web_search_preview",
                        "search_context_size": "low",
                        "user_location": {
                            "type": "approximate",
                            "country": "KR",
                            "city": "Seoul",
                            "region": "Seoul",
                        }
                    }],
                    input="2025년도 한국 시중은행의 고금리 예금, 적금 상품을 알려줘. 상품명, 기본금리, 우대금리, 가입 조건, 가입금액 중심으로 3개 요약해줘. 금리가 높은 순으로 각각 간결하게 요약해줘",
                    tool_choice="required"
                )

                # 🔥 결과 가공해서 카드 스타일로 출력
                result_text = response.output_text

                # 간단히 상품별로 나눈다고 가정하고, 상품별로 구분
                products = result_text.split("\n\n")

                for product in products:
                    if product.strip():
                        with st.container(border=True):
                            st.markdown(f"#### 🏦 {product.strip().splitlines()[0]}")
                            for line in product.strip().splitlines()[1:]:
                                st.markdown(f"- {line}")

            except Exception as e:
                st.error(f"❗ 검색 중 오류 발생: {e}")

                # 고금리 예적금 추천 끝난 뒤에 추가
    st.write("---")
    st.subheader("💡 생활비 절약 꿀팁 추천 (실시간)")

    try:
        saving_tips_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 한국 사람들에게 현실적이고 실천 가능한 생활비 절약 꿀팁을 추천하는 전문가야."},
                {"role": "user", "content": "직장인들이 한국에서 실천할 수 있는 생활비 절약 방법 5가지 알려줘. 각 방법은 제목과 간단한 설명을 함께 적어줘. 1줄로 간결하고 실행 가능해야 해."}
            ]
        )

        saving_tips = saving_tips_response.choices[0].message.content
        tips = saving_tips.split("\n\n")

        for tip in tips:
            if tip.strip():
                with st.container(border=True):
                    st.markdown(f"#### 🛠️ {tip.strip().splitlines()[0]}")
                    for line in tip.strip().splitlines()[1:]:
                        st.markdown(f"- {line}")

    except Exception as e:
        st.error(f"❗ 생활비 절약 꿀팁 검색 중 오류 발생: {e}")

        # 3) 할인 쇼핑몰 추천 카드
    st.write("---")
    st.subheader("🛒 알뜰 쇼핑몰 추천")

    discount_shops = [
        {
            "name": "떠리몰",
            "description": "유통기한 임박 상품을 저렴하게 판매하는 온라인 마켓입니다.",
            "link": "https://www.ttorimall.com/"
        },
        {
            "name": "쿠팡 반품마켓",
            "description": "반품된 제품을 할인된 가격에 판매하는 쿠팡 서비스입니다.",
            "link": "https://pages.coupang.com/f/special-promotion/returnmarket"
        },
        {
            "name": "오늘의집 리퍼마켓",
            "description": "인테리어 용품을 리퍼브 제품으로 저렴하게 구매할 수 있는 마켓입니다.",
            "link": "https://ohou.se/store/refurbished"
        }
    ]

    for shop in discount_shops:
        with st.container(border=True):
            st.markdown(f"#### 🛍️ [{shop['name']}]({shop['link']})")
            st.markdown(f"- {shop['description']}")
    

