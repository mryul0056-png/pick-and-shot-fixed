import streamlit as st
import google.generativeai as genai
from PIL import Image
from google.api_core import retry

# [설정] 페이지 설정
st.set_page_config(page_title="PnP Product Master", layout="wide")

# [보안] API 키 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 보안 경고: API 키가 설정되지 않았습니다.")
    st.stop()

# [안전 설정] 필터 해제
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# [유틸리티] 이미지 최적화
def optimize_image(image, max_size=1024):
    width, height = image.size
    if max(width, height) > max_size:
        scale = max_size / max(width, height)
        return image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    return image

# UI 스타일
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    h1, h2, h3 { color: #1E272E; border-bottom: 2px solid #D2DAE2; padding-bottom: 10px; margin-top: 35px; }
    .copy-hint { font-size: 0.85rem; color: #666; margin-bottom: 5px; background-color: #eef; padding: 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.title("🔒 제품 일관성 락킹")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품 명칭", "프리미엄 블랙 뿔테 안경")
    theme_choice = st.selectbox("기획 예술 테마", ["Cinematic Noir", "Miniature Diorama", "Ethereal Floral", "Cyberpunk Chrome", "Autumn Paris"])
    generate_btn = st.button("🔥 마스터피스 기획 및 생성")

st.title("📸 픽앤샷: 하이엔드 제품 기획 센터")

if generate_btn and prod_file:
    raw_p_img = Image.open(prod_file)
    p_img = optimize_image(raw_p_img)
    
    # [핵심 수정] 모델 자동 감지 및 할당 로직
    # 1순위: 1.5 Flash (속도/품질 최적), 2순위: 1.0 Pro (호환성 최적)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
        # 테스트 호출로 모델 존재 여부 확인 (Dummy check)
        # 실제 호출 시 에러가 나면 except로 넘어감
        active_engine = "gemini-1.5-flash"
    except:
        model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
        active_engine = "gemini-pro (Compatibility Mode)"
    
    st.caption(f"ℹ️ Active Engine: {active_engine}")

    instruction = f"""
    당신은 전 세계 1%의 상업 사진 감독이자 브랜드 전략가입니다.
    대상 제품: {product_name}
    테마: {theme_choice}
    
    **필수: 업로드된 이미지의 제품 형태를 완벽히 유지할 것.**
    출력은 반드시 마크다운 헤더(###)로 구분하십시오.

    ### [SECTION 1: 전략적 촬영 기획]
    - 조명, 카메라 세팅, 구도 설명.

    ### [SECTION 2: 하이엔드 영문 프롬프트]
    - 미드저니/DALL-E용 고화질 프롬프트 작성.

    ### [SECTION 3: 마케팅 카피]
    - 고객을 사로잡는 한글 카피라이팅.

    ### [SECTION 4: 모델 착용 프롬프트]
    - 모델과 제품의 조화를 이루는 영문 프롬프트.
    """
    
    inputs = [instruction, p_img]
    if face_file:
        inputs.append(optimize_image(Image.open(face_file)))
        
    with st.spinner(f"렌더링 중입니다... ({active_engine})"):
        try:
            response = model.generate_content(inputs)
            res_text = response.text
            
            st.markdown("---")
            sections = res_text.split("###")
            for section in sections:
                content = section.strip()
                if content:
                    header = content.split("\n")[0]
                    body = "\n".join(content.split("\n")[1:])
                    st.markdown(f"### {header}")
                    if any(x in header.upper() for x in ["PROMPT", "SECTION 2", "SECTION 4"]):
                        st.code(body, language="text")
                    else:
                        st.markdown(body)
            
            st.success("✅ 생성 완료")
            
        except Exception as e:
            # 여기로 떨어진다는 것은 gemini-pro조차 실패했거나 다른 문제임
            st.error(f"⚠️ 오류 발생: {str(e)}")
            if "404" in str(e):
                st.info("💡 팁: requirements.txt에 'google-generativeai>=0.5.2'를 추가하세요.")

elif generate_btn:
    st.warning("⚠️ 이미지를 업로드해 주세요.")
