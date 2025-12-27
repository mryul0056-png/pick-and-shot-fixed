import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- [1] 페이지 기본 설정 (가장 먼저 실행) ---
st.set_page_config(
    page_title="Pick & Shot: High-End Studio",
    page_icon="📸",
    layout="wide"
)

# --- [2] 스타일링 (CSS) ---
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; color: #FAFAFA; }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .report-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- [3] API 키 및 모델 설정 (안전장치 포함) ---
def configure_genai():
    try:
        # Streamlit Secrets에서 키를 가져오거나 환경변수 확인
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            st.error("🚨 치명적 오류: GOOGLE_API_KEY가 설정되지 않았습니다.")
            st.info("Streamlit 설정(Secrets) 또는 .env 파일에 API 키를 입력해주세요.")
            st.stop() # 앱 실행 중단
            
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"⚠️ 설정 오류 발생: {str(e)}")
        return False

# --- [4] 핵심 로직: 하이엔드 프롬프트 생성기 ---
def analyze_image(image, vibe):
    # 모델 선택 (Vision 기능이 탁월한 1.5 Flash 사용)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 🌟 [전문가 페르소나 주입] 
    # 당신은 보스턴 컨설팅 그룹 출신의 상품 기획자이자 보그(Vogue) 수석 포토그래퍼입니다.
    prompt = f"""
    당신은 세계 최고의 상업 사진 작가이자 상품 기획자입니다.
    업로드된 제품 이미지를 분석하여 다음 3가지를 한국어로 작성해주세요.
    
    분위기(Vibe) 설정: {vibe}
    
    1. [상품 본질 분석]: 이 상품의 핵심 매력 포인트와 타겟 고객층 (전문적 용어 사용)
    2. [럭셔리 스튜디오 세팅]: 조명(Lighting), 앵글(Angle), 배경(Background), 소품(Props)에 대한 구체적인 지시
    3. [이미지 생성 프롬프트]: Midjourney나 Stable Diffusion에 넣었을 때 최고급 결과물이 나올 수 있는 영어 프롬프트 (Hyper-realistic, 8k, Detailed texture 등 포함)
    
    출력 형식은 깔끔한 마크다운으로 해주세요.
    """
    
    with st.spinner('📸 AI 디렉터가 상품을 분석하고 촬영 컨셉을 잡는 중...'):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Error: 분석 중 문제가 발생했습니다. ({str(e)})"

# --- [5] UI 레이아웃 (사용자 경험 최적화) ---
def main():
    st.title("Pick & Shot 📸")
    st.caption("High-End Product Photography AI Director")
    
    # 사이드바: 설정 및 이미지 업로드
    with st.sidebar:
        st.header("Step 1. Studio Setup")
        uploaded_file = st.file_uploader("상품 이미지를 올려주세요", type=["jpg", "png", "jpeg", "webp"])
        
        st.header("Step 2. Concept")
        vibe_option = st.selectbox(
            "원하는 분위기 (Vibe) 선택",
            ["Luxury & Minimal (고급/미니멀)", "Neon & Cyberpunk (힙합/네온)", "Nature & Organic (자연주의)", "Vintage & Warm (빈티지/따뜻함)"]
        )
        
        st.markdown("---")
        st.info("💡 팁: 해상도가 높은 원본 이미지를 사용할수록 분석 결과가 정확합니다.")

    # 메인 화면: 결과 출력
    if uploaded_file is not None:
        # 이미지 로드 및 표시
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(image, caption='Original Product', use_column_width=True)
            
        with col2:
            st.markdown("### 🎯 Ready to Analyze")
            if st.button("전문가 분석 및 기획안 생성 (Start)"):
                if configure_genai(): # API 설정 검증
                    result = analyze_image(image, vibe_option)
                    st.session_state['result'] = result # 결과 저장 (새로고침 방지)

        # 결과가 있으면 화면 하단에 표시 (상태 유지)
        if 'result' in st.session_state:
            st.markdown("---")
            st.subheader("📋 Professional Report")
            st.markdown(f'<div class="report-box">{st.session_state["result"]}</div>', unsafe_allow_html=True)
            
    else:
        # 대기 화면
        st.markdown("""
        ### 👋 환영합니다, Creator님.
        **Pick & Shot**은 당신의 제품을 명품으로 만들어줄 AI 크리에이티브 디렉터입니다.
        왼쪽 사이드바에서 이미지를 업로드하여 시작하세요.
        """)

if __name__ == "__main__":
    main()
