# 실손의료비 세대별 분석 서비스 배포 가이드

본 서비스는 Flask(Python) 백엔드와 HTML/JS/CSS 프론트엔드로 구성되어 있습니다. 
LLM(Google Gemini, OpenAI, Claude 등)을 통해 상세한 분석 리포트를 생성합니다.

## 1. 사전 요구사항
- Python 3.9 이상
- LLM API 키 (최소 하나 이상 필요)
  - `GOOGLE_API_KEY`: Google AI Studio에서 발급 (권장)
  - `OPENAI_API_KEY`: OpenAI Platform에서 발급
  - `ANTHROPIC_API_KEY`: Anthropic Console에서 발급

## 2. 필수 라이브러리 설치
터미널에서 아래 명령어를 실행하여 필요한 패키지를 설치합니다.
```bash
pip install flask google-generativeai openai anthropic
```

## 3. 환경 변수 설정
API 키를 환경 변수에 등록합니다. (Windows PowerShell 기준)
```powershell
$env:GOOGLE_API_KEY = "your_google_api_key_here"
# 또는
$env:OPENAI_API_KEY = "your_openai_api_key_here"
```

## 4. 서비스 실행
```bash
python app.py
```
서버가 시작되면 브라우저에서 `http://localhost:5000` 접속 시 서비스를 이용할 수 있습니다.

## 5. 주요 파일 설명
- `app.py`: Flask 웹 서버 및 API 엔드포인트
- `llm_service.py`: 세대 판정 로직 및 LLM 프롬프트 관리
- `실손의료비_세대별_데이터.json`: 1~5세대 실손 보험 공식 데이터셋
- `static/`: 웹 프론트엔드 자산 (HTML, CSS, JS)

## 6. 주의사항
- 5세대 실손은 2025년 말 출시 예정 데이터 기반이므로 실제 상품 출시 후 약관을 확인해야 합니다.
- API 키가 없는 경우 미리 작성된 '모의 분석 결과(Mock Data)'가 표시됩니다.
