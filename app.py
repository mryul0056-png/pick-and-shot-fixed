import streamlit as st
import google.generativeai as genai
from PIL import Image

# [긴급 조치] image_fcc4fd.png의 403 키 유출 해결을 위해 새 키를 Secrets에 넣으세요.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키가 유출되어 차단되었습니다. 새 키를 발급받아 Secrets에 입력하세요.")

# 개발자님 환경에서 작동이 검증된 모델명으로 고정
MODEL_ENGINE = 'gemini-2.5-flash'

st.set_page_config(page_title="PnP Product Master", layout="wide")

# 가로 스크롤 방지 및 수직 가독성 최적화 CSS
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 영역 (결과창 공간 확보)
with st.sidebar:
    st.title("🔒 제품 일관성 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수 - 이 디자인이 고정됨)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 제품 고정 기획 및 프롬프트 생성")
    st.caption(f"Active Engine: {MODEL_ENGINE}")

# 메인 화면
st.title("📸 픽앤샷: 제품 디자인 락킹(Locking) 센터")
st.write("고객님의 소중한 제품 디자인이 AI에 의해 변형되지 않도록 강력하게 고정합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # [핵심 솔루션: 제품 일관성 고정 프롬프트]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자, 제품의 원형을 완벽하게 보존하는 마케팅 전문가입니다.
    가장 중요한 규칙: **업로드된 이미지의 제품({product_name}) 디자인, 형태, 색상, 로고 위치 등 모든 디테일을 100% 동일하게 유지해야 합니다. 절대로 새로운 디자인을 창조하지 마십시오.**

    이 규칙을 바탕으로 아래 4개 섹션으로 기획서를 작성하세요. 프롬프트는 영어, 마케팅 문구는 한글입니다.

    ### [SECTION 1: 전문 촬영 기획서 (한글)]
    - 컨셉: 제품의 원형을 유지한 채 '{theme_choice}' 테마를 극대화하는 전략.
    - 기술 데이터: 촬영 각도(Eye-level 권장), 조명 배치, ISO 100, f/2.8, 셔터스피드 1/125 제안.

    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    *공통 사양: The exact product shown in the input image (design, shape, color) must be preserved perfectly. Hasselblad 100MP, 8k.*
    1. **Minimalist Luxury**: 제품 본연의 디자인을 강조하는 영문 프롬프트. (한글 카피 삽입: "본연의 가치")
    2. **Atmospheric Lifestyle**: 제품 디자인이 돋보이는 세련된 일상 영문 프롬프트. (한글 카피 삽입: "당신의 순간을 완성하다")
    3. **Artistic Avant-Garde**: 제품의 형태를 해치지 않는 선에서 강렬한 대비를 준 영문 프롬프트. (한글 카피 삽입: "압도적 존재감")

    ### [SECTION 3: 상세페이지 마케팅 문구 (한글)]
    - 고객의 구매 욕구를 자극하는 한글 상세 설명과 카피라이팅.

    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    - 업로드된 인물 사진의 특징을 유지하며, **원본 제품 디자인을 변형 없이 자연스럽게 착용**한 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 제품을 완벽하게 고정하는 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 수직 나열식 레이아웃으로 출력 (가로 스크롤 완전 해결)
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    st.markdown(f"### {section.strip()}")
            
            st.balloons()
            st.success("✅ 제품 디자인이 고정된 기획안이 생성되었습니다. 마우스 휠을 내려 확인하세요.")
        except Exception as e:
            st.error(f"실행 오류: {str(e)}")
            st.info("⚠️ 403 에러는 새 API 키 발급 외에는 해결 방법이 없습니다. Secrets를 확인하세요.")
elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
