import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 인증 및 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ [필독] image_fcc4fd.png 에러 확인: API 키가 유출되어 차단되었습니다. 새로운 키를 발급받아 Secrets에 넣으세요.")

# 개발자님 환경에서 404 없이 성공했던 모델명
MODEL_NAME = 'gemini-2.5-flash' 

# 2. UI/UX 설정 (와이드 레이아웃 및 가로 스크롤 방지 CSS)
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")
st.markdown("""
    <style>
    /* 텍스트가 옆으로 나가지 않고 아래로 자동 줄바꿈되도록 설정 */
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 영역 (결과창 공간을 최대로 확보)
with st.sidebar:
    st.title("⚙️ 픽앤샷 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 사진 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "프리미엄 제품")
    theme_choice = st.selectbox("기획 테마", [
        "시네마틱 누아르(Cinematic Noir)", "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", "크리스마스 박스(Christmas Box Wine)", 
        "사이버펑크 크롬(Cyberpunk Chrome)", "가을 파리 OOTD(Autumn Paris)"
    ])
    generate_btn = st.button("🔥 촬영 지시서 및 프롬프트 생성")
    st.info(f"사용 엔진: {MODEL_NAME}")

# 메인 화면: 휠만 내려서 보는 4단 구성
st.title("📸 픽앤샷(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if prod_file:
        p_img = Image.open(prod_file)
        model = genai.GenerativeModel(MODEL_NAME)
        
        # 4가지 카테고리를 명확히 뽑아내기 위한 천재적 인스트럭션
        instruction = f"""
        당신은 상업 사진 감독입니다. 사진을 분석하여 아래 4개 섹션으로 '한글 기획안'과 '영어 프롬프트'를 작성하세요.

        ### [SECTION 1: 상세 촬영 기획안]
        - 상품({product_name}) 컨셉 및 배경 무드 설명.
        - 촬영 각도(앵글)와 구도 추천.
        - 카메라 기술 설정값: ISO, 조리개(f-stop), 셔터스피드, 조명 배치 위치.

        ### [SECTION 2: 제품 화보 프롬프트]
        - 상품과 배경만 강조된 고퀄리티 영어 프롬프트.
        - Hasselblad 100MP, 85mm f/1.8, 8k 사양 필수 포함.

        ### [SECTION 3: 상세페이지 마케팅 문구]
        - 고객의 구매 욕구를 자극하는 전문적인 한글 카피라이팅과 제품 상세 설명.

        ### [SECTION 4: 모델 일관성 유지 프롬프트]
        - 첨부된 인물 사진의 이목구비와 특징을 유지하며 제품을 사용하는 영어 프롬프트.
        - 어떤 각도에서도 동일 인물로 보이도록 인물 고정 키워드 포함.
        """
        
        inputs = [instruction, p_img]
        if face_file: inputs.append(Image.open(face_file))
            
        with st.spinner("AI 감독님이 촬영 현장을 설계 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 가로 스크롤 없이 세로로 쭉 나열하는 4단 구성
                st.markdown("---")
                
                # 섹션 1: 기획안
                st.header("1️⃣ 전문 촬영 기획안")
                st.info(content.split("### [SECTION 2]")[0].replace("### [SECTION 1: 상세 촬영 기획안]", "").strip())
                
                # 섹션 2: 제품 프롬프트
                st.header("2️⃣ 제품 화보 프롬프트 (High-Quality)")
                st.code(content.split("### [SECTION 2]")[1].split("### [SECTION 3]")[0].strip(), language='text')
                
                # 섹션 3: 마케팅 문구
                st.header("3️⃣ 상세페이지 마케팅 문구")
                st.success(content.split("### [SECTION 3]")[1].split("### [SECTION 4]")[0].strip())
                
                # 섹션 4: 모델 일관성 프롬프트
                st.header("4️⃣ 인물 일관성 유지 프롬프트")
                if "### [SECTION 4]" in content:
                    st.code(content.split("### [SECTION 4]")[1].strip(), language='text')
                
                st.balloons()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 업로드해주세요.")
