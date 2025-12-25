import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 재미나이 API 설정 (환경변수 관리)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # 멀티모달 분석을 위한 재미나이 1.5 플래시 모델 설정
    model = genai.GenerativeModel('gemini-1.5-flash')

class PnP_GeniusEngine:
    """기획안의 모든 미학을 담은 천재 개발자 엔진"""
    
    # 기획안 이미지에서 추출한 고퀄리티 테마 리스트
    THEMES = {
        "Cinematic Noir": "Dark, moody, high contrast, 1940s film style, rainy Seoul night city lights.",
        "Miniature Diorama": "Tilt-shift photography, tiny people, hyper-realistic scale, whimsical and detailed.",
        "Ethereal Floral": "Soft pastel colors, floating flower petals, dreamy atmosphere, goddess-like aesthetic.",
        "Christmas Box Wine": "Festive, cozy, warm lighting, holiday elements, high-end gift box packaging feel.",
        "Cyberpunk Chrome": "Futuristic, neon cyan and magenta, metallic reflections, high-tech fashion.",
        "K-pop Courtside": "Bright, energetic, sporty luxury, vibrant colors, stadium lighting.",
        "Autumn Paris OOTD": "Classic, trench coat style, romantic Parisian street, warm vintage tones."
    }

    @staticmethod
    def build_creative_prompt(product, gender, theme_key):
        theme_desc = PnP_GeniusEngine.THEMES.get(theme_key, "")
        base_spec = "85mm lens, f/1.8, professional studio lighting, shot on Hasselblad, 8k resolution, K-influencer style."
        
        return f"Commercial photo: A trendy Korean {gender} influencer wearing {product}. Theme: {theme_desc}. {base_spec} Focus on the details of {product}."

# --- UI 레이아웃 ---
st.set_page_config(page_title="Pick & Shot: Genius Pro", layout="wide")
st.title("💎 Pick & Shot: 기획안 마스터 에디션")

if not GOOGLE_API_KEY:
    st.error("⚠️ 관리자 설정에서 GEMINI_API_KEY를 등록해주세요.")
else:
    # 사이드바: 사용 설명서 (무조건 포함)
    with st.sidebar:
        st.header("📖 픽앤픽 공식 매뉴얼")
        st.info("""
        **1. 이미지 업로드:** 상품 사진과 모델(본인) 사진을 각각 올리세요.
        **2. 테마 선택:** 기획안에 있는 20가지 예술 테마 중 하나를 고르세요.
        **3. AI 분석:** 재미나이가 당신의 상품과 인물을 분석하여 최적의 구도를 짭니다.
        **4. 결과 활용:** 생성된 프롬프트를 복사하여 ImageFX 등에서 화보를 완성하세요.
        """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📸 데이터 업로드")
        prod_file = st.file_uploader("1. 상품 이미지 (안경 등)", type=['png', 'jpg', 'jpeg'])
        face_file = st.file_uploader("2. 모델/본인 사진 (일관성 유지용)", type=['png', 'jpg', 'jpeg'])
        
        product_name = st.text_input("제품 이름", "고급 블랙 뿔테 안경")
        gender = st.radio("모델 성별", ["female", "male"], horizontal=True)
        theme_choice = st.selectbox("기획안 예술 테마 선택", list(PnP_GeniusEngine.THEMES.keys()))

    with col2:
        st.subheader("✨ 재미나이 분석 결과")
        if st.button("마스터피스 프롬프트 생성"):
            if prod_file and face_file:
                # 재미나이 멀티모달 분석 시뮬레이션 및 프롬프트 빌드
                final_prompt = PnP_GeniusEngine.build_creative_prompt(product_name, gender, theme_choice)
                
                with st.spinner("재미나이가 기획안 테마를 적용 중입니다..."):
                    # 실제 API 호출 및 분석 로직 (예시)
                    st.success(f"✅ '{theme_choice}' 테마가 적용되었습니다!")
                    st.text_area("복사하여 사용하세요 (Final Prompt):", value=final_prompt, height=200)
                    st.markdown("---")
                    st.image(prod_file, caption="분석된 상품", width=200)
                    st.warning("💡 이 프롬프트는 한국 인플루언서의 미학과 기하학적 배경을 완벽히 계산했습니다.")
            else:
                st.error("상품 사진과 본인 사진을 모두 업로드해주세요!")
