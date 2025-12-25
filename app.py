import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. 지능형 모델 초기화 (404 에러 원천 차단)
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

def initialize_engine():
    if not GOOGLE_API_KEY:
        return None, "API 키가 등록되지 않았습니다."
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 404 에러 방지를 위한 가용 모델 리스트 체크
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 최신 Pro 모델 우선순위, 없으면 Flash로 자동 전환
        target = next((m for m in available_models if 'gemini-1.5-pro' in m), 
                      next((m for m in available_models if 'gemini-1.5-flash' in m), None))
        if target:
            return genai.GenerativeModel(target), f"연결 성공: {target.split('/')[-1]}"
        return None, "사용 가능한 모델이 없습니다."
    except:
        # 긴급 폴백 모델
        return genai.GenerativeModel('gemini-1.5-flash'), "시스템 안정화 모드로 연결됨"

model, model_status = initialize_engine()

# 2. 기획 테마 정의
THEMES = {
    "시네마틱 누아르(Cinematic Noir)": "어두운 명암 대비, 안경 렌즈의 날카로운 빛 반사.",
    "미니어처 디오라마(Miniature Diorama)": "제품을 거대하게, 주변 피규어는 작게 배치하는 연출.",
    "신비로운 꽃의 여신(Ethereal Floral)": "몽환적인 파스텔 톤과 꽃잎의 신비로운 조화.",
    "크리스마스 박스(Christmas Box)": "따뜻하고 화려한 연말 선물 컨셉 조명.",
    "사이버펑크 크롬(Cyberpunk Chrome)": "미래지향적 금속 질감과 네온 조명 효과."
}

# --- UI/UX 레이아웃 (정렬 최적화) ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.caption(f"엔진 상태: {model_status}")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명 입력", "프리미엄 제품")
    theme_choice = st.selectbox("기획 테마 선택", list(THEMES.keys()))
    generate_btn = st.button("🔥 마스터피스 기획 시작", use_container_width=True)
    
    st.markdown("---")
    st.header("📖 한글설명(Manual)")
    st.markdown("""
    1. **사진 업로드**: 상품과 본인 사진을 올립니다.
    2. **테마 선택**: 기획안에 맞는 예술 테마를 고릅니다.
    3. **재미나이 실행**: AI가 기획안과 프롬프트를 분리 생성합니다.
    """)

st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if not model:
        st.error(model_status)
    elif prod_file:
        p_img = Image.open(prod_file)
        instruction = f"""
        당신은 세계 최고의 상업 사진 작가입니다. 반드시 아래 3개 섹션으로 구분하여 응답하세요.
        
        [PART 1: PRODUCT ONLY]
        {product_name}과 배경만 나오는 상업 화보용 영어 프롬프트. (Hasselblad 100MP, 8k 사양 포함)

        [PART 2: MARKETING COPY]
        이 상품을 위한 상세페이지용 한글 마케팅 문구와 기획 의도.

        [PART 3: MODEL PHOTO]
        업로드된 모델이 {product_name}을 착용한 화보용 영어 프롬프트.
        """
        inputs = [instruction, p_img]
        if face_file: inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이가 고퀄리티 기획안을 작성 중입니다..."):
            try:
                response = model.generate_content(inputs)
                content = response.text
                
                # 결과 탭 분리
                tab1, tab2, tab3 = st.tabs(["🖼 제품 화보 프롬프트", "📝 상세페이지 기획", "👤 모델 화보 프롬프트"])
                
                with tab1:
                    st.code(content.split("[PART 2]")[0].replace("[PART 1]", "").strip(), language='text')
                with tab2:
                    if "[PART 2]" in content:
                        st.markdown(content.split("[PART 2]")[1].split("[PART 3]")[0].strip())
                with tab3:
                    if "[PART 3]" in content:
                        st.code(content.split("[PART 3]")[1].strip(), language='text')
                st.success("✅ 모든 산출물이 정렬되었습니다.")
            except Exception as e:
                st.error(f"오류: {str(e)}")
    else:
        st.error("상품 사진을 업로드해 주세요.")
