import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# 1. 자가 치유형 엔진 설정 (429/404 에러 방지)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Secrets에 GEMINI_API_KEY를 정확히 입력해주세요.")

def get_best_model():
    """사용 가능한 최적의 엔진을 순차적으로 탐색하여 반환"""
    # 추천 모델 순위: 2.0-flash -> 1.5-flash -> 1.5-flash-latest
    candidate_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-latest']
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            # 간단한 테스트 호출로 가용성 확인 (선택 사항)
            return model, model_name
        except:
            continue
    return None, None

model, active_model_name = get_best_model()

# 2. UI 레이아웃 최적화
st.set_page_config(page_title="PnP High-End Master", layout="wide")

# 가로 스크롤 방지 및 하이엔드 디자인 CSS
st.markdown("""
    <style>
    .stMarkdown, .stCodeBlock { white-space: pre-wrap !important; word-break: break-all !important; }
    .report-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #e1e4e8; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1a1a1a; margin-top: 30px; }
    .copy-hint { font-size: 0.8rem; color: #666; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.title("🔒 제품 고정 & 마케팅")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (디자인 락킹)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델 사진 (일관성 유지)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "블랙 & 크림 하이브리드 안경")
    theme_choice = st.selectbox("기획 무드", ["Cinematic Noir", "Minimalist Luxury", "Cyberpunk", "Vintage Classic"])
    generate_btn = st.button("🚀 하이엔드 기획서 생성", use_container_width=True)
    st.caption(f"현재 연결된 엔진: {active_model_name}")

# 메인 화면
st.title("📸 픽앤샷(Pick & Shot): 하이엔드 마케팅 센터")

if generate_btn and prod_file:
    if not model:
        st.error("❌ 현재 모든 AI 엔진의 할당량이 초과되었습니다. 1분 후 다시 시도해주세요.")
    else:
        p_img = Image.open(prod_file)
        
        # [천재 디자이너의 제품 락킹 + 한글 카피 지시어]
        instruction = f"""
        당신은 보그(Vogue) 화보를 총괄하는 상업 사진 감독입니다. 
        가장 중요한 임무: 업로드된 안경 이미지의 **'검정 전면 프레임과 대조되는 크림색(아이보리) 다리(Temples)'** 디자인을 100% 유지하며 아래 기획서를 작성하세요.

        ### [SECTION 1: 전문 촬영 기획서 (한글)]
        - 컨셉: '{theme_choice}'를 바탕으로 한 제품의 미학적 분석.
        - 촬영 기술: 촬영 각도(Eye-level), 조명(Rembrandt), ISO 100, f/2.8, 1/125s 수치 포함.

        ### [SECTION 2: 하이엔드 영문 프롬프트 3종 (한글 카피 포함)]
        *제품의 'Black frame and cream temples' 디테일을 영어로 강조하고, 이미지 내에 한글 문구를 삽입하세요.*
        1. **Minimalist Luxury Mood**: 정적인 미학. (이미지 내 한글 문구: "본연의 가치")
        2. **Atmospheric Lifestyle Mood**: 세련된 일상 공간. (이미지 내 한글 문구: "당신의 순간을 완성하다")
        3. **Artistic Avant-Garde Mood**: 고대비 예술적 연출. (이미지 내 한글 문구: "압도적 존재감")

        ### [SECTION 3: 마케팅 상세 문구 (한글)]
        - 소비자의 소유욕을 자극하는 고급스러운 카피라이팅.

        ### [SECTION 4: 인물 일관성 유지 영문 프롬프트]
        - 모델의 특징을 보존하며, 지정된 안경을 착용한 하이엔드 화보 영어 프롬프트.
        """
        
        inputs = [instruction, p_img]
        if face_file: inputs.append(Image.open(face_file))
            
        with st.spinner("AI 감독님이 할당량을 체크하며 기획서를 작성 중입니다..."):
            try:
                response = model.generate_content(inputs)
                res_text = response.text
                
                # 가로 스크롤 없이 세로로 시원하게 출력
                st.markdown("---")
                sections = res_text.split("###")
                for section in sections:
                    if section.strip():
                        st.markdown(f'<div class="report-card"><h3>{section.strip()}</h3></div>', unsafe_allow_html=True)
                
                st.balloons()
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ 할당량이 초과되었습니다. 60초만 기다렸다가 다시 '마스터피스 생성' 버튼을 눌러주세요.")
                else:
                    st.error(f"실행 오류: {str(e)}")
elif generate_btn:
    st.warning("상품 이미지를 업로드해 주세요.")
