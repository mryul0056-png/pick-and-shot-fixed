import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1] 페이지 기본 설정 ---
st.set_page_config(
    page_title="Pick & Shot: Hybrid Studio",
    page_icon="📸",
    layout="wide"
)

st.markdown("""
<style>
    /* 전체 테마: 다크 & 럭셔리 */
    .main { background-color: #0e1117; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #1c1e24; }
    
    /* 버튼 스타일: 시인성 강화 */
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

    /* 결과 리포트 박스 */
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
        # Streamlit Secrets 또는 환경변수에서 키 로드
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("🚨 API Key가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
            return False
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ 설정 오류: {str(e)}")
        return False

# --- [3] 핵심 로직: 상황별 맞춤형 분석 ---
def analyze_hybrid(product_img, model_img, vibe):
    # 최신 모델 호출 (requirements.txt 업데이트 필수)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 공통 프롬프트 (High-End Quality)
    base_instruction = f"""
    당신은 세계적인 하이엔드 광고 디렉터입니다.
    제공된 이미지를 분석하여 '{vibe}' 컨셉의 광고 촬영 기획안과 프롬프트를 작성하세요.
    
    [핵심 원칙]
    1. Product Fidelity: 상품의 디자인, 로고, 재질은 절대 변형 없이 묘사할 것.
    2. Professionalism: 조명(Softbox, Rim light), 앵글, 렌즈 스펙(85mm f/1.8)을 명시할 것.
    """

    # 분기 처리 (Branching Logic)
    if model_img:
        # Case A: 모델 사진이 있는 경우 -> 합성(Consistency) 모드
        specific_instruction = """
        [Mode: Product + Model Integration]
        - 두 번째 이미지(Model)의 인물 특징(얼굴, 헤어, 체형)을 최대한 유지하세요.
        - 모델이 상품을 자연스럽게 착용하거나 사용하고 있는 컷을 연출하세요.
        """
        # 이미지 리스트에 두 장 모두 포함
        content = [base_instruction + specific_instruction, product_img, model_img]
    else:
        # Case B: 상품만 있는 경우 -> 가상 모델 추천(Casting) 모드
        specific_instruction = f"""
        [Mode: Virtual Model Casting]
        - 현재 모델 이미지가 없습니다. 상품과 '{vibe}' 분위기에 가장 완벽하게 어울리는 모델을 AI가 추천하세요.
        - 예: '시크한 표정의 20대 여성 모델' 또는 '제품이 돋보이는 미니멀한 손 모델' 등 구체적으로 묘사하세요.
        """
        # 이미지 리스트에 상품만 포함
        content = [base_instruction + specific_instruction, product_img]

    # 출력 포맷 지정
    format_instruction = """
    결과는 다음 두 파트로 명확히 나누어 출력하세요:
    
    PART 1. [Creative Director Report] (Korean)
    - 촬영 컨셉 및 전략
    - (모델 미지정 시) 추천 모델 및 스타일링 가이드
    - 조명 및 세트장 구성
    
    PART 2. [Prompt for Midjourney/Stable Diffusion] (English)
    - 복사해서 바로 사용할 수 있는 프롬프트 텍스트만 작성.
    - 설명 텍스트 제외. --ar 4:5 --v 6.0 등의 파라미터 포함.
    """
    
    # 텍스트 프롬프트 합치기
    if isinstance(content[0], str):
        content[0] += format_instruction

    with st.spinner('🎬 AI Director is analyzing & designing...'):
        try:
            response = model.generate_content(content)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- [4] UI 레이아웃 ---
def main():
    # 사이드바: 입력 및 실행 컨트롤 타워
    with st.sidebar:
        st.title("Pick & Shot 📸")
        st.caption("Hybrid AI Studio")
        
        st.header("1. Upload Assets")
        # 상품 업로드 (필수)
        product_file = st.file_uploader("📦 상품 이미지 (Product)", type=["jpg", "png", "webp"])
        
        st.markdown("---")
        # 모델 업로드 (선택) - 안내 문구 강화
        model_file = st.file_uploader("bust_in_silhouette: 모델 이미지 (Optional)", type=["jpg", "png", "webp"], 
                                    help="모델 사진을 넣으면 합성을, 안 넣으면 AI가 어울리는 모델을 추천해줍니다.")
        
        st.header("2. Concept")
        vibe_option = st.selectbox(
            "촬영 분위기",
            ["Luxury Studio (명품/미니멀)", "Cinematic Film (영화 같은 연출)", 
             "Urban Street (힙합/스트릿)", "Nature Sunlight (자연광/감성)"]
        )
        
        st.markdown("---")
        # 실행 버튼 (항상 노출)
        analyze_btn = st.button("✨ 기획안 및 프롬프트 생성")

    # 메인 화면: 프리뷰 및 결과
    st.markdown("### 🎞️ Studio Preview")

    col1, col2 = st.columns(2)
    p_img = None
    m_img = None

    # 프리뷰 로직
    with col1:
        if product_file:
            p_img = Image.open(product_file)
            st.image(p_img, caption="Main Product", use_column_width=True)
        else:
            st.info("👈 왼쪽에서 '상품' 이미지를 먼저 올려주세요.")

    with col2:
        if model_file:
            m_img = Image.open(model_file)
            st.image(m_img, caption="Reference Model", use_column_width=True)
        else:
            # 모델 사진 없을 때 빈 공간 대신 안내 UI 표시
            st.markdown("""
            <div style="
                border: 2px dashed #444; 
                border-radius: 10px; 
                padding: 40px; 
                text-align: center; 
                color: #888;">
                🕵️‍♀️ <b>모델 사진 없음</b><br>
                AI가 상품에 맞는 모델을<br>자동으로 캐스팅합니다.
            </div>
            """, unsafe_allow_html=True)

    # 실행 로직
    if analyze_btn:
        if not product_file:
            st.warning("⚠️ 분석을 시작하려면 최소한 '상품 이미지'는 필요합니다!")
        else:
            if configure_genai():
                # 하이브리드 분석 함수 호출
                result_text = analyze_hybrid(p_img, m_img, vibe_option)
                st.session_state['final_result'] = result_text

    # 결과 출력
    if 'final_result' in st.session_state:
        st.markdown("---")
        full_text = st.session_state['final_result']
        
        st.header("📋 Creative Director's Report")
        st.markdown(f'<div class="report-box">{full_text}</div>', unsafe_allow_html=True)
        
        st.subheader("📋 One-Click Copy Prompt")
        st.code(full_text, language="text")

if __name__ == "__main__":
    main()
