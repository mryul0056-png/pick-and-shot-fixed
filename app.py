import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 재미나이(Gemini) API 설정
# 배포 환경의 Secrets에 GEMINI_API_KEY를 꼭 등록해주세요.
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

class PnP_GeniusEngine:
    """기획안 테마 + 재미나이 지능 결합 엔진"""
    
    # 기획안 기반 테마 리스트: 한글명(EnglishName) 형식
    THEMES = {
        "시네마틱 누아르(Cinematic Noir)": "어둡고 고대비가 강한 누아르 스타일, 비 내리는 밤의 도시 불빛.",
        "미니어처 디오라마(Miniature Diorama)": "실제 사물이 아주 작은 미니어처처럼 보이는 틸트-시프트 기법.",
        "신비로운 꽃의 여신(Ethereal Floral)": "몽환적인 파스텔 톤, 흩날리는 꽃잎과 여신 같은 분위기.",
        "크리스마스 박스(Christmas Box Wine)": "따뜻한 연말 분위기, 고급 선물 상자와 아늑한 조명.",
        "사이버펑크 크롬(Cyberpunk Chrome)": "미래 지향적 느낌, 차가운 금속 반사와 네온 사인.",
        "K-팝 코트사이드(K-pop Courtside)": "에너지 넘치는 스포티 럭셔리, 선명한 색감과 경기장 조명.",
        "가을 파리 OOTD(Autumn Paris OOTD)": "낭만적인 파리 거리, 클래식한 트렌치 코트와 빈티지 톤."
    }

    @staticmethod
    def get_analysis_instruction(product_name, theme):
        theme_desc = PnP_GeniusEngine.THEMES.get(theme, "")
        return f"""
        당신은 상업 사진 분석 전문가 '재미나이'입니다.
        1. 업로드된 [상품 사진]의 디자인과 [모델 사진]의 인물 특징을 정밀 분석하세요.
        2. '{theme}'({theme_desc}) 테마에 맞춰 '{product_name}'이 돋보이는 8K 화보용 프롬프트를 생성하세요.
        3. 모델은 한국 인플루언서 스타일로 설정하고, 안경의 질감과 반사가 완벽하게 표현되도록 지시하세요.
        4. 사양: Hasselblad 100MP, 85mm f/1.8, 스튜디오 조명, 하이엔드 텍스처.
        """

# --- UI 레이아웃 (한국어 최적화) ---
st.set_page_config(page_title="Pick & Shot: Master", layout="wide")
st.title("📸 픽앤픽(Pick & Shot): 재미나이 마스터 에디션")

if not GOOGLE_API_KEY:
    st.error("⚠️ 관리자 설정(Secrets)에서 GEMINI_API_KEY를 등록해야 재미나이가 작동합니다.")
else:
    # 사이드바: 한국어 전용 활용 가이드
    with st.sidebar:
        st.header("📖 픽앤픽 활용 설명서")
        st.markdown("""
        **1단계: 사진 업로드**
        * 판매할 상품(안경 등)과 모델(본인) 사진을 올리세요.
        
        **2단계: 재미나이 분석**
        * **재미나이**가 사진을 보고 기획안 테마를 입힙니다.
        
        **3단계: 결과 활용**
        * 생성된 프롬프트를 복사하여 **재미나이(Imagen)**나 미드저니 등에 입력하세요.
        """)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🖼 사진 업로드")
        prod_file = st.file_uploader("1. 상품 이미지 (안경 등)", type=['png', 'jpg', 'jpeg'])
        face_file = st.file_uploader("2. 모델/본인 사진 (일관성 유지)", type=['png', 'jpg', 'jpeg'])
        
        product_name = st.text_input("제품 이름 입력", "고급 블랙 뿔테 안경")
        theme_choice = st.selectbox("기획안 테마 선택", list(PnP_GeniusEngine.THEMES.keys()))

    with col2:
        st.subheader("✨ 재미나이 마스터피스 결과")
        if st.button("🔥 전문가용 화보 프롬프트 생성"):
            if prod_file and face_file:
                p_img = Image.open(prod_file)
                f_img = Image.open(face_file)
                
                with st.spinner("재미나이가 기획안 테마를 적용하여 분석 중입니다..."):
                    # 재미나이 멀티모달 분석
                    instruction = PnP_GeniusEngine.get_analysis_instruction(product_name, theme_choice)
                    response = model.generate_content([instruction, p_img, f_img])
                    
                    st.success(f"✅ '{theme_choice}' 테마 분석 완료!")
                    st.text_area("이 프롬프트를 복사하세요:", value=response.text, height=350)
                    st.info("💡 팁: 재미나이가 분석한 이 프롬프트는 인물 일관성과 상품 디테일을 모두 담고 있습니다.")
            else:
                st.error("상품과 인물 사진을 모두 업로드해주세요!")
