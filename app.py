import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 인증 및 엔진 설정 (성공했던 모델명 gemini-2.5-flash로 고정)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets 설정을 확인해주세요.")

# [중요] 개발자님 환경에서 404 에러 없이 실행 성공했던 모델명입니다.
MODEL_NAME = 'gemini-2.5-flash' 

st.set_page_config(page_title="PnP High-End Marketing Master", layout="wide")

# 가로 스크롤 방지 및 수직 가독성 최적화 CSS
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 모든 입력과 설정을 왼쪽으로 몰아 정렬 해결
with st.sidebar:
    st.title("⚙️ 마케팅 기획 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🚀 마스터피스 기획 및 프롬프트 생성")
    st.caption(f"검증된 엔진 사용 중: {MODEL_NAME}")

# 메인 화면: 휠만 내려서 보는 수직 레이아웃
st.title("📸 픽앤샷(Pick & Shot): 전문 기획 센터")
st.write("모델은 기획을 하고, 당신은 영문 프롬프트와 한글 카피를 가져가기만 하면 됩니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_NAME)
    
    # [천재 기획자의 4단 전략 인스트럭션]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자 소비심리 마케팅 전문가입니다. 
    상품({product_name})을 분석하여 아래 4개 섹션으로 기획서를 작성하세요. 모든 프롬프트는 영어로 작성하되, 이미지 내 삽입 문구만 한글로 구성하세요.

    ### [SECTION 1: 전문 촬영 기획안 (한글)]
    - 컨셉: '{theme_choice}'를 극대화한 촬영 전략.
    - 기술 세팅: 최적의 촬영 각도, 조명 배치, ISO 100, f/2.8, 셔터스피드 1/125 등 전문가적 촬영 수치 제안.

    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    *공통 사양: Hasselblad 100MP, 8k. 각 프롬프트는 이미지 내에 특정 한글 문구를 삽입하도록 설계하세요.*
    1. **Minimalist Luxury**: 제품 본연의 질감을 강조하는 영문 프롬프트. (삽입될 한글 문구: "본연의 가치")
    2. **Atmospheric Lifestyle**: 세련된 일상을 묘사하는 영문 프롬프트. (삽입될 한글 문구: "당신의 순간을 완성하다")
    3. **Artistic Avant-Garde**: 강렬한 대비를 활용한 영문 프롬프트. (삽입될 한글 문구: "압도적 존재감")

    ### [SECTION 3: 상세페이지 마케팅 문구 (한글)]
    - 고객의 구매 욕구를 자극하는 한글 상세 설명과 카피라이팅.

    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    - 업로드된 인물 사진의 특징을 완벽히 유지하며 제품과 한글 문구가 조화로운 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 휠 스크롤 리포트를 작성 중입니다..."):
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
            st.success("✅ 기획안이 생성되었습니다. 마우스 휠을 내려 전체 내용을 확인하세요.")
        except Exception as e:
            st.error(f"실행 오류: {str(e)}")
            st.info("모델명을 'gemini-flash-latest'로 바꾸면 해결될 수도 있습니다.")
elif generate_btn:
    st.warning("분석할 이미지를 먼저 업로드해 주세요.")
