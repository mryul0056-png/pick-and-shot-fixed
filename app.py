import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 인증 및 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Secrets에서 GEMINI_API_KEY를 확인해주세요.")

# 개발자님 환경에서 작동 확인된 모델명 사용
MODEL_NAME = 'gemini-2.5-flash' 

# 2. UI/UX 설정 (와이드 레이아웃 적용)
st.set_page_config(page_title="Pick & Shot Professional", layout="wide")

# 가로 스크롤 방지용 커스텀 CSS
st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; }
    code { white-space: pre-wrap !important; } /* 프롬프트 줄바꿈 허용 */
    </style>
    """, unsafe_allow_html=True)

# 사이드바: 모든 입력과 설정을 한곳으로 정렬 (결과창 공간 확보)
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정 센터")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 사진 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    
    theme_choice = st.selectbox("기획 테마 선택", [
        "시네마틱 누아르(Cinematic Noir)", 
        "미니어처 디오라마(Miniature Diorama)", 
        "신비로운 꽃의 여신(Ethereal Floral)", 
        "크리스마스 박스(Christmas Box Wine)", 
        "사이버펑크 크롬(Cyberpunk Chrome)",
        "가을 파리 OOTD(Autumn Paris)"
    ])
    
    generate_btn = st.button("🔥 마스터피스 기획 시작", use_container_width=True)
    st.markdown("---")
    st.header("📖 한글설명(Manual)")
    st.info("이 프로그램은 이미지를 생성하지 않습니다. 재미나이 AI가 사진을 정밀 분석하여 상업용 설계도와 마케팅 카피를 '글'로 작성합니다.")

# 메인 화면
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")
st.write("모델은 기획을 하고, 당신은 프롬프트를 가져가기만 하면 됩니다.")

if generate_btn:
    if prod_file:
        p_img = Image.open(prod_file)
        model = genai.GenerativeModel(MODEL_NAME)
        
        # [천재적 프롬프트 엔진] 4가지 섹션 강제 지정
        instruction = f"""
        당신은 상업 사진 감독이자 마케팅 전문가입니다. 업로드된 이미지를 분석하여 반드시 아래 4개 섹션으로 글을 작성하세요.

        ### [SECTION 1: 전문 기획안]
        - 상품({product_name})에 대한 컨셉 설정.
        - 사진 촬영 각도(앵글), 배경 설명.
        - 카메라 기술 설정(ISO, 셔터스피드, 조리개값, 조명 위치).

        ### [SECTION 2: 제품 단독 화보 프롬프트]
        - 제품과 기획된 배경만 나오는 상업용 영어 프롬프트.
        - Hasselblad 100MP, 85mm f/1.8, 8k 사양 필수 포함.

        ### [SECTION 3: 마케팅 상세 문구]
        - 제품과 배경의 조화를 활용한 상세페이지용 마케팅 카피 및 제품 설명(한글).

        ### [SECTION 4: 모델 일관성 유지 프롬프트]
        - 업로드된 모델 사진을 활용하여 어떤 각도에서도 일관성이 유지되는 제품 착용 영어 프롬프트.
        - 인물 특징을 보존하는 기술 지시어 포함.
        """
        
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이 AI 감독님이 전략을 짜는 중..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 결과물을 4개의 탭으로 깔끔하게 분리 (마우스 휠로 세로로 확인 가능)
                tab1, tab2, tab3, tab4 = st.tabs(["📋 기획안", "🖼 제품 프롬프트", "📝 상세 문구", "👤 모델 프롬프트"])
                
                with tab1:
                    st.subheader("상세 촬영 기획서")
                    # 섹션별 파싱 후 출력
                    plan_text = content.split("### [SECTION 2]")[0].replace("### [SECTION 1: 전문 기획안]", "").strip()
                    st.markdown(plan_text)
                
                with tab2:
                    st.subheader("제품 + 배경 중심 설계도 (Prompt)")
                    if "### [SECTION 2]" in content:
                        st.code(content.split("### [SECTION 2]")[1].split("### [SECTION 3]")[0].strip(), language='text')
                
                with tab3:
                    st.subheader("마케팅 카피 및 상세 문구")
                    if "### [SECTION 3]" in content:
                        st.markdown(content.split("### [SECTION 3]")[1].split("### [SECTION 4]")[0].strip())
                
                with tab4:
                    st.subheader("인물 일관성 유지 설계도 (Prompt)")
                    if "### [SECTION 4]" in content:
                        st.code(content.split("### [SECTION 4]")[1].strip(), language='text')
                
                st.success("✅ 모든 분석이 완료되었습니다. 탭을 클릭하여 확인하세요.")
                st.balloons()
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 업로드해주세요.")
