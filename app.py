import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(page_title="Pick & Shot: Model x Product", page_icon="📸", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stFileUploader"] {
        border: 1px dashed #FF4B4B;
        padding: 10px;
        border-radius: 10px;
    }
    .report-box {
        background-color: #262730;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-top: 20px;
        line-height: 1.6;
    }
    h3 { color: #FAFAFA !important; }
</style>
""", unsafe_allow_html=True)

# --- [2] API 키 설정 (안전장치) ---
def configure_genai():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("🚨 API Key가 없습니다. Streamlit Secrets에 'GOOGLE_API_KEY'를 설정해주세요.")
            st.stop()
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ 설정 오류: {str(e)}")
        return False

# --- [3] 핵심 로직: 듀얼 비전 분석 (상품 + 모델) ---
def analyze_dual_images(product_img, model_img, vibe):
    # 최신 모델 사용 (Flash가 안되면 Pro로 자동 전환 고려, 여기선 Flash 강제)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 🌟 [일관성 유지 프롬프트] 
    # 상품의 변형을 막고, 모델의 특징을 유지하며 합성하는 전문 지침
    prompt = f"""
    당신은 세계 최고의 광고 감독이자 AI 프롬프트 엔지니어입니다.
    두 장의 이미지가 입력되었습니다.
    
    - [이미지 1]: 판매할 '상품(Product)' (절대 변형되어서는 안 됨)
    - [이미지 2]: 광고 모델(Model) 또는 레퍼런스 인물 (이 사람의 외형/특징 유지)
    
    요청사항: 
    이 두 이미지를 합성하여 '{vibe}' 분위기의 하이엔드 광고 사진을 만들기 위한
    'Midjourney' 또는 'Stable Diffusion' 전용 영어 프롬프트를 작성해주세요.
    
    필수 포함 항목:
    1. [Subject Consistency]: 모델의 얼굴, 헤어스타일, 체형을 상세히 묘사 (이미지 2 기준).
    2. [Product Fidelity]: 상품의 색상, 재질, 로고 위치를 정확히 묘사 (이미지 1 기준). 모델이 상품을 자연스럽게 착용하거나 들고 있는 포즈 묘사.
    3. [Environment & Lighting]: '{vibe}'에 맞는 배경, 조명, 카메라 앵글, 렌즈 스펙 (예: 85mm, f/1.8).
    4. [Negative Prompt]: 왜곡, 낮은 해상도, 손가락 기형 등을 방지하는 키워드.
    
    출력은 한글 설명과 영어 프롬프트 블록으로 나누어 깔끔하게 작성해주세요.
    """
    
    with st.spinner('📸 상품과 모델을 매칭하여 최적의 컷을 설계 중입니다...'):
        try:
            # 두 장의 이미지와 텍스트를 리스트로 전달
            response = model.generate_content([prompt, product_img, model_img])
            return response.text
        except Exception as e:
            return f"Error: 분석 중 문제가 발생했습니다. ({str(e)})"

# --- [4] 메인 UI 레이아웃 ---
def main():
    st.title("Pick & Shot : Model Edition 📸")
    st.caption("Custom Model & Product Integration AI Director")
    
    # 사이드바: 옵션 설정
    with st.sidebar:
        st.header("Step 3. Concept")
        vibe_option = st.selectbox(
            "촬영 분위기 (Vibe)",
            ["Luxury Studio (명품/스튜디오)", "Outdoor Natural (야외/자연광)", 
             "Cyberpunk Neon (미래지향/네온)", "Cinematic Film (영화 같은 연출)"]
        )
        st.markdown("---")
        st.info("💡 팁: 모델 사진은 얼굴이 선명한 것이 좋고, 상품 사진은 누끼(배경제거)가 없어도 괜찮습니다.")

    # 메인: 2단 업로드 (상품 vs 모델)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Step 1. 상품 (Product)")
        product_file = st.file_uploader("상품 사진 업로드", type=["jpg", "png", "webp"], key="prod")
        if product_file:
            p_img = Image.open(product_file)
            st.image(p_img, caption="Main Product", use_column_width=True)

    with col2:
        st.subheader("Step 2. 모델 (Model)")
        model_file = st.file_uploader("모델/레퍼런스 사진 업로드", type=["jpg", "png", "webp"], key="mod")
        if model_file:
            m_img = Image.open(model_file)
            st.image(m_img, caption="Target Model", use_column_width=True)

    # 실행 버튼 (두 이미지가 모두 있을 때만 활성화)
    st.markdown("---")
    if product_file and model_file:
        if st.button("✨ 모델 착용컷 기획안 & 프롬프트 생성 (Start)"):
            if configure_genai():
                # 이미지 객체 다시 로드 (안전성 확보)
                p_img = Image.open(product_file)
                m_img = Image.open(model_file)
                
                result = analyze_dual_images(p_img, m_img, vibe_option)
                st.session_state['dual_result'] = result
    
    elif not product_file and not model_file:
        st.info("👆 위 두 영역에 '상품'과 '모델' 사진을 각각 올려주세요.")

    # 결과 출력창
    if 'dual_result' in st.session_state:
        st.subheader("📋 Perfect Match Prompt Report")
        st.markdown(f'<div class="report-box">{st.session_state["dual_result"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
