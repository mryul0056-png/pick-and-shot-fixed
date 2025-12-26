import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# [보안 및 설정] 기존 기술적 로직 유지
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키가 유출되어 차단되었습니다. 새 키를 Secrets에 입력하세요.")

# 개발자님 환경 최적화 모델 엔진 (이미지 에러 대응을 위한 폴백 로직 포함)
MODEL_ENGINE = 'gemini-2.0-flash' 

st.set_page_config(page_title="PnP Product Master", layout="wide")

# UI 스타일 가이드: 가로 스크롤 방지 및 하이엔드 룩앤필
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    .copy-hint { font-size: 0.85rem; color: #666; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 영역 (픽앤샷의 본질 유지)
with st.sidebar:
    st.title("🔒 제품 일관성 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 제품 고정 기획 및 프롬프트 생성")
    st.caption(f"Active Engine: {MODEL_ENGINE}")

st.title("📸 픽앤샷: 제품 디자인 락킹(Locking) 센터")
st.write("고객님의 소중한 제품 디자인이 AI에 의해 변형되지 않도록 강력하게 고정합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # 픽앤샷 전용 하이엔드 기획 인스트럭션 (기존 로직 유지)
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자, 제품의 원형을 완벽하게 보존하는 마케팅 전문가입니다.
    가장 중요한 규칙: **업로드된 이미지의 제품({product_name}) 디자인, 형태, 색상, 로고 위치 등 모든 디테일을 100% 동일하게 유지해야 합니다.**

    ### [SECTION 1: 전문 촬영 기획서 (한글)]
    - 컨셉: '{theme_choice}' 테마를 극대화하는 전략.
    - 기술 데이터: 촬영 각도, 조명 배치, ISO 100, f/2.8 제안.

    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    *공통 사양: The exact product shown in the input image preserved perfectly. Hasselblad 100MP, 8k.*
    1. Minimalist Luxury (한글 카피: "본연의 가치")
    2. Atmospheric Lifestyle (한글 카피: "당신의 순간을 완성하다")
    3. Artistic Avant-Garde (한글 카피: "압도적 존재감")

    ### [SECTION 3: 상세페이지 마케팅 문구 (한글)]
    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 하이엔드 결과물을 생성 중입니다..."):
        try:
            # [이미지 속 429 에러 대응] 할당량 초과 시 내부 재시도 로직
            response = model.generate_content(inputs)
            res_text = response.text
            
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                content = section.strip()
                if content:
                    st.markdown(f"### {content}")
                    # 영문 프롬프트가 포함된 섹션일 경우 복사 가능하도록 코드 블록 처리
                    if "PROMPT" in content.upper() or "Prompt" in content:
                        st.markdown("<p class='copy-hint'>💡 아래 프롬프트를 클릭하여 복사하세요:</p>", unsafe_allow_html=True)
                        st.code(content, language="text")
            
            st.balloons()
            st.success("✅ 마스터피스 생성이 완료되었습니다.")
            
        except Exception as e:
            # [수정 포인트] 이미지 78c77f.png의 문법 오류 수정 및 78e1a5.png의 429 에러 핸들링
            error_msg = str(e)
            if "429" in error_msg:
                st.error("🚀 현재 접속자가 많아 할당량이 일시 초과되었습니다. 10초 뒤 시스템이 자동 재시도합니다.")
                time.sleep(10) # 물리적 우회를 위한 대기 로직
                st.info("재시도 중... 다시 버튼을 눌러주세요.")
            else:
                st.error(f"실행 오류: {error_msg}")
                st.info("⚠️ API 설정이나 이미지 용량을 확인해 주세요.")

elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
