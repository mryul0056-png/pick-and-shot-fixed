import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] 페이지 및 스타일 설정 ---
st.set_page_config(
    page_title="Pick & Shot: Hybrid Director",
    page_icon="📸",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1c1e24; }
    
    /* 버튼 스타일 */
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        height: 55px;
        font-weight: 800;
        font-size: 18px;
        margin-top: 20px;
        border: none;
    }
    .stButton>button:hover { background-color: #FF2B2B; color: white; }

    /* 리포트 박스 */
    .report-box {
        background-color: #262730;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- [2] API 키 설정 ---
def configure_genai():
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("🚨 System Error: API Key가 없습니다. 설정(Secrets)을 확인해주세요.")
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ 설정 오류: {str(e)}")
        return False

# --- [3] 핵심 로직: 하이브리드 분석 (상품 Only vs 상품+모델) ---
def analyze_campaign(product_img, model_img, vibe):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 1. 기본 프롬프트 (공통)
    base_prompt = f"""
    당신은 세계 최고의 하이엔드 광고 디렉터입니다.
    입력된 이미지를 바탕으로 '{vibe}' 컨셉의 광고 촬영 기획안과 프롬프트를 작성하세요.
    
    [필수 조건]
    1. Product Fidelity: 상품의 디자인, 로고, 재질은 절대 변형 없이 묘사할 것.
    2. High-End Quality: 전문 조명(Softbox, Rim light)과 카메라 세팅(85mm f/1.8)을 명시할 것.
    """

    # 2. 상황별 프롬프트 분기 (Logic Branching)
    if model_img:
        # Case A: 모델 사진이 있는 경우 (합성 모드)
        specific_prompt = """
        [추가 지시사항 - 모델 합성]
        - 두 번째 이미지(Model Image)의 인물 특징(얼굴, 헤어, 체형)을 그대로 유지하세요.
        - 모델이 상품을 자연스럽게 착용하거나 들고 있는 포즈를 묘사하세요.
        """
        content = [base_prompt + specific_prompt, product_img, model_img]
    else:
        # Case B: 상품만 있는 경우 (가상 모델 추천 모드)
        specific_prompt = f"""
        [추가 지시사항 - 모델 가상 추천]
        - 현재 모델 이미지가 없습니다. 상품과 '{vibe}' 분위기에 가장 잘 어울리는 최적의 모델(성별, 나이, 스타일)을 AI가 창의적으로 제안해서 묘사하세요.
        - 예: '시크한 표정의 금발 숏컷 여성 모델' 또는 '미니멀한 배경의 정물 촬영' 등 상품에 최적화된 연출.
        """
        content = [base_prompt + specific_prompt, product_img]

    # 3. 출력 형식 지정
    format_prompt = """
    
    결과는 다음 두 부분으로 명확히 구분해 출력하세요:
    
    PART 1. [크리에이티브 디렉팅 리포트] (한글)
    - 컨셉 및 전략
    - (모델이 없으면) 추천 모델 스타일링 제안
    - 조명 및 촬영 세팅
    
    PART 2. [Midjourney/Stable Diffusion Prompt] (영어)
    - 바로 복사해서 쓸 수 있는 프롬프트 텍스트만 작성 (설명 제외).
    - --ar 4:5 --v 6.0 등의 파라미터 포함.
    """
    
    # 최종 컨텐츠 조합 (문자열 리스트의 마지막에 포맷 지침 추가)
    if isinstance(content[0], str):
        content[0] += format_prompt
        
    with st.spinner('🎬 AI Director is designing the campaign...'):
        try:
            response = model.generate_content(content)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- [4] 메인 UI ---
def main():
    # 사이드바
    with st.sidebar:
        st.title("Pick & Shot 📸")
        st.caption("All-in-One AI Studio")
        
        st.header("1. Upload Assets")
        # 상품은 필수
        product_file = st.file_uploader("📦 상품 이미지 (필수)", type=["jpg", "png", "webp"])
        
        # 모델은 선택사항으로 변경
        st.markdown("---")
        model_file = st.file_uploader("bust_in_silhouette: 모델 이미지 (선택사항)", type=["jpg", "png", "webp"], help="모델 사진을 넣으면 합성을, 안 넣으면 AI가 어울리는 모델을 추천해줍니다.")
        
        st.markdown("---")
        st.header("2. Concept")
        vibe_option = st.selectbox(
            "촬영 분위기",
            ["Luxury Studio (명품/미니멀)", "Cinematic Film (영화 같은 연출)", 
             "Urban Street (힙합/스트릿)", "Nature Sunlight (자연광/감성)"]
        )
        
        st.markdown("---")
        analyze_btn = st.button("✨ 기획안 및 프롬프트 생성")

    # 메인 화면
    st.markdown("### 🎞️ Studio Preview")

    col1, col2 = st.columns(2)
    p_img = None
    m_img = None

    with col1:
        if product_file:
            p_img = Image.open(product_file)
            st.image(p_img, caption="Main Product", use_column_width=True)
        else:
            st.info("👈 왼쪽에서 '상품' 이미지를 먼저 올려주세요.")

    with col2:
        if model_file:
            m_img = Image.open(model_file)
            st.image(m_img, caption="Model (Reference)", use_column_width=True)
        else:
            st.markdown("""
            <div style='padding: 20px; border: 1px dashed #555; border-radius: 10px; text-align: center; color: #888;'>
                모델 사진 없음<br>(AI가 자동으로 모델을 추천합니다)
            </div>
            """, unsafe_allow_html=True)

    # 실행 로직
    if analyze_btn:
        if not product_file:
            st.warning("⚠️ '상품 이미지'는 반드시 필요합니다!")
        else:
            if configure_genai():
                # 모델 이미지가 없으면 None으로 처리됨
                result_text = analyze_campaign(p_img, m_img, vibe_option)
                st.session_state['final_result'] = result_text

    # 결과 출력
    if 'final_result' in st.session_state:
        st.markdown("---")
        full_text = st.session_state['final_result']
        
        st.header("📋 Creative Director's Report")
        st.markdown(f'<div class="report-box">{full_text}</div>', unsafe_allow_html=True)
        
        st.subheader("📋 Copy Prompt (One-Click)")
        st.caption("아래 코드를 복사하여 미드저니/스테이블 디퓨전에 붙여넣으세요.")
        st.code(full_text, language="text")

if __name__ == "__main__":
    main()
