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
st.markdown("##### 상품 분석 및 개인 맞춤형/AI 전용 듀얼 프롬프트 생성기")
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

    if st.button("✨ 전문가용 기획서 및 고퀄리티 프롬프트 생성", type="primary", use_container_width=True):
        with st.spinner("AI 감독이 전략을 구성 중입니다... (15~20초 소요)"):
            try:
                # 리스트 0번의 최신 모델 사용
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # 인물 사진 유무에 따른 프롬프트 조건 분기
                identity_instruction = ""
                input_content = [prod_img]
                
                if person_file:
                    input_content.append(pers_img)
                    identity_instruction = """
                    [모드: 인물 일관성 유지(Identity Preservation)]
                    - 제공된 '인물 사진'의 얼굴 특징, 신체 비율, 피부톤을 '상수(Constant)'로 고정하십시오.
                    - 어떤 각도에서도 동일 인물로 보이도록 상세 묘사를 프롬프트에 포함하세요.
                    - Midjourney의 '--cref' 기능을 활용하기 위한 구조적 설계를 제시하세요.
                    """
                else:
                    identity_instruction = """
                    [모드: 가상 AI 모델 생성(AI Model Generation)]
                    - 이 상품의 타겟 소비층을 분석하여 가장 어울리는 '가상의 전문 모델'을 창조하세요.
                    - 성별, 인종, 연령대, 분위기를 구체적으로 설정하여 상업 화보급 외모를 정의하세요.
                    """

                full_prompt = f"""
                당신은 세계 최고의 상업 사진작가이자 숏폼 디렉터입니다. 
                다음 이미지를 분석하여 전문가용 가이드를 작성하세요.

                {identity_instruction}

                ---
                **1. 📸 상품 맞춤형 촬영 스펙 (Technical Spec)**
                - 상품 카테고리(안경, 의류, 가방 등)를 먼저 식별하세요.
                - 추천 ISO, 조리개(F-stop), 셔터스피드와 그 이유.
                - 조명 배치도(Key, Fill, Back light) 및 배경 재질 제안.
                - 피사체와의 최적 거리(cm 단위) 및 렌즈 초점거리(mm).

                **2. 🎨 초고화질 이미지 생성 프롬프트 (High-End AI Prompt)**
                - 이 상품을 착용한 상태로 다양한 각도에서 일관성을 유지하기 위한 영어 프롬프트를 작성하세요.
                - (정면, 45도 측면, 클로즈업 등 3가지 버전 제시)
                - 인물 일관성을 위한 특수 파라미터(예: --cref, --cw) 사용법 포함.

                **3. 🎬 숏폼(15초) 영상 촬영 지시서**
                - 트렌디한 BGM 추천 및 초 단위 구간별 구도/자막 내용 표 형식 작성.
                ---
                """

                response = model.generate_content([full_prompt] + input_content)
                
                st.balloons()
                st.success("✅ 기획서 생성이 완료되었습니다!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
else:
    st.info("👈 왼쪽 사이드바에서 상품 이미지를 먼저 올려주세요.")
