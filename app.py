import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 재미나이 API 설정 (환경변수)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # 이미지 분석이 가능한 재미나이 1.5 프로 모델 설정
    model = genai.GenerativeModel('gemini-1.5-pro')

class PnP_GeniusEngine:
    """기획안 테마 + 재미나이 멀티모달 분석 엔진"""
    
    THEMES = {
        "Cinematic Noir": "어둡고 고대비가 강한 누아르 스타일, 비 내리는 밤의 도시 불빛.",
        "Miniature Diorama": "틸트-시프트 기법, 실제 사물이 미니어처처럼 보이는 환상적 구도.",
        "Ethereal Floral": "몽환적인 파스텔 톤, 흩날리는 꽃잎과 신비로운 분위기.",
        "Christmas Box Wine": "따뜻한 연말 분위기, 고급 선물 상자와 아늑한 조명.",
        "Cyberpunk Chrome": "미래 지향적 사이버펑크, 금속 반사와 화려한 네온 사인.",
        "K-pop Courtside": "에너지 넘치는 스포티 럭셔리, 선명한 색감과 경기장 조명.",
        "Autumn Paris OOTD": "낭만적인 파리 거리, 클래식한 트렌치 코트와 빈티지 톤."
    }

    @staticmethod
    def get_analysis_prompt(product_name, theme):
        theme_desc = PnP_GeniusEngine.THEMES.get(theme, "")
        return f"""
        당신은 세계 최고의 상업 사진작가이자 재미나이 이미지 전문가입니다.
        첨부된 [상품 사진]의 질감과 [모델 사진]의 얼굴 특징을 정밀하게 분석하세요.
        이후 '{theme}' 테마({theme_desc})에 맞춰 '{product_name}'이 돋보이는 8K 화보용 프롬프트를 작성하세요.
        필수 사양: Hasselblad H6D, 85mm f/1.8 렌즈, 스튜디오 조명, 한국 인플루언서 미학 반영.
        """

# --- UI 레이아웃 ---
st.set_page_config(page_title="Pick & Shot: Gemini Master", layout="wide")
st.title("📸 픽앤픽: 재미나이 마스터 에디션")

if not GOOGLE_API_KEY:
    st.error("⚠️ 관리자 설정에서 GEMINI_API_KEY를 등록해주세요.")
else:
    # 사이드바: 한글 사용 설명서 (무조건 포함)
    with st.sidebar:
        st.header("📘 픽앤픽 활용 가이드")
        st.markdown(f"""
        **1단계: 재미나이에게 데이터 전달**
        * 판매할 상품과 모델 사진을 올리면 **재미나이**가 시각적 특징을 분석합니다.
        
        **2단계: 테마별 지능형 합성**
        * 기획안 테마를 고르면 **재미나이**가 상업 화보급 프롬프트를 생성합니다.
        
        **3단계: 결과 활용**
        * 생성된 프롬프트를 **재미나이(Imagen)** 또는 전문 생성 도구에 입력하여 화보를 완성하세요.
        """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🖼 사진 업로드 (재미나이 분석용)")
        prod_file = st.file_uploader("1. 판매할 상품 이미지 (안경 등)", type=['png', 'jpg', 'jpeg'])
        face_file = st.file_uploader("2. 모델/본인 사진 (일관성 유지용)", type=['png', 'jpg', 'jpeg'])
        
        product_name = st.text_input("제품 이름", "고급 블랙 뿔테 안경")
        theme_choice = st.selectbox("기획안 예술 테마 선택", list(PnP_GeniusEngine.THEMES.keys()))

    with col2:
        st.subheader("✨ 재미나이 마스터피스 생성")
        if st.button("전문가용 프롬프트 생성"):
            if prod_file and face_file:
                p_img = Image.open(prod_file)
                f_img = Image.open(face_file)
                
                with st.spinner("재미나이가 이미지를 분석하고 기획안 테마를 적용 중입니다..."):
                    # 재미나이 멀티모달 분석 요청
                    analysis_prompt = PnP_GeniusEngine.get_analysis_prompt(product_name, theme_choice)
                    response = model.generate_content([analysis_prompt, p_img, f_img])
                    
                    st.success(f"✅ 재미나이가 '{theme_choice}' 테마를 완벽히 분석했습니다!")
                    st.text_area("생성된 마스터피스 프롬프트:", value=response.text, height=300)
                    st.info("💡 이 프롬프트는 당신의 얼굴과 제품의 특징을 모두 포함하고 있습니다.")
            else:
                st.error("상품 사진과 인물 사진을 모두 업로드해 주세요!")
