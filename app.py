import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API 설정 (개발자님 성공 코드 방식 그대로 유지)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets에서 GEMINI_API_KEY를 확인해주세요.")

# 2. 엔진 설정 (가장 안정적인 최신 모델 사용)
# 아까 성공하셨던 모델명이 'gemini-2.5-flash' 혹은 'gemini-2.0-flash-exp'라면 그 명칭을 그대로 씁니다.
MODEL_NAME = 'gemini-1.5-flash' # 혹은 'gemini-2.0-flash-exp'

# --- UI 설정 ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 정렬을 위해 입력창을 왼쪽으로 배치
with st.sidebar:
    st.title("📸 픽앤픽 설정 센터")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 사진 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    
    theme_choice = st.selectbox("기획 테마 선택", [
        "시네마틱 누아르(Cinematic Noir)", 
        "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", 
        "크리스마스 박스(Christmas Box Wine)", 
        "사이버펑크 크롬(Cyberpunk Chrome)",
        "가을 파리 OOTD(Autumn Paris)"
    ])
    
    generate_btn = st.button("🔥 마스터피스 기획 시작", use_container_width=True)
    st.info(f"현재 작동 엔진: {MODEL_NAME}")

# 메인 화면
st.title("✨ 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if prod_file:
        p_img = Image.open(prod_file)
        model = genai.GenerativeModel(MODEL_NAME)
        
        # [초고퀄리티 프롬프트 유지] - 기획안 테마와 기술 사양 강제 주입
        instruction = f"""
        당신은 세계 최고의 상업 사진 작가이자 마케팅 전문가입니다. 
        업로드된 이미지를 분석하여 다음 3개 섹션으로 '글'을 작성하세요.
        
        [SECTION 1: 제품 단독 화보]
        {product_name}과 배경만 강조된 상업 화보용 영어 프롬프트. 
        반드시 Hasselblad 100MP, 85mm f/1.8, razor-sharp textures, 8k resolution 사양을 포함하세요.

        [SECTION 2: 상세페이지 마케팅 기획]
        이 상품을 위한 전문적인 한글 마케팅 문구와 기획 의도. 
        고객이 당장 사고 싶게 만드는 상세페이지용 텍스트를 작성하세요.

        [SECTION 3: 모델 기반 화보]
        업로드된 인물 사진의 특징을 유지하며 {product_name}을 자연스럽게 착용한 영어 프롬프트.
        """
        
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 AI가 마스터피스를 기획 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 결과 탭 분리 (정렬 문제 해결)
                tab1, tab2, tab3 = st.tabs(["🖼 제품 단독 화보", "📝 상세페이지 문구", "👤 모델 기반 화보"])
                
                with tab1:
                    st.subheader("제품 + 배경 중심 프롬프트")
                    st.code(content.split("[SECTION 2]")[0].replace("[SECTION 1: 제품 단독 화보]", "").strip(), language='text')
                
                with tab2:
                    st.subheader("상세페이지 마케팅 카피")
                    if "[SECTION 2]" in content:
                        st.markdown(content.split("[SECTION 2]")[1].split("[SECTION 3]")[0].strip())
                
                with tab3:
                    st.subheader("인물 일관성 기반 프롬프트")
                    if "[SECTION 3]" in content:
                        st.code(content.split("[SECTION 3]")[1].strip(), language='text')
                
                st.success("✅ 기획이 완료되었습니다. 각 탭을 확인하세요!")
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 업로드해주세요.")
