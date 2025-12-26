import streamlit as st
import google.generativeai as genai
from PIL import Image

# [설정] 페이지 설정
st.set_page_config(page_title="PnP Product Master", layout="wide")

# [보안] API 키 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 오류: Secrets에 GEMINI_API_KEY가 있는지 확인하세요.")
    st.stop()

# [핵심 수정] 구버전 라이브러리 호환을 위해 'gemini-pro'로 강제 고정
# gemini-1.5-flash는 라이브러리 업데이트 전까지 사용 불가합니다.
MODEL_ENGINE = 'gemini-pro' 

# UI 스타일
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.title("🔒 제품 일관성 락킹")
    prod_file = st.file_uploader("상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    theme_choice = st.selectbox("테마 선택", ["Cinematic Noir", "Minimal Luxury", "Cyberpunk"])
    generate_btn = st.button("🔥 생성 시작")
    st.caption(f"Engine: {MODEL_ENGINE} (Compatibility Mode)")

st.title("📸 픽앤샷: 하이엔드 기획 (호환 모드)")

if generate_btn and prod_file:
    p_img = Image.open(prod_file)
    model = genai.GenerativeModel(MODEL_ENGINE)
    
    instruction = f"""
    당신은 전문 크리에이티브 디렉터입니다.
    제품: 안경
    테마: {theme_choice}
    
    1. 이 제품을 위한 매력적인 마케팅 카피 3가지를 작성하세요.
    2. 미드저니용 프롬프트를 영어로 작성하세요.
    """
    
    with st.spinner("구형 엔진으로 렌더링 중... (화질/속도가 낮을 수 있음)"):
        try:
            response = model.generate_content([instruction, p_img])
            st.markdown(response.text)
            st.success("✅ 생성 완료")
        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.info("💡 이 오류까지 뜬다면 API 키가 틀렸거나 구글 클라우드 문제입니다.")
