import os
from flask import Flask, request, jsonify

app = Flask(__name__)

class HighEndPromptEngine:
    """기획안의 고퀄리티를 보장하는 프롬프트 빌더"""
    
    # 상업 사진의 퀄리티를 결정짓는 필수 기술 스펙
    TECHNICAL_MASTER = (
        "shot on Phase One XF, 80mm lens, f/2.8, professional studio lighting, "
        "high-end fashion editorial style, 8k resolution, ray-tracing, "
        "intricate textures, hyper-realistic skin pores, volumetric lighting"
    )

    @staticmethod
    def build_prompt(user_concept, category="portrait"):
        """사용자 컨셉을 고퀄리티 프롬프트로 변환"""
        # 이미지 2, 3, 4번과 같은 결과물을 내기 위한 카테고리별 템플릿
        templates = {
            "portrait": f"A high-end commercial portrait of {user_concept}. {HighEndPromptEngine.TECHNICAL_MASTER}, softbox rim lighting, sharp focus on eyes, crisp details.",
            "product": f"Macro photography of {user_concept}, {HighEndPromptEngine.TECHNICAL_MASTER}, cinematic depth of field, extreme close-up, sharp textures of materials.",
            "miniature": f"A creative {user_concept} scene, tilt-shift photography, miniature world aesthetic, Octane Render, whimsical atmosphere, vibrant color grading."
        }
        return templates.get(category, templates["portrait"])

@app.route('/generate-task', methods=['POST'])
def generate_task():
    data = request.json
    user_input = data.get('input') # 예: "검정 뿔테 안경을 쓴 20대 여성"
    category = data.get('category', 'portrait')
    
    # 1. 기획안 기반 고퀄리티 프롬프트 생성
    engine = HighEndPromptEngine()
    refined_prompt = engine.build_prompt(user_input, category)
    
    # 2. 결과 반환 (이 프롬프트가 이미지 생성 모델로 전달됨)
    return jsonify({
        "status": "success",
        "original_input": user_input,
        "high_end_prompt": refined_prompt,
        "instruction": "이 프롬프트를 Gemini/Imagen API에 전달하여 고퀄리티 이미지를 생성하세요."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
