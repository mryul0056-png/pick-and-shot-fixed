import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. API 설정 및 가용 모델 자동 탐색 (404 에러 방지 핵심)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

def initialize_engine():
    if not GOOGLE_API_KEY:
        return None, "API 키가 설정되지 않았습니다."
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 가용 모델 리스트 확인 및 최적 모델 선택
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Pro 모델 우선, 없으면 Flash 모델 사용
        target_model = next((m for m in available_models if 'gemini-1.5-pro' in m), 
                            next((m for m in available_models if 'gemini-1.5-flash' in m), None))
        
        if target_model:
            return genai.GenerativeModel(target_model), f"연결 성공: {target_model}"
        else:
            return None, "사용 가능한 모델이 없습니다."
    except Exception as e:
        # 리스트 확인 실패 시 수동 지정 시도 (Fallback)
        return genai.GenerativeModel('gemini-1.5-flash'), "표준 엔진(Flash)으로 긴급 연결됨"

model, status_msg = initialize_engine()

class PnP_StudioEngine:
    """3대 산출물(제품/기획/모델) 통합 생성 로직"""
    THEMES = {
        "시네마틱 누아르(Cinematic Noir)": "도시의 차가운 야경과 강한 명암 대비.",
        "미니어처 디오라마(Miniature Diorama)": "사물을 거대하게, 주변 피규어는 작게 배치하는 연출.",
        "신비로운 꽃의 여신(Ethereal Floral)": "몽환적인 파스텔 톤과 꽃의 우아한 조화.",
        "크리스마스 박스(Christmas Box)": "따뜻하고 화려한 연말 선물 컨셉.",
        "사이버펑크 크롬(Cyberpunk Chrome)": "미래지향적 금속 질감과 네온 조명."
    }

    @staticmethod
    def get_system_instruction(theme_key, product_name):
        return f"""
        당신은 상업 사진 작가이자 마케팅 전문가입니다. 반드시 아래 3가지 섹션으로 구분하여 응답하세요.

        ### [SECTION 1: 제품 단독 화보]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트. (인물 제외)
        사양: Hasselblad 100MP, 85mm f/1.8, razor-sharp focus, 8k resolution.

        ### [SECTION 2: 상세페이지 기획]
        제품 특징 분석 및 상세페이지용 마케팅 카피 문구 (한글). 
        고객의 구매 욕구를 자극하는 전문적인 기획 내용 포함.

        ### [SECTION 3: 모델 기반 화보]
        업로드된 인물 사진이 {product_name}을 자연스럽게 활용하는 화보용 영어 프롬프트.
        인물의 특징을 유지하며 테마와 조화를 이룰 것.
        """

# --- UI 레이아웃 개편 ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 설정 및 입력 (상단 정렬 방해 방지)
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.markdown(f"**엔진 상태:** `{status_msg}`")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "프리미엄 제품")
    theme_choice = st.selectbox("기획안 테마", list(PnP_StudioEngine.THEMES.keys()))
    generate_btn = st.button("🔥 마스터피스 생성", use_container_width=True)

# 메인 화면: 결과 중심 정렬
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if not model:
        st.error(status_msg)
    elif prod_file:
        p_img = Image.open(prod_file)
        instruction = PnP_StudioEngine.get_system_instruction(theme_choice, product_name)
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 엔진이 정밀 기획안을 작성 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 결과물을 탭으로 깔끔하게 분리
                tab1, tab2, tab3 = st.tabs(["🖼 제품 단독 화보", "📝 상세페이지 기획", "👤 모델 기반 화보"])
                
                with tab1:
                    st.subheader("제품 + 배경 중심 프롬프트")
                    st.code(content.split("### [SECTION 2]")[0].replace("### [SECTION 1: 제품 단독 화보]", "").strip(), language='text')
                
                with tab2:
                    st.subheader("마케팅 카피 및 상세 기획")
                    if "### [SECTION 2]" in content:
                        st.markdown(content.split("### [SECTION 2]")[1].split("### [SECTION 3]")[0].strip())
                
                with tab3:
                    st.subheader("인물 일관성 기반 프롬프트")
                    if "### [SECTION 3]" in content:
                        st.code(content.split("### [SECTION 3]")[1].strip(), language='text')
                
                st.success("✅ 모든 기획안이 생성되었습니다.")
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 이미지를 먼저 업로드해주세요.")
