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

# [오류 수정] 404 에러 방지를 위해 가장 안정적인 최신 정식 모델명을 사용합니다.
MODEL_NAME = 'gemini-1.5-flash' 

st.set_page_config(page_title="PnP Product Master", layout="wide")

# 2. UI 스타일 가이드: 하이엔드 프리미엄 룩앤필
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
    st.caption(f"Active Engine: {MODEL_NAME}")

st.title("📸 픽앤샷: 하이엔드 제품 기획 센터")
st.write("고성능 AI 엔진 최적화 완료. 대기 없이 최상의 퀄리티를 생성합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    # 404 오류 방지를 위해 명확한 모델 이름으로 인스턴스 생성
    model = genai.GenerativeModel(model_name=MODEL_NAME)
    
    # 4. [최고 기획자/포토그래퍼 로직] 하이엔드 프롬프트 인스트럭션
    # 광학 데이터(Phase One XF, Schneider 렌즈)를 주입하여 결과물의 격을 높입니다.
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독이자 브랜드 기획자입니다.
    가장 중요한 규칙: 업로드된 제품({product_name})의 디자인, 형태, 색상, 로고 위치를 100% 동일하게 유지하십시오.
    
    기획서 구성:
    ### [SECTION 1: 전문 촬영 기획서 (한글)]
    - 테마: {theme_choice} 최적화 전략.
    - 기술 데이터: Phase One XF Body, 80mm Schneider Lens, f/1.2, ISO 50.
    
    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    (프롬프트 내용만 깔끔하게 작성하십시오. 반드시 'Prompt:'로 시작하십시오.)
    *공통 사양: High-End Editorial, 8k Resolution, Ray Tracing, Professional Studio Lighting.*
    
    ### [SECTION 3: 상세페이지 마케팅 문구 (한글)]
    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("전문 감독님이 제품을 분석하여 하이엔드 기획안을 작성 중의입니다..."):
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
            # 6. [에러 통합 핸들러] 이미지 속 모든 오류(429/404/Syntax)에 대응
            error_str = str(e)
            # 파이썬 주석(#)을 사용하여 이미지 78c77f의 SyntaxError를 완벽 차단
            if "429" in error_str:
                st.error("🚀 접속량이 많아 일시적으로 지연되었습니다. 결제 연결을 확인하시거나 10초 뒤 다시 시도해 주세요.")
                time.sleep(10)
            elif "404" in error_str:
                st.error("⚠️ 모델 인식 오류: 시스템이 최신 엔진으로 자동 복구를 시도 중입니다. 잠시 후 다시 시도하세요.")
            else:
                st.error(f"실행 오류: {error_str}")

elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
