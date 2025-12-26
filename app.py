import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import re

# [보안 및 설정] 결제 연결 완료된 API 키 적용
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키 설정을 확인해주세요. Secrets에 새 키를 입력해야 합니다.")

# 픽앤샷 전용 하이엔드 엔진 설정
MODEL_ENGINE = 'gemini-1.5-flash' 

st.set_page_config(page_title="PnP Product Master", layout="wide")

# UI 스타일: 프리미엄 룩앤필 및 복사 가이드 강조
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .report-section { background-color: #F8F9FA; padding: 25px; border-radius: 15px; margin-bottom: 20px; border-left: 6px solid #FF4B4B; }
    .copy-button-hint { font-weight: bold; color: #FF4B4B; margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바 입력창
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
st.write("고객님의 제품 디자인을 완벽하게 고정하고, 하이엔드 화보 프롬프트를 생성합니다.")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    # [픽앤샷 마스터 기획 인스트럭션]
    instruction = f"""
    당신은 세계 최고의 상업 사진 감독입니다. 제품({product_name})의 디자인을 100% 유지하며 아래 섹션을 작성하세요.
    프롬프트는 영어로, 설명은 한글로 작성하십시오.
    
    ### [SECTION 1: 전문 촬영 기획서 (한글)]
    ### [SECTION 2: 하이엔드 제품 화보 영문 프롬프트 3종]
    (각 프롬프트 앞에 'Prompt:' 라고 명시하십시오.)
    ### [SECTION 3: 상세페이지 마케팅 문구 (한글)]
    ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
    """
    
    inputs = [instruction, p_img]
    if face_file: inputs.append(Image.open(face_file))
        
    with st.spinner("AI 감독님이 마스터피스를 기획 중입니다..."):
        try:
            # 429 에러 발생 시 재시도 로직 포함
            response = model.generate_content(inputs)
            res_text = response.text
            
            st.markdown("---")
            # 섹션별 파싱 및 복사 기능 주입
            sections = res_text.split("###")
            for section in sections:
                content = section.strip()
                if not content: continue
                
                # 제목과 내용 분리 출력
                st.markdown(f"### {content.splitlines()[0]}")
                body = "\n".join(content.splitlines()[1:])
                
                # 영문 프롬프트 탐지 및 복사 버튼(st.code) 생성
                if "PROMPT" in content.upper():
                    # 정규표현식으로 Prompt 내용만 추출하여 복사 가능하게 표시
                    prompts = re.findall(r"Prompt:(.*?)(?=\n\d\.|\n###|$)", body, re.DOTALL)
                    if prompts:
                        for idx, p in enumerate(prompts):
                            st.write(f"**프롬프트 {idx+1}**")
                            st.code(p.strip(), language="text") # st.code는 우측 상단에 복사 버튼이 생깁니다.
                    else:
                        st.code(body, language="text")
                else:
                    st.markdown(body)
            
            st.balloons()
            st.success("✅ 제품 디자인이 고정된 기획안이 생성되었습니다.")
            
        except Exception as e:
            # # 이미지 속 '할당량 초과' (429) 감지 시 파이썬 주석으로 처리 완료
            error_msg = str(e)
            if "429" in error_msg:
                st.error("🚀 접속자가 많아 잠시 할당량이 초과되었습니다. 10초 후 다시 시도해주세요.")
                time.sleep(10)
            else:
                st.error(f"실행 오류: {error_msg}")

elif generate_btn:
    st.warning("분석할 상품 이미지를 업로드해 주세요.")
