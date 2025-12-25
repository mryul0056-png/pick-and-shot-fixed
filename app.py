import streamlit as st
import os

class PnP_MasterEngine:
    """상품과 인물의 조화를 만드는 천재적 프롬프트 엔진"""
    
    TECH_MACRO = "shot on Hasselblad H6D, 100mm Macro, f/2.8, razor-sharp focus on product textures, 8k resolution."
    
    @staticmethod
    def generate_consistency_prompt(product_info, gender, bg_style, use_ref_image=False):
        # 인물 일관성 유지를 위한 지시어 포함
        ref_instruction = "Maintain the facial identity and features from the attached reference photo perfectly." if use_ref_image else f"A trendy Korean {gender} influencer model."
        
        backgrounds = {
            "Geometric": "minimalist architectural space, golden ratio shadows, luxury marble.",
            "Fantasy": "ethereal dreamscape, floating crystals, iridescent lighting, surreal floral.",
            "City": "Seoul night view penthouse, neon reflections, glass and steel."
        }
        
        prompt = (
            f"Professional commercial ad. {ref_instruction} wearing the '{product_info}'. "
            f"The '{product_info}' is the masterpiece, highlighted with studio lighting. "
            f"Background: {backgrounds.get(bg_style)}. {PnP_MasterEngine.TECH_MACRO} "
            f"High-end fashion editorial style, hyper-realistic, sophisticated color grading."
        )
        return prompt

# --- UI Layout ---
st.set_page_config(page_title="Pick & Shot: Professional", layout="wide")
st.title("📸 Pick & Shot: Professional Edition")
st.write("본인의 사진과 상품으로 '돈이 되는' 고퀄리티 화보 프롬프트를 생성하세요.")

# 1. 사이드바: 설정 및 매뉴얼
with st.sidebar:
    st.header("📖 프롬프트 사용 설명서")
    st.markdown("""
    **1단계: 이미지 업로드**
    * 판매할 상품(안경 등)과 모델(본인) 사진을 올리세요.
    
    **2단계: 프롬프트 복사**
    * 생성된 '마스터피스 프롬프트'를 복사합니다.
    
    **3단계: AI 도구 활용**
    * **Midjourney:** `/imagine` 뒤에 사진 링크와 프롬프트를 넣으세요. (`--cref` 활용 권장)
    * **ImageFX:** 프롬프트를 붙여넣고 'Fixed seeds'를 활용해 일관성을 높이세요.
    """)

# 2. 메인 화면: 업로드 영역
col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼 이미지 업로드")
    product_img = st.file_uploader("1. 판매할 상품 이미지 (안경 등)", type=['jpg', 'png', 'jpeg'])
    person_img = st.file_uploader("2. 모델/본인 사진 (일관성 유지용)", type=['jpg', 'png', 'jpeg'])

with col2:
    st.subheader("⚙️ 화보 설정")
    product_desc = st.text_input("상품 이름/특징", "투명 뿔테 안경")
    gender = st.radio("모델 성별", ["female", "male"], horizontal=True)
    bg_style = st.selectbox("배경 스타일", ["Geometric", "Fantasy", "City"])

if st.button("🔥 고퀄리티 마스터피스 프롬프트 생성"):
    if product_desc:
        has_ref = True if person_img else False
        final_prompt = PnP_MasterEngine.generate_consistency_prompt(product_desc, gender, bg_style, has_ref)
        
        st.success("✅ 프롬프트가 완성되었습니다!")
        st.code(final_prompt, language='text')
        
        st.warning("💡 Tip: 이 프롬프트를 사용할 때 업로드한 이미지의 URL을 앞부분에 함께 넣으면 일관성이 비약적으로 상승합니다.")
