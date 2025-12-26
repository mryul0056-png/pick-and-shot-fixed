import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. API 인증 및 환경 설정
try:
    # image_fcc4fd.png의 403 에러 해결을 위해 새 키를 Secrets에 등록 필수
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ [보안 경고] API 키 유출로 차단됨. 새로운 키를 발급받아 Secrets에 업데이트하세요.")

# 개발자님 환경에서 404 없이 성공했던 최신 안정화 엔진
MODEL_ENGINE = 'gemini-1.5-flash' 

# 2. UI/UX 설정 (와이드 레이아웃 및 가로 스크롤 차단)
st.set_page_config(page_title="PnP High-End Marketing Master", layout="wide")
st.markdown("""
    <style>
    /* 텍스트 줄바꿈 강제 및 가로 스크롤 방지 */
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 영역
with st.sidebar:
    st.title("🛡️ 마케팅 전략 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 하이엔드 제품")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 천재 기획자의 마케팅 화보 설계")
    st.caption(f"Active Engine: {MODEL_ENGINE}")

# 메인 화면
st.title("📸 픽앤샷(Pick & Shot): K-하이엔드 기획 센터")
st.write("이미지 생성용 **영문 프롬프트**와 이미지 삽입용 **한글 문구**를 동시에 설계합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # [천재 마케터의 전략적 인스트럭션]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자 소비심리 마케팅 전문가입니다. 
    상품({product_name})을 분석하여 아래 4개 섹션으로 기획서를 작성하세요. 모든 프롬프트는 영어로 작성하되, 이미지 내 삽입 문구만 한글로 구성하세요.

    ### [SECTION 1: 전문 촬영 기획안 (한글)]
    - 컨셉: '{theme_choice}'를 극대화한 브랜드 스토리.
    - 기술 세팅: 촬영 각도, 조명 배치, ISO 100, f/2.8, 셔터스피드 1/125 등 전문가적 수치.

    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    *공통 사양: Hasselblad 100MP, 8k, professional lighting. 각 프롬프트는 이미지 내 중앙 혹은 적절한 위치에 특정 한글 문구를 삽입하도록 설계하세요.*
    1. **Minimalist Luxury Mood**: 제품 본연의 질감을 강조하는 영문 프롬프트. (이미지 내 삽입될 한글 문구: "본연의 가치")
    2. **Atmospheric Lifestyle Mood**: 세련된 일상을 묘사하는 영문 프롬프트. (이미지 내 삽입될 한글 문구: "당신의 순간을 완성하다")
    3. **Artistic Avant-Garde Mood**: 강렬한 대비를 활용한 예술적 영문 프롬프트. (이미지 내 삽입될 한글 문구: "압도적 존재감")

    ### [SECTION 3: 마케팅 상세 문구 (한글)]
    - 고객의 구매 욕구를 즉각적으로 자극하는 전문 카피라이팅과 기획 의도 설명.

    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    - 업로드된 모델의 특징을 유지하며 제품과 한글 문구가 조화롭게 어우러진 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 한글 카피가 포함된 영문 설계도를 작성 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 휠 스크롤에 최적화된 수직 나열 레이아웃
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    st.markdown(f"### {section.strip()}")
            
            st.balloons()
            st.success("✅ 모든 기획안이 생성되었습니다. 마우스 휠을 내려 확인하세요.")
        except Exception as e:
            st.error(f"실행 오류: {str(e)}")
elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
