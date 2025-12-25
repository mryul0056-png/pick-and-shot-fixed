import streamlit as st
from google import genai
from PIL import Image

# --- 1. 보안 설정 (최신 google-genai 방식) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("⚠️ 설정에서 API 키를 입력해주세요! (Settings > Secrets)")

st.set_page_config(page_title="Pick & Shot - 픽앤샷", page_icon="📸")
st.title("📸 픽앤샷 (Pick & Shot)")

# --- 2. 메인 로직 ---
uploaded_file = st.file_uploader("상품 사진을 올려주세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="분석 준비 완료!", use_container_width=True)
    
    if st.button("🚀 숏폼 촬영 지시서 생성"):
        with st.spinner("AI 감독님이 전략을 짜는 중..."):
            try:
                # 이 방식은 404 에러 없이 gemini-1.5-flash를 뚫어버립니다.
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=["너는 숏폼 전문 감독이야. 이 사진의 상품을 분석해서 15초 촬영 구도와 자막을 짜줘.", image]
                )
                st.write(response.text)
                st.balloons()
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
