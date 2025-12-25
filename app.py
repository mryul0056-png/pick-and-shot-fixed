import streamlit as st
import google.generativeai as genai  # 반드시 이 라이브러리여야 합니다
from PIL import Image
import os

# --- 디버깅용 (라이브러리 버전 확인) ---
# 이 글자가 화면에 나오면 정상적으로 바뀐 겁니다.
st.sidebar.write(f"Installed SDK: google-generativeai")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Secrets에서 GEMINI_API_KEY를 확인해주세요!")

st.set_page_config(page_title="Pick & Shot - Fixed", page_icon="📸")
st.title("📸 픽앤샷 (Stable Version)")

uploaded_file = st.file_uploader("상품 사진을 올려주세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="분석 준비 완료!", use_container_width=True)
    
    if st.button("🚀 숏폼 촬영 지시서 생성"):
        with st.spinner("AI 감독님이 전략을 짜는 중..."):
            try:
                # 404 에러를 피하는 가장 확실한 모델 선언
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 이미지와 텍스트를 리스트로 전달 (표준 방식)
                response = model.generate_content([
                    "너는 숏폼 전문 감독이야. 이 사진의 상품을 분석해서 15초 촬영 구도와 자막을 짜줘.", 
                    image
                ])
                
                st.subheader("🎬 AI 촬영 지시서")
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                # 에러 메시지 상세 출력
                st.error(f"실패 원인: {str(e)}")
                st.info("여전히 404가 난다면 Streamlit에서 'Manage App' -> 'Reboot App'을 눌러주세요.")
