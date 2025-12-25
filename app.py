import streamlit as st
import google.generativeai as genai
from PIL import Image

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Secrets 설정 확인 필요")

st.set_page_config(page_title="Pick & Shot - Final", page_icon="📸")
st.title("📸 픽앤샷 (2025 Standard)")

uploaded_file = st.file_uploader("상품 사진을 올려주세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="준석 준비 완료!", use_container_width=True)
    
    if st.button("🚀 숏폼 촬영 지시서 생성"):
        with st.spinner("AI 감독님이 전략을 짜는 중..."):
            try:
                # [수정] 개발자님의 리스트 0번에 있는 가장 확실한 모델명을 사용합니다.
                # 'gemini-2.5-flash' 혹은 'gemini-flash-latest' 둘 다 가능합니다.
                model = genai.GenerativeModel('gemini-2.5-flash') 
                
                response = model.generate_content([
                    "너는 숏폼 전문 감독이야. 이 사진의 상품을 분석해서 15초 촬영 구도와 자막을 짜줘. 한국어로 상세히 작성해줘.", 
                    image
                ])
                
                st.subheader("🎬 AI 촬영 지시서")
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
                st.info("이래도 안 되면 모델명을 'gemini-flash-latest'로 바꿔보세요.")
