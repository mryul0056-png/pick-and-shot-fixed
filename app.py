import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 보안 설정 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Secrets에서 GEMINI_API_KEY를 확인해주세요!")

st.set_page_config(page_title="Pick & Shot - Final", page_icon="📸")
st.title("📸 픽앤샷 (Fixed Version)")

uploaded_file = st.file_uploader("상품 사진을 올려주세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="분석 준비 완료!", use_container_width=True)
    
    if st.button("🚀 숏폼 촬영 지시서 생성"):
        with st.spinner("AI 감독님이 전략을 짜는 중..."):
            try:
                # [핵심] 리스트(image_ef3501.png)에서 확인된 정확한 이름으로 수정
                # 'gemini-1.5-flash-latest' 또는 더 최신인 'gemini-2.0-flash' 사용 가능
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                response = model.generate_content([
                    "너는 숏폼 전문 감독이야. 이 사진의 상품을 분석해서 15초 촬영 구도와 자막을 짜줘. 한국어로 답해줘.", 
                    image
                ])
                
                st.subheader("🎬 AI 촬영 지시서")
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
