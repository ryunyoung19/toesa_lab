import streamlit as st
import openai
import os

# OpenAI 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🏢 퇴사연구소 Streamlit 앱 시작
st.set_page_config(page_title="텅장랩 - 재정 진단 & 추천", page_icon="🏢")

st.title("🏢 텅장랩 - 재정 진단 & 고금리 금융상품 추천기")
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
            st.subheader("💰 부족한 당신을 위한 실시간 고금리 예적금 상품 추천")

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
                    input="2025년도 한국 시중은행의 고금리 예금, 적금 상품을 알려줘. 1.상품명, 2.최고금리(기본금리,  우대금리), 3.가입조건, 4. 가입금액을 바탕으로 3개 간결하게 요약해줘.",
                    tool_choice="required"
                )

                # 🔥 결과 가공해서 카드 스타일로 출력
                result_text = response.output_text

                # 간단히 상품별로 나눈다고 가정하고, 상품별로 구분
                products = result_text.split("\n\n")

                for product in products:
                    if product.strip():
                        with st.container(border=True):
                            st.markdown(f"{product.strip().splitlines()[0]}")
                            for line in product.strip().splitlines()[1:]:
                                st.markdown(f"- {line}")

            except Exception as e:
                st.error(f"❗ 검색 중 오류 발생: {e}")

                # 고금리 예적금 추천 끝난 뒤에 추가
    st.write("---")
    st.subheader("💡 생활비 절약 실시간 꿀팁")

    try:
        saving_tips_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 한국 사람들에게 현실적이고 실천 가능한 생활비 절약 꿀팁을 추천하는 전문가야."},
                {"role": "user", "content": "직장인들이 한국에서 실천할 수 있는 생활비 절약 방법 3가지 알려줘. 각 방법은 제목과 간단한 설명을 함께 적어줘. 1줄로 간결하고 실행 가능해야 해."}
            ]
        )

        saving_tips = saving_tips_response.choices[0].message.content
        tips = saving_tips.split("\n\n")

        for tip in tips:
            if tip.strip():
                with st.container(border=True):
                    st.markdown(f"{tip.strip().splitlines()[0]}")
                    for line in tip.strip().splitlines()[1:]:
                        st.markdown(f"- {line}")

    except Exception as e:
        st.error(f"❗ 생활비 절약 꿀팁 검색 중 오류 발생: {e}")

        # 3) 할인 쇼핑몰 추천 카드
    st.write("---")
    st.subheader("🛒 알뜰 쇼핑몰 추천")

    try:
        discount_shops_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 한국 사람들에게 가성비 좋은 할인 쇼핑몰을 추천하는 전문가야."},
                {"role": "user", "content": "한국에서 잘 알려지지 않은(떠리몰, 쿠팡 반품마켓, 오늘의집 리퍼마켓 등) 알뜰하게 쇼핑할 수 있는 온라인 쇼핑몰 3곳 추천해줘. 각각 1. 쇼핑몰 이름, 2. 간단한 특징 요약, 3. 링크를 짧고 명확하게 알려줘. 문장은 짧게 해줘."}
            ]
        )

        discount_shops_text = discount_shops_response.choices[0].message.content
        shops = discount_shops_text.split("\n\n")

        for shop in shops:
            if shop.strip():
                lines = shop.strip().splitlines()
                if len(lines) >= 3:
                    shop_name = lines[0].replace("1.", "").strip()
                    shop_desc = lines[1].replace("2.", "").strip()
                    shop_link = lines[2].replace("3.", "").strip()

                    with st.container(border=True):
                        st.markdown(f"**{shop_name}**")
                        st.markdown(f"- {shop_desc}")
                        st.markdown(f"[🔗 쇼핑몰 바로가기]({shop_link})")

    except Exception as e:
        st.error(f"❗ 쇼핑몰 추천 검색 중 오류 발생: {e}")
