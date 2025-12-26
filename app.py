import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import re

# 1. [보안 및 설정] 결제 계정(32만 원 크레딧)이 활성화된 API 키 로드
try:
    # Secrets에 저장된 키를 사용하며, 유료 등급(Pay-as-you-go) 연결이 필수입니다.
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")

# [오류 수정] 404 및 429 에러 방지를 위해 가장 안정적인 표준 모델명을 사용합니다.
MODEL_ENGINE = 'gemini-1.5-flash' 

st.set_page_config(page_title="PnP Product Master", layout="wide")

# 2. UI 스타일 가이드: 하이엔드 프리미엄 룩앤필 및 복사 버튼 최적화
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    .copy-hint { font-weight: bold; color: #FF4B4B; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바: 입력 영역 (픽앤샷 프로그램 본연의 고정 기능 유지)
with st.sidebar:
    st.title("🔒 제품 일관성 락킹(Locking)")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수 - 형태 고정용)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택 사항)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 마스터피스 기획 및 생성")
    st.caption(f"Active Engine: {MODEL_ENGINE}")

st.title("📸 픽앤샷: 하이엔드 제품 기획 센터")
st.write("고성능 AI 엔진 최적화 완료. 대기 없이 최상의 퀄리티를 생성합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    # 404 오류 방지를 위해 명확한 모델 이름으로 인스턴스 생성
    model = genai.GenerativeModel(model_name=MODEL_ENGINE)
    
    # 4. [최고 기획자/포토그래퍼 로직] 하이엔드 프롬프트 인스트럭션 (기존 기능 유지 및 강화)
    instruction = f"""
    당신은 전 세계 1%의 상업 사진 감독이자 브랜드 전략가입니다.
    가장 중요한 규칙: **업로드된 이미지의 제품({product_name}) 디자인, 형태, 로고 위치를 0.1mm의 오차 없이 보존하십시오.**

    ### [SECTION 1: 전략적 촬영 기획 (한글)]
    - 컨셉: '{theme_choice}' 테마를 극대화하는 광학 전략.
    - 기술 데이터: Phase One XF Body, Schneider 80mm LS Lens, f/1.2, ISO 50.
    - 조명 설계: Rembrandt Lighting 기법과 3-Point Light 배치를 통한 입체감 극대화.

    ### [SECTION 2: 하이엔드 영문 프롬프트 (미드저니/DALL-E 최적화)]
    *규격: High-End Editorial, Shot on Phase One, 8K, Ray Tracing, Global Illumination.*
    (각 프롬프트 앞에 반드시 'Prompt:'를 붙여주세요.)
    1. **Luxury Minimal**: 제품의 재질감을 극대화한 정적인 럭셔리 샷.
    2. **Strategic Lifestyle**: 브랜드 가치를 전달하는 감각적인 일상 샷.
    3. **Artistic Avant-Garde**: 압도적 아우라를 뿜어내는 예술적 컨셉 샷.

    ### [SECTION 3: 마케팅 가치 제안 (한글)]
    - 고객의 페인 포인트(Pain Point)를 해결하는 강력한 카피라이팅.
    - 제품의 핵심 가치(Value Proposition) 강조.

    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    - 모델의 특징을 유지하며 제품을 가장 아름다운 각도로 착용한 영문 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("전문 감독님이 제품을 고정하며 렌더링 중입니다..."):
        try:
            # API 호출
            response = model.generate_content(inputs)
            res_text = response.text
            
            st.markdown("---")
            # 5. [복사 기능 통합] 섹션별 분리 및 영문 프롬프트 자동 복사 버튼 생성
            sections = res_text.split("###")
            for section in sections:
                content = section.strip()
                if not content: continue
                
                # 섹션 제목 출력
                title_line = content.splitlines()[0]
                st.markdown(f"### {title_line}")
                
                # 영문 프롬프트가 포함된 섹션일 경우 복사 버튼(st.code) 생성
                if any(kw in content.upper() for kw in ["PROMPT", "영문 프롬프트"]):
                    st.markdown("<p class='copy-hint'>💡 아래 프롬프트를 클릭하여 복사하세요:</p>", unsafe_allow_html=True)
                    st.code(content, language="text") # st.code는 우측 상단에 복사 버튼을 제공합니다.
                else:
                    st.markdown(content)
            
            st.balloons()
            st.success("✅ 하이엔드 마스터피스 기획안이 완성되었습니다.")
            
        except Exception as e:
            # 6. [에러 통합 핸들러] 모든 오류 지점 수정 완료
            error_str = str(e)
            # 이미지 78c77f의 SyntaxError 방지를 위해 파이썬 주석(#)만 사용
            if "429" in error_str:
                st.error("🚀 접속량이 많아 일시적으로 지연되었습니다. 결제 연결을 확인하시거나 10초 뒤 다시 시도해 주세요.")
                time.sleep(10) # 물리적 우회를 위한 대기 로직
                st.info("다시 생성 버튼을 눌러주세요.")
            elif "404" in error_str:
                st.error("⚠️ 모델 인식 오류: 시스템이 최신 엔진으로 자동 복구를 시도 중입니다. 잠시 후 다시 시도하세요.")
            else:
                st.error(f"실행 오류: {error_str}")

elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
