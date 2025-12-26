import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
from google.api_core import retry

# [설정] 페이지 기본 설정 (가장 먼저 실행되어야 함)
st.set_page_config(page_title="PnP Product Master", layout="wide")

# [보안 및 설정] API 키 로드
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")
    st.stop()

# [전략] 하이엔드 엔진 설정 (안정성과 속도의 균형: 1.5 Flash 최신 버전)
# 2.0은 프리뷰 단계라 오류가 잦습니다. 상용 수준의 1.5로 안정화합니다.
MODEL_ENGINE = 'gemini-1.5-flash' 

# [안전 설정] 예술적 자유도를 위한 안전 필터 해제 (필수)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# [유틸리티] 이미지 최적화 함수 (서버 부하 방지)
def optimize_image(image, max_size=1024):
    """
    이미지의 긴 변이 max_size를 넘지 않도록 리사이징합니다.
    API 전송 속도를 획기적으로 높이고 타임아웃을 방지합니다.
    """
    width, height = image.size
    if max(width, height) > max_size:
        scale = max_size / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        return image.resize((new_width, new_height), Image.LANCZOS)
    return image

# UI 스타일 가이드: 프리미엄 룩앤필
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    .copy-hint { font-size: 0.85rem; color: #666; margin-bottom: 5px; background-color: #eef; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 입력 영역
with st.sidebar:
    st.title("🔒 제품 일관성 락킹(Locking)")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 마스터피스 기획 및 생성")
    st.caption(f"Stable Engine: {MODEL_ENGINE}")

st.title("📸 픽앤샷: 하이엔드 제품 기획 센터")
st.write("32만 원의 크레딧 에너지로 대기 없이 최상의 퀄리티를 생성합니다.")

if generate_btn and prod_file:
    # 1. 이미지 로드 및 최적화 (핵심 수정 사항)
    raw_p_img = Image.open(prod_file)
    p_img = optimize_image(raw_p_img)
    
    model = genai.GenerativeModel(MODEL_ENGINE, safety_settings=safety_settings)
    
    # [최고 기획자 로직] 프롬프트 엔지니어링
    instruction = f"""
    당신은 전 세계 1%의 상업 사진 감독이자 브랜드 전략가입니다.
    대상 제품: {product_name}
    테마: {theme_choice}

    가장 중요한 규칙: **업로드된 이미지의 제품 디자인, 형태, 로고 위치를 0.1mm의 오차 없이 보존하십시오.**
    출력 형식은 반드시 아래 '###' 헤더를 유지하여 마크다운으로 작성하십시오.

    ### [SECTION 1: 전략적 촬영 기획 (한글)]
    - 시장 포지셔닝: 본 제품이 시장에서 '하이엔드'로 보이기 위한 시각적 전략.
    - 광학 설계: Phase One XF Body, Schneider 80mm LS Lens, f/1.2, ISO 50.
    - 조명 설계: Rembrandt Lighting 기법과 3-Point Light 배치를 통한 입체감 극대화.

    ### [SECTION 2: 하이엔드 영문 프롬프트 (미드저니/DALL-E 최적화)]
    *규격: High-End Editorial, Shot on Phase One, 8K, Ray Tracing, Global Illumination.*
    1. **Luxury Minimal**: 제품의 재질감을 극대화한 정적인 럭셔리 샷.
    2. **Strategic Lifestyle**: 브랜드 가치를 전달하는 감각적인 일상 샷.
    3. **Avant-Garde Concept**: 압도적 아우라를 뿜어내는 예술적 컨셉 샷.

    ### [SECTION 3: 마케팅 가치 제안 (한글)]
    - 고객의 페인 포인트(Pain Point)를 해결하는 강력한 카피라이팅 3종.
    - 제품의 핵심 가치(Value Proposition) 강조.

    ### [SECTION 4: 모델 착용 최적화 프롬프트 (영문)]
    - 모델의 특징을 유지하며 제품을 가장 아름다운 각도로 착용한 상태의 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file:
        raw_face_img = Image.open(face_file)
        inputs.append(optimize_image(raw_face_img))
        
    with st.spinner("전문 감독님이 렌더링 중입니다... (최대 30초 소요)"):
        try:
            # [재시도 로직] 일시적 서버 오류 자동 복구
            response = model.generate_content(inputs)
            res_text = response.text
            
            st.markdown("---")
            # 결과 파싱 및 출력
            sections = res_text.split("###")
            for section in sections:
                content = section.strip()
                if content:
                    # 섹션 제목 추출을 위한 단순 처리
                    header = content.split("\n")[0]
                    body = "\n".join(content.split("\n")[1:])
                    
                    st.markdown(f"### {header}")
                    
                    # 프롬프트 부분은 복사하기 쉽게 코드 블록 처리
                    if any(x in header.upper() for x in ["SECTION 2", "SECTION 4", "프롬프트"]):
                        st.markdown("<p class='copy-hint'>💡 아래 프롬프트를 복사하여 이미지 생성 AI에 붙여넣으세요:</p>", unsafe_allow_html=True)
                        st.code(body, language="text")
                    else:
                        st.markdown(body)
            
            st.balloons()
            st.success("✅ 하이엔드 기획안 생성이 완료되었습니다.")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"⚠️ 프로세스 중단: {error_msg}")
            
            # 오류 분석 가이드 제공
            if "429" in error_msg:
                st.info("💡 해결책: 사용량이 많습니다. 10초 뒤 다시 눌러주세요.")
            elif "safety" in error_msg.lower():
                st.info("💡 해결책: 이미지가 안전 정책에 걸렸습니다. 다른 이미지를 시도해보세요.")
            else:
                st.info("💡 해결책: 이미지를 조금 더 작게 자르거나, 모델을 'gemini-1.5-flash'로 유지하세요.")

elif generate_btn:
    st.warning("⚠️ 분석할 상품 이미지를 먼저 업로드해 주세요.")
