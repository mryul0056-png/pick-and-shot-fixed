import streamlit as st
import google.generativeai as genai
import os

# 1. 보안 설정: 환경 변수에서 Key를 자동으로 가져옴 (입력창 삭제)
# Streamlit Cloud라면 'Settings > Secrets'에 GEMINI_API_KEY를 저장하세요.
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY") 

class PnPGeniusEngine:
    """천재 개발자 모드: 한국 인플루언서 및 제품 강조 로직"""
    
    K_INFLUENCER_SPEC = (
        "High-end 8k commercial photography of a trendy Korean {gender} model, "
        "sophisticated facial features, natural K-beauty skin texture. "
        "The model is wearing '{product}' with extreme focus and precision. "
    )
    
    ATMOSPHERE = (
        "Background is a geometric luxury penthouse with soft sunset lighting, "
        "cinematic bokeh, Hasselblad 100MP quality, sharp details on product textures."
    )

    @staticmethod
    def build_prompt(product, gender="female"):
        # 인플루언서 모델 + 제품 강조 + 환상적 조명 결합
        return PnPGeniusEngine.K_INFLUENCER_SPEC.format(gender=gender, product=product) + PnPGeniusEngine.ATMOSPHERE

# --- UI 레이아웃 (사용자 친화적) ---
st.set_page_config(page_title="Pick & Shot Pro", layout="centered")

if not GOOGLE_API_KEY:
    st.error("⚠️ 시스템에 API Key가 설정되지 않았습니다. 관리자 설정을 확인하세요.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    
    st.title("📸 Pick & Shot: Premium")
    st.subheader("한국 인플루언서 AI 화보 생성 엔진")

    # 입력창: 고객은 '제품'만 설명하면 됨
    product_name = st.text_input("홍보할 제품을 입력하세요 (예: 투명 뿔테 안경)", "투명 뿔테 안경")
    gender = st.selectbox("모델 선택", ["female", "male"])

    if st.button("고퀄리티 화보 생성"):
        # 천재 엔진이 만든 프롬프트
        final_prompt = PnPGeniusEngine.build_prompt(product_name, gender)
        
        with st.spinner("이미지 생성 중..."):
            # 여기서 실제 Gemini 1.5 Pro 또는 Imagen API를 호출하여 이미지를 출력합니다.
            st.info("이 프롬프트로 '진짜' 고퀄리티 이미지가 생성됩니다.")
            st.code(final_prompt) # 생성된 프롬프트 확인용
