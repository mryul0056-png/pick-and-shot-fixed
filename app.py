import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 보안 및 버전 강제 설정 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # [수정] v1 정식 버전을 사용하도록 명시적 설정 시도
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Secrets에서 GEMINI_API_KEY를 확인해주세요!")

st.set_page_config(page_title="Pick & Shot - Final Fixed", page_icon="📸")
st.title("📸 픽앤샷 (Version Fixed)")

uploaded_file = st.file_uploader("상품 사진을 올려주세요", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="분석 준비 완료!", use_container_width=True)
    
    if st.button("🚀 숏폼 촬영 지시서 생성"):
        with st.spinner("AI 감독님이 전략을 짜는 중..."):
            try:
                # [핵심 변경] v1beta가 아닌 정식 모델 경로를 직접 찌릅니다.
                # 만약 이게 안되면 'gemini-1.5-flash-latest'로 자동 전환 시도
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                
                response = model.generate_content([
                    "너는 숏폼 전문 감독이야. 이 사진의 상품을 분석해서 15초 촬영 구도와 자막을 짜줘.", 
                    image
                ])
                
                st.subheader("🎬 AI 촬영 지시서")
                st.markdown(response.text)
                st.balloons()
            except Exception as e:
                # 404가 또 날 경우를 대비해 사용 가능한 모델 리스트를 출력해버립니다 (디버깅용)
                st.error(f"실패 원인: {str(e)}")
                if "404" in str(e):
                    st.warning("⚠️ 구글 서버에서 모델을 찾지 못함. 모델명을 'gemini-1.5-flash-latest'로 시도합니다.")
                    try:
                        model_alt = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
                        response_alt = model_alt.generate_content(["상품 분석해줘", image])
                        st.markdown(response_alt.text)
                    except:
                        st.info("지원되는 모델 목록을 확인 중...")
                        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                        st.write("현재 사용 가능한 모델:", models)
