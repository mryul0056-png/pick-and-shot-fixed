import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import time

# --- [1] 페이지 및 스타일 설정 (High-End Mood) ---
st.set_page_config(
    page_title="Pick & Shot: Director's Cut",
    page_icon="📸",
    layout="wide"
)

st.markdown("""
<style>
    /* 전체 배경 및 폰트 설정 */
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* 사이드바 스타일링 */
    section[data-testid="stSidebar"] {
        background-color: #1c1e24;
    }
    
    /* 버튼 스타일링 (눈에 띄게) */
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
    .stButton>button:hover {
        background-color: #FF2B2B;
        color: white;
    }

    /* 결과 박스 스타일링 */
    .report-box {
        background-color: #262730;
        padding: 25px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
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

# --- [3] 핵심 로직: Gemini Vision Analysis ---
def analyze_dual_images(product_img, model_img, vibe):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 전문가 프롬프트 (수정 금지: 일관성 유지 핵심 로직)
    prompt = f"""
    당신은 세계 최고의 하이엔드 광고 디렉터입니다.
    다음 두 이미지를 분석하여 완벽한 광고 촬영 기획안을 작성해주세요.
    
    [입력 이미지]
    1. Product Image: 판매할 상품 (디테일, 로고, 재질 유지 필수)
    2. Model/Ref Image: 모델의 외형, 포즈, 분위기 (Subject Consistency 유지 필수)
    
    [요청 사항]
    분위기: '{vibe}'
    
    결과는 다음 두 부분으로 나누어 출력하세요:
    
    PART 1. [크리에이티브 디렉팅 리포트] (한글 작성)
    - 컨셉 설명
    - 조명 및 앵글 세팅 가이드
    - 모델 포즈 및 스타일링 지시
    
    PART 2. [Midjourney/Stable Diffusion Prompt] (영어 작성)
    - 반드시 복사해서 바로 쓸 수 있는 프롬프트 텍스트만 작성.
    - /imagine prompt: 로 시작하지 말고 순수 프롬프트 내용만 작성.
    - 포함 키워드: hyper-realistic, 8k, highly detailed, professional photography, {vibe} style
    """
    
    with st.spinner('🎬 Director is analyzing the scene...'):
        try:
            response = model.generate_content([prompt, product_img, model_img])
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# --- [4] 메인 UI 레이아웃 (Layout Logic) ---
def main():
    # --- [A] 사이드바: 컨트롤 타워 (입력 & 실행) ---
    with st.sidebar:
        st.title("Pick & Shot 📸")
        st.caption("Professional AI Studio")
        
        st.header("1. Upload Assets")
        product_file = st.file_uploader("📦 상품 이미지 (Product)", type=["jpg", "png", "webp"])
        model_file = st.file_uploader("bust_in_silhouette: 모델/참고 이미지 (Model)", type=["jpg", "png", "webp"])
        
        st.markdown("---")
        st.header("2. Select Vibe")
        vibe_option = st.selectbox(
            "원하는 촬영 분위기",
            ["Luxury Studio (명품/미니멀)", "Cinematic Film (영화 같은 연출)", 
             "Urban Street (힙합/스트릿)", "Nature Sunlight (자연광/감성)"]
        )
        
        st.markdown("---")
        # 실행 버튼을 사이드바 하단에 배치 (항상 보임)
        analyze_btn = st.button("✨ 기획안 및 프롬프트 생성")

    # --- [B] 메인 화면: 결과 및 프리뷰 ---
    st.markdown("### 🎞️ Studio Preview")

    # 이미지가 업로드되면 미리보기 표시
    col1, col2 = st.columns(2)
    p_img = None
    m_img = None

    with col1:
        if product_file:
            p_img = Image.open(product_file)
            st.image(p_img, caption="Main Product", use_column_width=True)
        else:
            st.info("👈 왼쪽에서 상품을 업로드해주세요.")

    with col2:
        if model_file:
            m_img = Image.open(model_file)
            st.image(m_img, caption="Reference Model", use_column_width=True)
        else:
            st.info("👈 왼쪽에서 모델을 업로드해주세요.")

    # --- [C] 실행 로직 & 결과 출력 ---
    if analyze_btn:
        if not product_file or not model_file:
            st.warning("⚠️ 상품과 모델 이미지를 모두 업로드해야 분석이 가능합니다.")
        else:
            if configure_genai():
                # 분석 실행
                result_text = analyze_dual_images(p_img, m_img, vibe_option)
                st.session_state['final_result'] = result_text

    # 결과가 있으면 출력 (복사 기능 포함)
    if 'final_result' in st.session_state:
        st.markdown("---")
        full_text = st.session_state['final_result']
        
        # 텍스트 파싱: 프롬프트와 리포트 분리 시도 (간단한 파싱 로직)
        # 만약 PART 2가 명확하지 않다면 전체 출력
        
        st.header("📋 Creative Director's Report")
        
        # 1. 리포트 출력 (Markdown)
        st.markdown(f'<div class="report-box">{full_text}</div>', unsafe_allow_html=True)
        
        # 2. 복사 전용 프롬프트 박스 (Code Block 활용)
        st.subheader("📋 Copy Prompt (One-Click)")
        st.caption("우측 상단의 복사 버튼을 누르세요.")
        
        # 프롬프트만 추출하는 간단한 로직 (영어 부분 예시)
        # 실제로는 AI가 준 전체 텍스트에서 사용자가 복사할 부분을 찾기 쉽게 
        # 전체 텍스트를 코드 블록에 한번 더 넣어주는 것이 가장 안전합니다.
        st.code(full_text, language="text")

if __name__ == "__main__":
    main()
