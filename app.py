import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 재미나이 API 설정
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

class PnP_UniversalEngine:
    """모든 사물을 상업 화보로 만드는 범용 엔진"""
    
    # 기획안 기반 20여종 테마 (한글명/영어명 혼용)
    THEMES = {
        "시네마틱 누아르(Cinematic Noir)": "도시의 차가운 야경과 강한 명암 대비.",
        "미니어처 디오라마(Miniature Diorama)": "사물을 거대하게, 주변을 작게 만드는 초현실적 연출.",
        "신비로운 꽃의 여신(Ethereal Floral)": "몽환적인 꽃과 파스텔 톤의 우아한 분위기.",
        "크리스마스 박스(Christmas Box)": "따뜻하고 화려한 연말 선물 컨셉.",
        "사이버펑크 크롬(Cyberpunk Chrome)": "미래지향적 금속 질감과 네온 조명.",
        "K-팝 코트사이드(K-pop Courtside)": "스포티하고 에너지 넘치는 럭셔리 무드.",
        "가을 파리 OOTD(Autumn Paris)": "빈티지하고 낭만적인 유럽 거리 감성."
    }

    @staticmethod
    def get_universal_instruction(theme_key):
        theme_desc = PnP_UniversalEngine.THEMES.get(theme_key, "")
        return f"""
        당신은 상업 사진 분석 전문가 '재미나이'입니다.
        1. 업로드된 [상품 사진]의 형태, 재질, 색상을 정밀 분석하세요.
        2. 이 상품이 '{theme_key}'({theme_desc}) 테마의 중심이 되도록 화보 프롬프트를 작성하세요.
        3. 모델 사진이 있다면 모델이 상품을 사용하는 '한국 인플루언서' 화보로, 없다면 '제품 단독 광고'로 구성하세요.
        4. 카메라: Hasselblad 100MP, 85mm f/1.8, 극도의 선명도, 상업용 스튜디오 조명 반영.
        """

# --- UI 설정 ---
st.set_page_config(page_title="Pick & Shot Master", layout="wide")
st.title("📸 픽앤픽(Pick & Shot): 범용 제품 화보 엔진")

if not GOOGLE_API_KEY:
    st.error("⚠️ Secrets에서 GEMINI_API_KEY를 설정해주세요.")
else:
    with st.sidebar:
        st.header("📖 픽앤픽 한글설명(Manual)")
        st.markdown("""
        **1. 사진 업로드(Upload):** 판매할 상품(연필, 그릇, 컵 등 무엇이든) 사진을 올리세요.
        **2. 모델 사진(Optional):** 모델이나 본인 사진을 올리면 인물의 일관성을 유지합니다.
        **3. 테마 선택(Theme):** 기획자가 준비한 예술적 배경 테마를 선택하세요.
        **4. 재미나이 실행(Analyze):** 재미나이가 사물을 분석해 최적의 화보 프롬프트를 만듭니다.
        """)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🖼 이미지 데이터")
        prod_file = st.file_uploader("1. 상품 이미지 (무엇이든 가능)", type=['png', 'jpg', 'jpeg'])
        face_file = st.file_uploader("2. 모델/본인 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
        theme_choice = st.selectbox("기획안 테마 선택", list(PnP_UniversalEngine.THEMES.keys()))

    with col2:
        st.subheader("✨ 재미나이 마스터피스")
        if st.button("🔥 상업용 고퀄리티 프롬프트 생성"):
            if prod_file:
                p_img = Image.open(prod_file)
                # 모델 사진은 선택적 처리
                inputs = [PnP_UniversalEngine.get_universal_instruction(theme_choice), p_img]
                if face_file:
                    inputs.append(Image.open(face_file))
                
                with st.spinner("재미나이가 사물을 분석하여 기획안 테마를 입히는 중..."):
                    response = model.generate_content(inputs)
                    st.success("✅ 고퀄리티 프롬프트가 완성되었습니다!")
                    st.text_area("결과 프롬프트:", value=response.text, height=350)
            else:
                st.error("상품 사진을 최소 한 장 업로드해주세요!")
