import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 최신 모델 엔진 설정 (404 에러 방지용 공식 명칭)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # 가장 안정적이고 사양이 높은 최신 모델 지정
    model = genai.GenerativeModel('models/gemini-1.5-pro')

class PnP_MasterArchitect:
    """3대 산출물을 생성하는 상업 기획 엔진"""
    THEMES = {
        "시네마틱 누아르(Cinematic Noir)": "도시의 차가운 야경과 강한 명암 대비.",
        "미니어처 디오라마(Miniature Diorama)": "사물을 거대하게, 주변 피규어는 작게 배치하는 초현실 연출.",
        "신비로운 꽃의 여신(Ethereal Floral)": "몽환적인 파스텔 톤, 제품을 감싸는 꽃잎과 부드러운 채광.",
        "크리스마스 박스(Christmas Box)": "따뜻하고 화려한 연말 선물 컨셉.",
        "사이버펑크 크롬(Cyberpunk Chrome)": "미래지향적 금속 질감과 사이언/마젠타 네온 조명.",
        "K-팝 코트사이드(K-pop Courtside)": "스포티 럭셔리, 선명한 원색 대비와 경기장 조명 효과.",
        "가을 파리 OOTD(Autumn Paris)": "빈티지 브라운 톤, 유럽 거리의 부드러운 일몰 광선."
    }

    @staticmethod
    def get_system_prompt(product_name, theme_key):
        return f"""
        당신은 세계 최고의 '상업 사진 기획자'입니다. 
        사용자가 올린 사진을 분석하여 다음 3가지 항목을 구분하여 작성하세요.

        [PART 1: PRODUCT ONLY]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트. (모델 제외)
        
        [PART 2: MARKETING PLAN]
        상세페이지용 제품 특징 분석 및 고객을 유혹하는 한글 마케팅 카피 문구.

        [PART 3: MODEL PHOTO]
        업로드된 인물 사진이 {product_name}을 자연스럽게 활용하는 화보용 영어 프롬프트.
        
        * 공통 사양: Hasselblad 100MP, 85mm f/1.8, razor-sharp focus, 8k resolution 필수 포함.
        """

# --- UI/UX 레이아웃 (정렬 및 정돈) ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 입력 및 설정 영역 (상단 정렬 방해 방지)
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    theme_choice = st.selectbox("기획 테마 선택", list(PnP_MasterArchitect.THEMES.keys()))
    
    generate_btn = st.button("🔥 마스터피스 기획 시작", use_container_width=True)
    
    st.markdown("---")
    st.caption("현재 구동 엔진: Gemini 1.5 Pro (최상위 사양)")

# 메인 화면: 결과 중심 정렬
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")
st.write("모델은 기획을 하고, 당신은 프롬프트를 가져가기만 하면 됩니다.")

if generate_btn:
    if not GOOGLE_API_KEY:
        st.error("API Key가 등록되지 않았습니다.")
    elif prod_file:
        p_img = Image.open(prod_file)
        instruction = PnP_MasterArchitect.get_system_prompt(product_name, theme_choice)
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 프로 모델이 정밀 기획 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 결과물을 탭으로 분리하여 깔끔하게 정렬
                tab1, tab2, tab3 = st.tabs(["🖼 제품 단독 화보", "📝 상세페이지 기획안", "👤 모델 기반 화보"])
                
                with tab1:
                    st.subheader("제품 및 배경 중심 프롬프트")
                    st.code(content.split("[PART 2]")[0].replace("[PART 1]", "").strip(), language='text')
                
                with tab2:
                    st.subheader("상세페이지 마케팅 및 기획안")
                    if "[PART 2]" in content:
                        st.markdown(content.split("[PART 2]")[1].split("[PART 3]")[0].strip())
                
                with tab3:
                    st.subheader("인물 일관성 유지 프롬프트")
                    if "[PART 3]" in content:
                        st.code(content.split("[PART 3]")[1].strip(), language='text')
                
                st.success("✅ 기획안 정렬이 완료되었습니다. 각 탭을 확인하세요.")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
    else:
        st.error("상품 사진을 업로드해 주세요.")
else:
    st.info("좌측 사이드바에서 이미지를 올리고 테마를 선택한 후 버튼을 눌러주세요.")
