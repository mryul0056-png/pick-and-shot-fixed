import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. API 설정 및 모델 로드
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    # 모델명 앞에 'models/'를 붙이는 것이 최신 규격입니다.
    model = genai.GenerativeModel('models/gemini-1.5-pro')

class PnP_StudioEngine:
    """3대 산출물(제품/기획/모델) 통합 엔진"""
    
    THEMES = {
        "시네마틱 누아르(Cinematic Noir)": "도시의 차가운 야경, 비 내리는 질감, 안경 렌즈의 날카로운 빛 반사.",
        "미니어처 디오라마(Miniature Diorama)": "거대한 제품과 대비되는 작은 피규어 배치, 틸트-시프트 기법.",
        "신비로운 꽃의 여신(Ethereal Floral)": "몽환적 파스텔 톤, 제품을 감싸는 꽃잎, 부드러운 채광.",
        "크리스마스 박스(Christmas Box)": "연말의 따뜻함, 레드/골드 포인트 조명, 선물 같은 구도.",
        "사이버펑크 크롬(Cyberpunk Chrome)": "네온 블루와 핑크 조명, 금속성의 차가운 반사광.",
        "K-팝 코트사이드(K-pop Courtside)": "에너지 넘치는 원색 대비, 경기장 서치라이트 효과.",
        "가을 파리 OOTD(Autumn Paris)": "빈티지 브라운 톤, 유럽 거리의 부드러운 일몰 광선."
    }

    @staticmethod
    def get_system_instruction(theme_key, product_name):
        desc = PnP_StudioEngine.THEMES.get(theme_key)
        return f"""
        당신은 상업 사진 작가이자 마케팅 전문가입니다. 업로드된 이미지를 분석하여 3가지 산출물을 작성하세요.

        1. [Product-Only Prompt]: 제품과 배경만 나오는 화보용 프롬프트. (사람 제외)
        2. [Marketing Copy]: 상세페이지에 들어갈 제품 특징과 감성적인 카피 문구.
        3. [Model-Product Prompt]: 업로드된 모델(또는 본인)이 제품을 착용한 화보용 프롬프트.
        
        사양: Hasselblad 100MP, 85mm f/1.8, razor-sharp focus, 8k resolution 필수 포함.
        """

# --- UI/UX 개편 ---
st.set_page_config(page_title="Pick & Shot Master Pro", layout="wide")

# 사이드바: 모든 설정과 업로드를 좌측으로 배치
with st.sidebar:
    st.title("⚙️ 픽앤픽 설정")
    st.markdown("---")
    prod_file = st.file_uploader("1. 상품 이미지 (필수)", type=['png', 'jpg', 'jpeg'])
    face_file = st.file_uploader("2. 모델/본인 사진 (선택)", type=['png', 'jpg', 'jpeg'])
    product_name = st.text_input("제품명", "프리미엄 제품")
    theme_choice = st.selectbox("기획안 테마", list(PnP_StudioEngine.THEMES.keys()))
    
    generate_btn = st.button("🔥 마스터피스 생성 시작", use_container_width=True)
    
    st.markdown("---")
    st.header("📖 한글설명(Manual)")
    st.info("재미나이가 상품의 질감을 읽어 기획안과 프롬프트를 동시에 작성합니다.")

# 메인 화면: 결과 중심 정렬
st.title("📸 픽앤픽(Pick & Shot): 전문 기획 센터")

if generate_btn:
    if not GOOGLE_API_KEY:
        st.error("API Key가 설정되지 않았습니다.")
    elif prod_file:
        p_img = Image.open(prod_file)
        instruction = PnP_StudioEngine.get_system_instruction(theme_choice, product_name)
        inputs = [instruction, p_img]
        if face_file:
            inputs.append(Image.open(face_file))
            
        with st.spinner("재미나이가 기획안을 빌드 중입니다..."):
            try:
                response = model.generate_content(inputs)
                
                # 탭 구조를 사용하여 결과물을 깔끔하게 분리
                tab1, tab2, tab3 = st.tabs(["🖼 제품 단독 화보", "📝 상세페이지 기획", "👤 모델 기반 화보"])
                
                content = response.text
                # 결과 텍스트를 파싱하여 각 탭에 배치 (실제로는 재미나이에게 구분을 요청)
                with tab1:
                    st.subheader("제품 + 배경 중심 프롬프트")
                    st.write("모델 없이 제품의 질감과 배경의 조화에 집중합니다.")
                    st.code(content.split("2.")[0].replace("1.", ""), language='text')
                
                with tab2:
                    st.subheader("상세페이지 마케팅 문구")
                    st.write("고객을 유혹하는 감성 카피와 기획 포인트입니다.")
                    if "2." in content:
                        st.markdown(content.split("2.")[1].split("3.")[0])
                
                with tab3:
                    st.subheader("인물 일관성 기반 프롬프트")
                    st.write("업로드된 모델 사진의 특징을 유지하며 제품을 노출합니다.")
                    if "3." in content:
                        st.code(content.split("3.")[1], language='text')
                
                st.success("✅ 모든 산출물이 정렬되었습니다.")
                
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
    else:
        st.error("상품 사진을 업로드해주세요.")
else:
    st.info("좌측 사이드바에서 설정을 마친 후 생성 버튼을 눌러주세요.")
