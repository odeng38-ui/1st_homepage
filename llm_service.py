import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load data once
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), '실손의료비_세대별_데이터.json')
try:
    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
        INSURANCE_DATA = json.load(f)
except Exception as e:
    logger.error(f"Failed to load 실손의료비_세대별_데이터.json: {e}")
    # Fallback to local search if not found
    INSURANCE_DATA = {"generations": [], "switch_guide": {}}

def get_generation_from_join_date(join_date_str):
    """
    가입일(YYYY-MM-DD 형식) → 세대 판정
    """
    try:
        join_date = datetime.strptime(join_date_str, '%Y-%m-%d')
    except ValueError:
        return None, "유효하지 않은 날짜 형식입니다. (YYYY-MM-DD)"
    
    # 세대별 가입 기간 확인
    for gen in INSURANCE_DATA.get('generations', []):
        try:
            start = datetime.strptime(gen['join_period']['start_date'], '%Y-%m-%d')
            end = datetime.strptime(gen['join_period']['end_date'], '%Y-%m-%d')
            
            if start <= join_date <= end:
                return gen['generation'], gen['name']
        except Exception:
            continue
    
    return None, "해당 날짜에 맞는 실손 보험 세대를 찾을 수 없습니다."

def create_user_prompt(generation_data):
    """
    세대별 JSON 데이터를 기반으로 사용자 프롬프트 생성
    """
    try:
        # 5세대 데이터 (마지막 세대)
        fifth_gen = next((g for g in INSURANCE_DATA['generations'] if g['generation'] == 5), {})
        
        # Determine switch guide key
        suffix = "th"
        if generation_data["generation"] == 1: suffix = "st"
        elif generation_data["generation"] == 2: suffix = "nd"
        elif generation_data["generation"] == 3: suffix = "rd"
        
        switch_guide_key = f'from_{generation_data["generation"]}{suffix}_to_5th'
        switch_guide = INSURANCE_DATA['switch_guide'].get(switch_guide_key, {})

        prompt = f"""
## 입력 데이터 (보험 통계 및 가이드)

### [현재 가입 모델: {generation_data['generation']}세대 - {generation_data['name']}]
- 가입기간: {generation_data['join_period']['description']}
- 보장구조: {generation_data['coverage_structure']['type']}
- 세부 데이터: {json.dumps(generation_data, ensure_ascii=False)}

### [비교 대상 모델: 5세대 실손 (중증 중심형)]
- 세부 데이터: {json.dumps(fifth_gen, ensure_ascii=False)}

### [전문가 전환 가이드라인]
- 핵심 비교 요소: {json.dumps(switch_guide, ensure_ascii=False)}

## 요청사항
위 데이터를 바탕으로 고객에게 보내는 '실손보험 진단 보고서' 형태로 설명을 작성해주세요.
각 항목별로 구체적인 수치(자기부담금 %, 한도 금액 등)를 반드시 포함하여 신뢰도를 높여주세요.
"""
        return prompt
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        return "프롬프트 생성 중 오류가 발생했습니다."

SYSTEM_PROMPT = """
당신은 대한민국 최고의 '보험 분석 전문 AI 에이전트'입니다.
보험 설계사가 고객에게 브리핑하는 것처럼 전문적이고, 친절하며, 신뢰감 있는 톤을 유지하세요.

# 핵심 미션
1. 사용자의 현재 실손보험 세대를 정확히 인지하고 그 특징을 설명한다.
2. 현재 세대의 구체적인 보장/비보장 내용을 전달한다.
3. 5세대(전환 실손)로 갈아탔을 때의 실질적인 이득과 손해를 '숫자' 기반으로 분석한다.

# 출력 구조 (Markdown 형식 사용)

## 📊 현재 실손보험 진단 결과
- 가입하신 보험은 **{세대이름}**입니다. ({가입기간})
- 핵심 요약: {세대별 한 줄 특징}

## 🔍 상세 보장 정보
### ✅ 든든하게 보장받는 항목
- (데이터에서 보장되는 항목 4~5개를 수치와 함께 나열)
### ⚠️ 주의가 필요한 미보장 항목
- (데이터에서 제외되거나 제한적인 항목 3~4개 설명)

## 🔄 5세대 실손으로 전환한다면?
> **AI 분석 한마디**: {전환 권유 여부 및 핵심 이유}

### 💡 전환 시 얻게 되는 이로운 점 (Pros)
1. **보험료 절감**: {데이터 기반 수치}
2. (다른 장점 2가지 나열)

### 📉 전환 시 감수해야 할 부분 (Cons)
1. **자기부담금 증가**: {데이터 기반 수치}
2. (다른 단점 2가지 나열)

## 📋 전문가 제언
- (고객의 성향에 따른 유지/전환 가이드라인 제공)
- (주의사항: 실제 결정 전 약관 확인 및 담당 설계사 상담 필요 명시)

# 제약 사항
- 제공된 JSON 데이터에 없는 수치를 지어내지 마세요.
- 전문 용어는 쉽게 풀어서 설명하되, 보험 업계의 전문성을 유지하세요.
- 각 섹션은 이모지를 적절히 섞어 시각적으로 깔끔하게 구성하세요.
"""

def generate_explanation(join_date_str):
    # Step 1: 세대 판정
    gen_num, gen_name = get_generation_from_join_date(join_date_str)
    if not gen_num:
        return {"error": gen_name}
    
    # Step 2: 해당 세대 데이터 찾기
    gen_data = next((g for g in INSURANCE_DATA['generations'] if g['generation'] == gen_num), None)
    if not gen_data:
        return {"error": "해당 세대의 기초 데이터를 찾을 수 없습니다."}
    
    # Step 3: 프롬프트 생성
    user_prompt = create_user_prompt(gen_data)
    
    # Step 4: LLM 호출
    google_key = os.environ.get("GOOGLE_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    explanation = ""

    # Priority 1: Google Gemini (Recommended)
    if google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(user_prompt)
            explanation = response.text
        except Exception as e:
            logger.error(f"Google Gemini Error: {e}")
            # fall back to others if configured

    # Priority 2: OpenAI
    if not explanation and openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            explanation = response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")

    # Priority 3: Anthropic
    if not explanation and anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": user_prompt}],
                system=SYSTEM_PROMPT
            )
            explanation = response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API Error: {e}")

    # Mock Response
    if not explanation:
        logger.warning("No API key provided or all calls failed. Using mock response.")
        explanation = f"""
## 📊 현재 실손보험 진단 결과
- 가입하신 보험은 **{gen_data['name']}**입니다.
- 핵심 요약: {gen_data['special_features'][0]}

## 🔍 상세 보장 정보
### ✅ 든든하게 보장받는 항목
- **급여 의료비**: {gen_data['guarantees'].get('급여_의료비', {}).get('coverage', '보장')}
- **특징**: {gen_data['special_features'][1]}

### ⚠️ 주의가 필요한 미보장 항목
- {gen_data['exclusions']['주요_비보장_항목'][0]}
- {gen_data['exclusions']['주요_비보장_항목'][1]}

## 🔄 5세대 실손으로 전환한다면? (예상 분석)
> **AI 분석 한마디**: 보험료 부담이 크다면 5세대가 대안이 될 수 있으나 보장 축소를 고려해야 합니다.

### 💡 전환 시 얻게 되는 이로운 점 (Pros)
1. **보험료 절감**: {gen_data['premium'].get('level')} 수준에서 가장 저렴한 수준으로 낮아짐
2. {gen_data['pros'][0]}

### 📉 전환 시 감수해야 할 부분 (Cons)
1. **자기부담금 증가**: 기존보다 높은 자기부담률 적용 예상
2. {gen_data['cons'][0]}

## 📋 전문가 제언
- (API 키 미설정으로 인한 기초 데이터 기반 분석입니다.)
- 실제 보장 내용은 보험사마다 다를 수 있으니 가입하신 약관을 확인해 주세요.
"""

    return {
        "generation": gen_num,
        "generation_name": gen_name,
        "explanation": explanation
    }
