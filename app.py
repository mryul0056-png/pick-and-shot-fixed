import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 자가 치유형 AI 엔진 로직 (404 에러 원천 봉쇄)
def get_verified_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "API 키가 Secrets에 설정되지 않았습니다."
    
    try:
        genai.configure(api_key=api_key)
        # 현재 사용 가능한 모든 모델 리스트 확보
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: Pro 모델, 2순위: Flash 모델 자동 선택
        target_model_name = next((m for m in available_models if 'gemini-1.5-pro' in m), 
                                 next((m for m in available_models if 'gemini-1.5-flash' in m), None))
        
        if target_model_name:
            return genai.GenerativeModel(target_model_name), f"엔진 가동 중: {target_model_name.split('/')[-1]}"
        else:
            return None, "사용 가능한 재미나이 모델을 찾을 수 없습니다."
    except Exception as e:
        return None, f"인증 오류: {str(e)}"

# 2. UI 세션 상태 및 엔진 초기화
model, engine_status = get_verified_model()

# --- UI 레이아웃 개편 (사이드바 정렬) ---
st.set_page_config(page_title="Pick & Shot Professional", layout="wide")

with st.sidebar:
    st.title("⚙️ 픽앤픽 설정 센터")
    st.caption(engine_status)
    st.markdown("---")
    
    # 상품 및 모델 이미지 업로드
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    
    # 기획안 기반 20여종 테마 중 핵심 선택
    theme_choice = st.selectbox("기획 테마 선택", [
        "시네마틱 누아르(Cinematic Noir)", 
        "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", 
        "크리스마스 박스(Christmas Box Wine)", 
        "사이버펑크 크롬(Cyberpunk Chrome)",
        "가을 파리 OOTD(Autumn Paris)"
    ])
    
    generate_btn = st.button("🔥 마스터피스 기획 시작", use_container_width=True)
    
    st.markdown("---")
    st.header("📖 서비스 매뉴얼")
    st.info("재미나이가 사진을 정밀 분석하여 상업용 설계도(프롬프트)와 마케팅 카피를 작성합니다.")

# 메인 결과 화면
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if not model:
        st.error(engine_status)
    elif prod_file:
        p_img = Image.open(prod_file)
        
        # 3가지 산출물을 명확히 구분하는 지시어 (천재 개발자 모드)
        instruction = f"""
        당신은 상업 사진 작가이자 마케팅 전문가입니다. 업로드된 이미지를 분석하여 다음 3개 섹션으로 글을 작성하세요.
        
        ### [SECTION 1: PRODUCT ONLY PROMPT]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트. (모델 제외)
        사양: Hasselblad 100MP, 85mm f/1.8, razor-sharp textures, 8k resolution 필수 포함.

        ### [SECTION 2: 상세페이지 마케팅 기획]
        이 상품을 위한 전문적인 한글 마케팅 문구와 기획 의도. 
        고객의 감성을 자극하는 카피라이팅을 상세히 작성할 것.

        ### [SECTION 3: MODEL BASED PROMPT]
        업로드된 인물 사진의 특징을 유지하며 {product_name}을 자연스럽게 착용한 화보용 영어 프롬프트.
        """
        
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 AI가 마스터피스를 기획 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 탭으로 결과물 깔끔하게 분리
                tab1, tab2, tab3 = st.tabs(["🖼 제품 단독 화보", "📝 상세페이지 기획", "👤 모델 기반 화보"])
                
                with tab1:
                    st.subheader("제품 + 배경 중심 프롬프트")
                    st.code(content.split("### [SECTION 2]")[0].replace("### [SECTION 1: PRODUCT ONLY PROMPT]", "").strip(), language='text')
                
                with tab2:
                    st.subheader("상세페이지 마케팅 카피")
                    if "### [SECTION 2]" in content:
                        st.markdown(content.split("### [SECTION 2]")[1].split("### [SECTION 3]")[0].strip())
                
                with tab3:
                    st.subheader("인물 일관성 기반 프롬프트")
                    if "### [SECTION 3]" in content:
                        st.code(content.split("### [SECTION 3]")[1].strip(), language='text')
                
                st.success("✅ 모든 분석이 완료되었습니다.")
            except Exception as e:
                st.error(f"실행 중 오류 발생: {str(e)}")
    else:
        st.error("상품 이미지를 업로드해 주세요.")
