import google.generativeai as genai
import os

# 1. API 키 설정
# 실제 환경에서는 환경 변수 사용을 권장하지만, 테스트를 위해 직접 입력 방식 예시를 둡니다.
# 'YOUR_API_KEY' 부분에 개발자님의 정확한 API 키를 넣어주세요.
MY_API_KEY = "YOUR_API_KEY_HERE"

try:
    # 라이브러리 설정
    genai.configure(api_key=MY_API_KEY)

    # 2. 모델 설정 (핵심 수정 부분)
    # 기존 'gemini-pro' 대신 구체적인 최신 버전명을 사용합니다.
    # gemini-1.5-flash: 속도가 빠르고 최신 정보 처리에 강함 (추천)
    # gemini-1.0-pro: 기존 pro 버전의 안정화 버전
    model = genai.GenerativeModel('gemini-1.5-flash')

    print(">>> 모델 초기화 완료. 테스트 요청을 보냅니다...")

    # 3. 콘텐츠 생성 요청 (테스트)
    response = model.generate_content("안녕, 넌 누구니? 짧게 소개해줘.")

    # 4. 결과 출력
    print("\n[응답 결과]:")
    print(response.text)

except Exception as e:
    print(f"\n[오류 발생]: {e}")
    print("-" * 30)
    print("팁: 404 에러가 사라졌다면 모델명 변경이 성공한 것입니다.")
    print("팁: 403 에러가 뜬다면 API 키 권한이나 할당량 문제입니다.")
