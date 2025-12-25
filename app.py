import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 재미나이 API 설정 (환경변수 관리)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

def get_working_engine():
    """글을 써줄 AI 엔진(모델)을 안전하게 연결"""
    if not GOOGLE_API_KEY:
        return None, "API 키가 등록되지 않았습니다."
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 404 에러를 방지하기 위해 가용 모델 리스트에서 직접 찾음
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 최신 모델 순서대로 자동 탐색
        target = next((m for m in available_models if 'gemini-1.5-pro' in m), 
                      next((m for m in available_models if 'gemini-1.5-flash' in m), None))
        if target:
            return genai.GenerativeModel(target), f"AI 엔진 연결 성공: {target}"
        return None, "사용 가능한 AI 엔진을 찾을 수 없습니다."
    except Exception as e:
        return genai.GenerativeModel('gemini-1.5-flash'), "표준 엔진으로 긴급 연결됨"

model, status_msg = get_working_engine()

# --- UI 레이아웃 개편 ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 입력 및 설명서 (상단 정렬 방해 금지)
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.caption(status_msg)
    st.markdown("---")
    
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "프리미엄 제품")
    
    theme_choice = st.selectbox("기획 테마 선택", [
        "시네마틱 누아르(Cinematic Noir)", 
        "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", 
        "크리스마스 박스(Christmas Box)", 
        "사이버펑크 크롬(Cyberpunk Chrome)"
    ])
    
    generate_btn = st.button("🔥 기획안 및 프롬프트 생성", use_container_width=True)
    
    st.markdown("---")
    st.header("📖 한글설명(Manual)")
    st.info("""
    1. 사진을 올리면 재미나이가 상품의 특징을 읽습니다.
    2. 선택한 테마에 맞춰 '글'로 된 기획안과 프롬프트를 씁니다.
    3. 결과물은 3개의 탭에 나뉘어 출력됩니다.
    """)

# 메인 화면: 결과 중심 정렬
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")
st.write("이미지 생성기가 아닙니다. 당신을 위한 **최고의 상업용 설계도**를 만듭니다.")

if generate_btn:
    if not model:
        st.error(status_msg)
    elif prod_file:
        p_img = Image.open(prod_file)
        # AI에게 글을 쓰라고 시키는 명령문 (이미지 생성X, 텍스트 생성O)
        instruction = f"""
        당신은 상업 사진 작가입니다. 업로드된 사진을 분석하여 다음 3개 섹션으로 '글'을 작성하세요.
        
        [SECTION 1: 제품 단독 프롬프트]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트.

        [SECTION 2: 마케팅 상세 기획]
        이 상품을 위한 상세페이지용 한글 마케팅 문구와 기획 의도.

        [SECTION 3: 모델 기반 프롬프트]
        업로드된 인물 사진이 {product_name}을 사용 중인 화보용 영어 프롬프트.
        """
        inputs = [instruction, p_img]
        if face_file: inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 AI가 기획안을 작성 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 3개 탭으로 결과 정돈
                tab1, tab2, tab3 = st.tabs(["🖼 제품 프롬프트", "📝 상세페이지 기획", "👤 모델 프롬프트"])
                
                with tab1:
                    st.code(content.split("[SECTION 2]")[0].replace("[SECTION 1: 제품 단독 프롬프트]", "").strip(), language='text')
                with tab2:
                    if "[SECTION 2]" in content:
                        st.markdown(content.split("[SECTION 2]")[1].split("[SECTION 3]")[0].strip())
                with tab3:
                    if "[SECTION 3]" in content:
                        st.code(content.split("[SECTION 3]")[1].strip(), language='text')
                st.success("✅ 모든 텍스트 기획이 완료되었습니다.")
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 업로드해 주세요.")
