import streamlit as st
import google.generativeai as genai
from PIL import Image

# [필독] image_fcc4fd.png 에러 해결: 새로운 API 키를 Secrets에 넣어야 작동합니다.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 차단됨 (Leaked). 새로운 키를 발급받아 Secrets에 업데이트하세요.")

# 작동이 확인된 최신 모델 엔진 명칭
MODEL_ENGINE = 'gemini-2.5-flash' 

st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 가로 스크롤 방지 및 가독성 향상 CSS
st.markdown("""
    <style>
    .stMarkdown { white-space: pre-wrap !important; word-break: break-all !important; }
    .stCodeBlock { white-space: pre-wrap !important; }
    h1, h2, h3 { color: #1E1E1E; border-bottom: 2px solid #F0F2F6; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 정렬
with st.sidebar:
    st.title("⚙️ 픽앤샷 설정")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (일관성 유지용)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 이름", "고급 블랙 뿔테 안경")
    theme_choice = st.selectbox("예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome"])
    generate_btn = st.button("🚀 전문 기획서 생성")

# 메인 영역
st.title("📸 픽앤샷(Pick & Shot): 전문 기획 센터")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # [BCG 전략 프롬프트] 4가지 상세 섹션 구성
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독입니다. 사진을 정밀 분석하여 아래 4개 섹션으로 기획서를 작성하세요.

    ### 1. 전문 촬영 기획안
    - 상품({product_name})의 컨셉 및 배경 설정.
    - 최적의 촬영 각도(Low-angle, Eye-level 등)와 구도 제안.
    - 기술 데이터: ISO 100, f/2.8, 셔터스피드 1/125, 조명은 45도 측면 배치 등 상세히.

    ### 2. 제품 화보 프롬프트 (High-End)
    - 제품과 배경의 질감을 극대화한 영어 프롬프트. (Hasselblad 100MP, 8k 사양 포함)

    ### 3. 상세페이지 마케팅 문구
    - 제품의 특징을 살린 세련된 한글 마케팅 카피와 상세 설명.

    ### 4. 인물 일관성 유지 프롬프트
    - 업로드된 인물의 특징을 완벽히 유지하며 제품을 착용한 모습의 영어 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 마스터피스를 설계 중입니다..."):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            # 세로로 시원하게 나열하여 휠 스크롤로 확인
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                if section.strip():
                    st.markdown(f"### {section.strip()}")
            
            st.balloons()
        except Exception as e:
            st.error(f"실행 오류: {str(e)}")
elif generate_btn:
    st.warning("상품 이미지를 업로드해 주세요.")
