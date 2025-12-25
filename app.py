import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 보안 설정 및 초기화 ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Streamlit Cloud의 Settings > Secrets에 'GEMINI_API_KEY'를 입력해주세요!")
    st.stop()

# --- 2. 페이지 설정 ---
st.set_page_config(page_title="Pick & Shot Pro - 픽앤샷 전문판", page_icon="📸", layout="wide")
st.title("📸 픽앤샷 프로 (Pick & Shot Pro)")
st.markdown("##### 상품 분석 + 인물 일관성 유지 + 외부 도구 실행 가이드 통합판")
st.markdown("---")

# --- 3. 사이드바 이미지 업로드 영역 ---
with st.sidebar:
    st.header("📂 이미지 업로드")
    
    st.subheader("1. 판매 상품 이미지 (필수)")
    product_file = st.file_uploader("안경, 옷, 가방 등의 상품 사진", type=["jpg", "png", "jpeg"], key="product")
    
    st.subheader("2. 본인/모델 이미지 (선택)")
    person_file = st.file_uploader("일관성을 유지할 본인의 얼굴/신체 사진", type=["jpg", "png", "jpeg"], key="person")
    
    if product_file:
        st.info("✅ 상품 이미지 업로드됨")
    if person_file:
        st.success("👤 인물 사진 감지 - '일관성 유지 모드' 활성화")

# --- 4. 메인 로직 실행 ---
if product_file:
    col1, col2 = st.columns(2)
    with col1:
        prod_img = Image.open(product_file)
        st.image(prod_img, caption="분석 대상 상품", use_container_width=True)
    with col2:
        if person_file:
            pers_img = Image.open(person_file)
            st.image(pers_img, caption="참조용 인물 (일관성 기준)", use_container_width=True)
        else:
            st.warning("⚠️ 인물 사진이 없습니다. 'AI 가상 모델 모드'로 실행됩니다.")

    if st.button("✨ 전문가용 기획서 및 실행 가이드 생성", type="primary", use_container_width=True):
        with st.spinner("AI 감독이 1.2.3번 실행 가이드를 포함한 전략을 짜는 중..."):
            try:
                # 최신 모델 사용 (사용자 디버그 리스트 0번 참조)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 인물 사진 유무에 따른 조건 설정
                identity_instruction = ""
                input_content = [prod_img]
                
                if person_file:
                    input_content.append(pers_img)
                    identity_instruction = """
                    [모드: 인물 일관성 유지]
                    - 제공된 인물의 이목구비와 체형을 상수(Constant)로 고정할 것.
                    - 프롬프트에 'Reference identity from uploaded photo' 개념을 주입할 것.
                    """
                else:
                    identity_instruction = """
                    [모드: 가상 AI 모델 생성]
                    - 상품에 가장 적합한 페르소나를 가진 가상의 프로 모델을 정의할 것.
                    """

                full_prompt = f"""
                당신은 세계 최고의 상업 사진작가이자 숏폼 디렉터입니다. 
                이미지를 분석하여 다음 4가지 결과물을 한국어로 작성하세요.

                {identity_instruction}

                ---
                **1. 📸 상품 맞춤형 촬영 스펙 (Technical Spec)**
                - 상품 카테고리 식별 및 추천 ISO, 조리개, 셔터스피드.
                - 조명 배치도 및 피사체와의 최적 거리(cm 단위).

                **2. 🎨 초고화질 이미지 생성 프롬프트 (High-End AI Prompt)**
                - 미드저니 등에서 사용할 영어 프롬프트 (정면/측면/클로즈업 3종).
                - 인물 일관성을 위한 특수 파라미터 반영.

                **3. 🎬 숏폼(15초) 영상 촬영 지시서**
                - BGM 추천 및 초 단위 구간별 구도/자막 표.

                **4. 🛠️ 외부 AI 툴 활용 가이드 (1.2.3단계)**
                이 프롬프트를 다음 도구에서 어떻게 써야 인물/상품 일관성이 유지되는지 상세히 설명하세요:
                1) 미드저니: 이미지 URL 주입법 및 --cref, --cw 파라미터 설정법.
                2) 재미나이/챗봇: 사진 재업로드 및 프롬프트 주입 요령.
                3) 스테이블 디퓨전: ControlNet 및 IP-Adapter 활용 팁.
                ---
                """

                response = model.generate_content([full_prompt] + input_content)
                
                st.balloons()
                st.success("✅ 모든 가이드가 생성되었습니다!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
else:
    st.info("👈 왼쪽 사이드바에서 상품 이미지를 먼저 올려주세요.")
