import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. AI 엔진(모델) 자동 탐색 로직 - 404 에러 원천 차단
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

def setup_engine():
    if not GOOGLE_API_KEY:
        return None, "API Key가 설정되지 않았습니다."
    genai.configure(api_key=GOOGLE_API_KEY)
    try:
        # 가용한 모든 모델 중 텍스트 생성이 가능한 모델 리스트 확보
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Pro 모델을 먼저 찾고, 없으면 Flash 모델로 자동 전환 (Fallback)
        target = next((m for m in models if 'gemini-1.5-pro' in m), 
                      next((m for m in models if 'gemini-1.5-flash' in m), None))
        if target:
            return genai.GenerativeModel(target), f"연결 성공: {target}"
        return None, "사용 가능한 AI 엔진을 찾을 수 없습니다."
    except:
        return genai.GenerativeModel('gemini-1.5-flash'), "안전 모드(Flash)로 자동 연결됨"

model, status_msg = setup_engine()

# --- UI/UX 레이아웃 개편 ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 모든 설정과 입력을 한곳으로 정렬
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.caption(status_msg)
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명(Product Name)", "프리미엄 제품")
    theme_choice = st.selectbox("기획 테마(Theme)", [
        "시네마틱 누아르(Cinematic Noir)", 
        "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", 
        "크리스마스 박스(Christmas Box Wine)", 
        "사이버펑크 크롬(Cyberpunk Chrome)"
    ])
    generate_btn = st.button("🔥 기획안 및 프롬프트 생성", use_container_width=True)
    st.markdown("---")
    st.header("📖 한글설명(Manual)")
    st.info("재미나이 AI가 사진을 분석하여 상업용 설계도를 작성합니다. 이미지는 직접 생성하지 않습니다.")

# 메인 화면: 결과 중심 정렬
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if not model: st.error(status_msg)
    elif prod_file:
        p_img = Image.open(prod_file)
        # AI에게 3가지 섹션 작성을 강제하는 지시어
        instruction = f"""
        당신은 상업 사진 작가입니다. 업로드된 사진을 분석하여 반드시 아래 3개 섹션으로 구분된 텍스트를 작성하세요.
        
        [SECTION 1: PRODUCT ONLY]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트. (모델 제외, Hasselblad 100MP 사양 포함)

        [SECTION 2: MARKETING COPY]
        이 상품을 위한 상세페이지용 한글 마케팅 문구와 상세 기획 의도.

        [SECTION 3: MODEL PHOTO]
        업로드된 인물 사진이 {product_name}을 자연스럽게 활용하는 화보용 영어 프롬프트.
        """
        inputs = [instruction, p_img]
        if face_file: inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 AI가 설계도를 작성 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 탭을 사용하여 결과 정돈
                tab1, tab2, tab3 = st.tabs(["🖼 제품 프롬프트", "📝 상세페이지 기획", "👤 모델 프롬프트"])
                
                with tab1:
                    st.subheader("제품 및 배경 중심 설계도")
                    st.code(content.split("[SECTION 2]")[0].replace("[SECTION 1: 제품 단독 프롬프트]", "").strip(), language='text')
                with tab2:
                    st.subheader("마케팅 카피 및 상세 기획")
                    if "[SECTION 2]" in content:
                        st.markdown(content.split("[SECTION 2]")[1].split("[SECTION 3]")[0].strip())
                with tab3:
                    st.subheader("인물 일관성 유지 설계도")
                    if "[SECTION 3]" in content:
                        st.code(content.split("[SECTION 3]")[1].strip(), language='text')
                st.success("✅ 기획안 작성이 완료되었습니다.")
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 이미지를 업로드해 주세요.")
