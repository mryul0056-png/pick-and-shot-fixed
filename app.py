import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 기본 설정 (인증 및 엔진)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키를 Secrets에 확인해주세요.")

MODEL_ENGINE = 'gemini-2.0-flash' # 가장 안정적인 최신 엔진

st.set_page_config(page_title="PnP Masterpiece Integrator", layout="wide")

# CSS: 가로 스크롤 방지 및 복사 버튼 최적화
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    .stCodeBlock div button { visibility: visible !important; opacity: 1 !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 설정 영역
with st.sidebar:
    st.title("⚙️ 마스터피스 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (안경 디자인 고정)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (일관성 유지)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "블랙&크림 콤비 뿔테")
    # 테마 선택지를 하이엔드 무드로 구체화
    theme_choice = st.selectbox("핵심 기획 무드", [
        "High-Fashion Cinematic Noir (치명적/고급)", 
        "Elegant Minimalist Luxury (정제된/우아)", 
        "Dramatic Avant-Garde (예술적/강렬)"
    ])
    generate_btn = st.button("🔥 완벽한 통합본 생성")
    st.caption(f"Engine: {MODEL_ENGINE}")

# 메인 화면
st.title("📸 픽앤샷: 하이엔드 화보 통합 센터")
st.write("이미지 2의 **압도적 분위기**에 이미지 1의 **제품과 텍스트**를 결합합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # [천재 마케터의 "분위기 우선, 제품 침투" 인스트럭션]
    instruction = f"""
    당신은 보그(Vogue) 커버를 촬영하는 세계 최고의 상업 사진 작가입니다. 
    목표는 업로드된 제품({product_name})을 활용하여 '이미지 2'와 같은 압도적인 하이엔드 화보를 만드는 것입니다.

    **핵심 요구사항 (반드시 준수):**
    1.  **분위기 (최우선):** '{theme_choice}' 테마에 맞춰 드라마틱한 조명(Chiaroscuro, Rim lighting)과 깊이 있는 그림자를 사용하여 영화 같은 분위기를 연출하십시오. (이미지 2 스타일 참조)
    2.  **제품 고정:** 모델은 반드시 업로드된 이미지 속의 **'검정색 전면 프레임과 크림색(흰색) 다리'가 조합된 안경**을 착용해야 합니다. 조명이 이 두 가지 색상의 대비를 강조해야 합니다.
    3.  **텍스트 통합:** 지정된 한글 문구를 이미지의 분위기를 해치지 않는 우아한 타이포그래피 디자인 요소로 자연스럽게 배치하십시오.

    위 요구사항을 바탕으로 다음 4개 섹션을 작성하세요.

    ### [SECTION 1: 하이엔드 촬영 기획안 (한글)]
    - 컨셉: 제품의 고급스러움을 극대화하는 조명 및 앵글 전략.
    - 기술 세팅: ISO, 조리개, 셔터스피드 등 구체적 수치.

    ### [SECTION 2: 마스터피스 영문 프롬프트 3종]
    *공통 사양: Hasselblad 100MP, 8k, Editorial quality. dramatic lighting highlights the specific black frame and cream temples glasses.*
    1. **The Icon (대표 컷)**: 압도적인 분위기 속 제품 강조. (한글 문구: "본연의 가치")
    2. **The Mood (감성 컷)**: 모델의 아우라와 제품의 조화. (한글 문구: "당신의 시선을 완성하다")
    3. **The Detail (디테일 컷)**: 텍스처와 빛의 예술적 표현. (한글 문구: "압도적 존재감")

    ### [SECTION 3: 상세페이지 마케팅 카피 (한글)]
    - 고객의 심리를 꿰뚫는 고급스러운 카피라이팅.

    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    - 모델의 특징을 유지하며, 지정된 안경을 착용하고 하이엔드 무드를 연출하는 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 이미지 1과 2의 장점만 통합 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 수직 레이아웃 출력 및 복사 버튼 활성화
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    st.markdown(f"### {section.strip()}")
            
            st.balloons()
        except Exception as e:
            st.error(f"실행 오류: {str(e)}")
elif generate_btn:
    st.warning("상품 이미지를 먼저 업로드해 주세요.")
