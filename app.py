import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 인증 및 엔진 최적화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 유출 차단 해결 필요: 새로운 키를 발급받아 Secrets에 입력하세요.")

# 개발자님 환경에서 가장 안정적인 최신 엔진
MODEL_NAME = 'gemini-2.0-flash' 

st.set_page_config(page_title="PnP High-End Marketing Master", layout="wide")

# 가로 스크롤 방지 및 가독성 향상 CSS
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E1E1E; border-bottom: 2px solid #F0F2F6; padding-bottom: 10px; margin-top: 30px; }
    .report-box { background-color: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 정렬
with st.sidebar:
    st.title("🛡️ 마케팅 설정 센터")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "프리미엄 하이엔드 제품")
    theme_choice = st.selectbox("기획 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 천재 기획자의 화보 전략 생성")

# 메인 화면
st.title("📸 픽앤샷: 하이엔드 마케팅 기획 센터")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_NAME)
    
    # [천재 디자이너의 전략적 인스트럭션]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자 마케팅 전문가입니다. 상품({product_name})을 분석하여 아래 4개 섹션으로 기획서를 작성하세요.

    ### [SECTION 1: 전문 촬영 기획서]
    - 컨셉: '{theme_choice}'를 활용한 독보적 브랜드 아이덴티티 설정.
    - 기술 데이터: 촬영 각도(Low-angle 등), 조명 배치(Rembrandt lighting 등), ISO, 조리개, 셔터스피드 상세 수치.

    ### [SECTION 2: 하이엔드 제품 화보 프롬프트 3종]
    각 프롬프트는 8k, Hasselblad 100MP 사양을 기본으로 하되 다음 3가지 다른 표현을 제공하세요:
    1. **Minimalist Luxury (정적/고결)**: 여백의 미와 제품의 질감을 강조.
    2. **Atmospheric Lifestyle (감성/동적)**: 상류층의 일상을 연상시키는 세련된 배경.
    3. **Artistic Avant-Garde (실험적/강렬)**: 조명과 그림자의 대비를 활용한 예술적 연출.
    *중요: 각 프롬프트 끝에 "이미지 내 중앙 하단에 배치할 소비심리 자극 텍스트 문구(Short Copy for Consumer Psychology)"를 영어로 포함하세요.*

    ### [SECTION 3: 마케팅 상세 문구 및 카피]
    - 상세페이지용 한글 마케팅 카피. (예: "시간을 넘어서는 가치, 당신의 시선을 완성하다")
    - 고객의 페인 포인트를 건드리고 욕망을 자극하는 상세 기획 의도.

    ### [SECTION 4: 인물 일관성 유지 프롬프트]
    - 첨부된 인물 사진의 이목구비와 분위기를 100% 유지하며 제품을 사용하는 고퀄리티 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 마스터피스를 기획 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 수직 레이아웃 출력
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    if "SECTION 2" in section:
                        st.markdown(f"### {section.strip()}")
                        st.info("💡 3가지 프롬프트를 번갈아 테스트하여 최적의 결과물을 찾으세요.")
                    elif "SECTION 3" in section:
                        st.markdown(f"### {section.strip()}")
                        st.success("✅ 상세페이지 문구로 즉시 활용 가능합니다.")
                    else:
                        st.markdown(f"### {section.strip()}")
            
            st.balloons()
        except Exception as e:
            st.error(f"실행 중 오류 발생: {str(e)}")
elif generate_btn:
    st.warning("분석할 상품 이미지를 먼저 업로드해 주세요.")
