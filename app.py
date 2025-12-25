import streamlit as st
import google.generativeai as genai
import os

class GeniusPromptEngine:
    """세상의 아름다움과 기하학적 미학을 담는 천재 프롬프트 엔진"""
    
    # 1. 상업용 사진의 정점: 하이엔드 카메라 스펙 및 조명
    TECH_SPEC = (
        "shot on Hasselblad H6D, 100MP, 80mm f/1.9 lens, crisp sharp focus, "
        "8k UHD, Ray-tracing, Unreal Engine 5.4 render style, cinematic 3-point lighting, "
        "volumetric fog, Tyndall effect, subsurface scattering for skin."
    )

    # 2. 한국인 AI 인플루언서 모델 정의
    K_MODEL = {
        "female": "a trendy Korean female influencer, sophisticated features, flawless skin, high-fashion makeup, alluring gaze, Vogue editorial pose.",
        "male": "a stylish Korean male influencer, sharp jawline, charismatic look, K-pop aesthetic, trendy haircut, professional male model pose."
    }

    # 3. 환상적이고 기하학적인 배경 테마
    BACKGROUNDS = {
        "Geometric": "minimalist architectural space with golden ratio shadows, abstract geometric shapes, luxury marble textures.",
        "Fantastic": "ethereal dreamscape, floating crystal elements, sunset glow through iridescent clouds, surrealist floral installation.",
        "Urban Luxury": "Seoul city night view from a penthouse, neon reflections, glass and steel futuristic interior."
    }

    @staticmethod
    def craft_masterpiece(product_desc, gender="female", bg_style="Geometric"):
        """사용자의 제품을 천재적 예술 작품으로 변환"""
        model_desc = GeniusPromptEngine.K_MODEL.get(gender)
        bg_desc = GeniusPromptEngine.BACKGROUNDS.get(bg_style)
        
        # 제품이 주인공이 되도록 하는 핵심 프롬프트 구성
        prompt = (
            f"A high-end commercial advertisement featuring {model_desc} wearing the masterpiece '{product_desc}'. "
            f"The {product_desc} is the primary focus with ultra-sharp detail and reflections. "
            f"Background is {bg_desc}. {GeniusPromptEngine.TECH_SPEC}. "
            f"Composition follows the golden ratio, aesthetically perfect, vibrant yet sophisticated color grading."
        )
        return prompt

# --- Streamlit UI ---
st.set_page_config(page_title="Pick & Shot: Genius Edition", layout="wide")
st.title("✨ Pick & Shot: 천재 개발자 에디션")
st.write("당신의 제품을 세계 최고의 상업 화보로 재탄생시킵니다.")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎨 기획 및 설정")
        product = st.text_input("업로드한 제품 설명", placeholder="예: 무광 블랙 뿔테 안경")
        gender = st.radio("모델 성별", ["female", "male"], horizontal=True)
        bg_style = st.selectbox("배경 테마", ["Geometric", "Fantastic", "Urban Luxury"])
        
        if st.button("예술적 이미지 생성"):
            if product:
                # 천재 엔진 가동
                final_prompt = GeniusPromptEngine.craft_masterpiece(product, gender, bg_style)
                
                with st.spinner("미학적 렌더링 진행 중..."):
                    st.session_state.current_prompt = final_prompt
                    st.info(f"💎 생성된 마스터피스 프롬프트:\n\n{final_prompt}")
                    # 실제 이미지 생성 API 연동 시 이 final_prompt를 사용합니다.
            else:
                st.error("제품 설명을 입력해주세요.")

    with col2:
        st.subheader("🖼 마스터피스 프리뷰")
        if 'current_prompt' in st.session_state:
            st.success("2, 3, 4번과 같은 압도적 고퀄리티 이미지가 이 프롬프트를 통해 생성됩니다.")
            st.image("https://via.placeholder.com/800x1000.png?text=High-End+AI+Commercial+Preview", use_column_width=True)
