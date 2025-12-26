import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 인증 및 엔진 안정화 (403/404 에러 방지)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 보안 차단 해결 필요: 새로운 키를 발급받아 Secrets에 업데이트하세요.")

# 개발자님 환경 최적화 모델 엔진
MODEL_NAME = 'gemini-2.0-flash' 

st.set_page_config(page_title="PnP Korean Marketing Master", layout="wide")

# 가로 스크롤 방지 및 가독성 최적화 CSS
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #2C3E50; border-bottom: 2px solid #ECF0F1; padding-bottom: 8px; margin-top: 25px; }
    .stCodeBlock { border-radius: 10px; border: 1px solid #DCDDE1; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 정렬
with st.sidebar:
    st.title("🇰🇷 한글 마케팅 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 이름", "고급 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🚀 마케팅 전략 및 한글 프롬프트 생성")
    st.caption(f"Engine: {MODEL_NAME}")

# 메인 화면
st.title("📸 픽앤샷: 한글 타이포그래피 마케팅 센터")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_NAME)
    
    # [한글 텍스트 특화 마케팅 인스트럭션]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자 한글 타이포그래피 마케팅 전문가입니다. 
    상품({product_name})을 분석하여 아래 4개 섹션으로 기획서를 작성하세요.

    ### [SECTION 1: 전문 촬영 기획서]
    - 컨셉: '{theme_choice}' 테마를 적용한 하이엔드 무드.
    - 기술 데이터: 촬영 각도, 조명 위치(Key/Rim Light), ISO 100, f/2.8, 셔터스피드 1/125.

    ### [SECTION 2: 하이엔드 제품 화보 프롬프트 3종 (한글 문구 포함)]
    Hasselblad 100MP, 8k 사양을 기본으로 다음 3가지 무드와 '한글 문구'를 포함하세요:
    1. **Minimalist Luxury**: 여백의 미 강조. 이미지 내에 '본연의 가치' 또는 '침묵의 미학'과 같은 한글 문구(Korean Typography) 포함.
    2. **Atmospheric Lifestyle**: 세련된 일상 공간. 이미지 내에 '당신의 순간을 완성하다' 같은 감성 한글 카피 포함.
    3. **Artistic Avant-Garde**: 강렬한 대비. 이미지 내에 '압도적 존재감' 또는 '시대의 정점' 같은 한글 카피 포함.
    *지시사항: 한글 텍스트가 이미지에 자연스럽게 렌더링되도록 "Korean Hangul Text Typography" 키워드를 프롬프트에 활용하세요.*

    ### [SECTION 3: 상세페이지 마케팅 카피]
    - 상세페이지 상단에 사용할 강렬한 한글 헤드라인과 본문 마케팅 문구.
    - 제품의 소유욕을 자극하는 심리학적 분석 내용 포함.

    ### [SECTION 4: 인물 일관성 유지 프롬프트]
    - 업로드된 모델의 외모 특징을 유지하며 제품과 한글 문구가 조화된 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 한글 마케팅 전략을 설계 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 수직 나열식 레이아웃 출력
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    st.markdown(f"### {section.strip()}")
            
            st.balloons()
        except Exception as e:
            st.error(f"실행 중 오류 발생: {str(e)}")
elif generate_btn:
    st.warning("상품 이미지를 먼저 업로드해 주세요.")
