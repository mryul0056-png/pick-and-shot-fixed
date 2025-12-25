import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 성공했던 인증 방식 그대로 유지 (Secrets 필수)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets에서 GEMINI_API_KEY를 확인해주세요.")

# 2. UI 설정 (상단 정렬을 방해하지 않도록 사이드바 활용)
st.set_page_config(page_title="Pick & Shot Pro", layout="wide")

with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
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
    generate_btn = st.button("🚀 마스터피스 기획 시작", use_container_width=True)

# 메인 화면
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if prod_file:
        p_img = Image.open(prod_file)
        
        # [검증됨] 개발자님 환경에서 404가 안 났던 바로 그 모델명
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # [초고퀄리티 프롬프트 엔진] - 지능은 그대로 유지
        instruction = f"""
        당신은 상업 사진 작가입니다. 업로드된 이미지를 분석하여 3개 섹션으로 글을 작성하세요.
        
        [SECTION 1: 제품 단독 화보]
        {product_name}과 배경만 강조된 영어 프롬프트. (Hasselblad 100MP, 85mm f/1.8, 8k 사양 필수 포함)

        [SECTION 2: 상세페이지 기획]
        이 상품을 위한 전문적인 한글 마케팅 문구와 상세 기획 의도.

        [SECTION 3: 모델 기반 화보]
        업로드된 인물 사진의 특징을 유지하며 {product_name}을 자연스럽게 활용하는 영어 프롬프트.
        """
        
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("AI 감독님이 초고퀄리티 전략을 짜는 중..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 탭을 사용하여 결과 정돈 (상단 정렬 방해 금지)
                tab1, tab2, tab3 = st.tabs(["🖼 제품 화보", "📝 상세페이지 기획", "👤 모델 화보"])
                
                with tab1:
                    st.code(content.split("[SECTION 2]")[0].replace("[SECTION 1: 제품 단독 화보]", "").strip(), language='text')
                with tab2:
                    if "[SECTION 2]" in content:
                        st.markdown(content.split("[SECTION 2]")[1].split("[SECTION 3]")[0].strip())
                with tab3:
                    if "[SECTION 3]" in content:
                        st.code(content.split("[SECTION 3]")[1].strip(), language='text')
                
                st.balloons()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 올려주세요.")
