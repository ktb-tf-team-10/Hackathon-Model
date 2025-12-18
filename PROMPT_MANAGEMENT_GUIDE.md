# 프롬프트 관리 가이드

## 📌 개요

이 프로젝트는 **프롬프트를 구조화된 리소스**로 관리합니다.

### 왜 이렇게 하나요?

❌ **기존 방식 (코드에 문자열로 박기)**
```python
prompt = f"""
당신은 청첩장 문구 작성 전문가입니다.
톤: {tone}
신랑: {groom_name}
...
"""
```

**문제점**:
- 프롬프트 수정 = 코드 수정 + 배포
- 디자이너/기획자가 수정 불가
- 버전 관리 어려움
- A/B 테스트 불가능
- 코드 가독성 붕괴

✅ **새로운 방식 (md/json 파일 분리)**
```python
from utils.prompt_loader import load_text_generation_prompt

result = load_text_generation_prompt(
    tone="romantic",
    groom_name="홍길동",
    # ...
)
```

**장점**:
- 프롬프트만 수정 (배포 불필요)
- 비개발자도 수정 가능
- Git으로 버전 관리
- A/B 테스트 쉬움
- 모델 교체 비용 거의 0

---

## 📁 디렉토리 구조

```
6.해커톤/3.model/
├── prompts/                          # 📂 프롬프트 리소스 디렉토리
│   ├── invitation/                   # 청첩장 텍스트 생성용
│   │   ├── system.md                 # 시스템 역할 정의
│   │   ├── text_generate.md          # 텍스트 생성 태스크
│   │   └── text_schema.json          # 출력 스키마 (Gemini용)
│   │
│   └── nanobanana/                   # 청첩장 이미지 생성용
│       ├── system.md                 # 시스템 역할 정의
│       ├── page1_cover.md            # 페이지 1 (커버) 프롬프트
│       ├── page2_content.md          # 페이지 2 (인사말) 프롬프트
│       └── page3_location.md         # 페이지 3 (장소) 프롬프트
│
├── utils/
│   └── prompt_loader.py              # 🛠️ 프롬프트 로더 유틸리티
│
├── gemini_text_api.py                # Gemini 텍스트 생성 (프롬프트 로더 사용)
└── nanobanana_api.py                 # 나노바나나 이미지 생성 (프롬프트 로더 사용)
```

---

## 🎯 핵심 개념

### 1. 프롬프트 = 리소스 (데이터)

프롬프트를 **코드가 아닌 데이터**로 취급합니다.

- **코드**: 프롬프트를 조립하는 로직 (`prompt_loader.py`)
- **데이터**: 실제 프롬프트 내용 (`*.md`, `*.json`)

### 2. 템플릿 변수 (Jinja2)

프롬프트 파일에 `{{변수명}}`을 사용하여 동적 값을 주입합니다.

**예시** (`text_generate.md`):
```markdown
# Inputs
- **톤 (tone)**: {{tone}}
- **신랑 이름**: {{groom_name}}
- **신부 이름**: {{bride_name}}
```

**Python 코드**:
```python
prompt = loader.load_prompt(
    "invitation/text_generate.md",
    {
        "tone": "romantic",
        "groom_name": "홍길동",
        "bride_name": "김영희"
    }
)
```

**결과**:
```markdown
# Inputs
- **톤 (tone)**: romantic
- **신랑 이름**: 홍길동
- **신부 이름**: 김영희
```

### 3. 스키마 분리

출력 구조는 JSON 스키마로 정의합니다.

**`text_schema.json`**:
```json
{
  "type": "object",
  "properties": {
    "greetings": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["greetings"]
}
```

이 스키마는:
- Gemini Function Calling
- OpenAI JSON Schema
- Claude Tool Use

모두에서 재사용 가능합니다.

---

## 🛠️ 사용 방법

### 1. 텍스트 생성 (Gemini)

```python
from gemini_text_api import generate_wedding_texts

result = generate_wedding_texts(
    tone="romantic",
    groom_name="홍길동",
    bride_name="김영희",
    groom_father="홍판서",
    groom_mother="김씨",
    bride_father="김판서",
    bride_mother="이씨",
    venue="더 클래식 500",
    wedding_date="2025년 4월 12일 토요일",
    wedding_time="오후 2시 30분",
    address="서울특별시 강남구 테헤란로 123"
)

print(result)
# {
#   "greetings": ["인사말1", "인사말2", "인사말3"],
#   "invitations": ["초대1", "초대2", "초대3"],
#   "location": "장소안내",
#   "closing": ["마무리1", "마무리2", "마무리3"]
# }
```

**내부 동작**:
1. `prompts/invitation/system.md` 로드
2. `prompts/invitation/text_generate.md` 로드 + 변수 치환
3. `prompts/invitation/text_schema.json` 로드
4. Gemini API 호출
5. 구조화된 JSON 응답 반환

### 2. 이미지 생성 (나노바나나)

```python
from utils.prompt_loader import load_nanobanana_prompts

# 페이지 1 (커버)
page1_prompt = load_nanobanana_prompts(
    page=1,
    groom_name="홍길동",
    bride_name="김영희",
    border_design_id="border1"
)

# 페이지 2 (인사말 & 초대)
page2_prompt = load_nanobanana_prompts(
    page=2,
    greeting_text="...",
    invitation_text="...",
    groom_name="홍길동",
    bride_name="김영희",
    groom_father="홍판서",
    groom_mother="김씨",
    bride_father="김판서",
    bride_mother="이씨",
    border_design_id="border1"
)

# 페이지 3 (장소 안내)
page3_prompt = load_nanobanana_prompts(
    page=3,
    wedding_date="2025년 4월 12일 토요일",
    wedding_time="오후 2시 30분",
    venue="더 클래식 500",
    address="서울특별시 강남구 테헤란로 123",
    floor_hall="3층 그랜드홀",
    border_design_id="border1"
)
```

### 3. 직접 PromptLoader 사용

```python
from utils.prompt_loader import PromptLoader

loader = PromptLoader()

# 단일 프롬프트 로드
prompt = loader.load_prompt(
    "invitation/text_generate.md",
    {"tone": "romantic"}
)

# 스키마 로드
schema = loader.load_schema("invitation/text_schema.json")

# 시스템 + 태스크 결합
combined = loader.load_combined(
    "invitation/system.md",
    "invitation/text_generate.md",
    {"tone": "romantic"}
)
```

---

## 📝 프롬프트 파일 작성 가이드

### 1. 시스템 프롬프트 (`system.md`)

**역할 정의**:
```markdown
# Role
당신은 고급 청첩장 문구를 작성하는 전문 작가입니다.

# Core Principles
- 과장되지 않고 품격 있는 문체를 사용합니다
- 결혼의 의미와 감사의 마음을 담아 작성합니다

# Constraints
- 반드시 지정된 JSON 형식으로만 응답합니다
- 이모지, 특수문자를 사용하지 않습니다
```

### 2. 태스크 프롬프트 (`text_generate.md`)

**작업 지시**:
```markdown
# Task
결혼식 청첩장에 들어갈 문구를 작성합니다.

# Inputs
- **톤 (tone)**: {{tone}}
- **신랑 이름**: {{groom_name}}

# Tone Guide

## romantic (로맨틱한)
- 사랑과 감성을 담은 어투
- 따뜻하고 감동적인 표현
- 예: "사랑하는 사람과 영원을 약속하는 날"

# Output Requirements

## 1. greetings (인사말)
- 3가지 버전 제공
- 각 버전은 2-4문장으로 구성
```

### 3. 스키마 파일 (`text_schema.json`)

**출력 구조**:
```json
{
  "type": "object",
  "properties": {
    "greetings": {
      "type": "array",
      "description": "청첩장 인사말 3가지 버전",
      "minItems": 3,
      "maxItems": 3,
      "items": { "type": "string" }
    }
  },
  "required": ["greetings"]
}
```

---

## 🔄 프롬프트 수정 워크플로우

### 시나리오: 인사말 톤을 더 따뜻하게 변경

**기존 방식** (코드 수정):
```bash
1. gemini_text_api.py 파일 열기
2. 수백 줄의 코드에서 프롬프트 문자열 찾기
3. 문자열 수정
4. 코드 테스트
5. Git commit
6. 배포
7. 서버 재시작
```

**새로운 방식** (프롬프트 파일 수정):
```bash
1. prompts/invitation/text_generate.md 파일 열기
2. "romantic" 섹션에서 예시 문구 수정
   - 기존: "사랑하는 사람과 영원을 약속하는 날"
   - 변경: "평생 함께할 단 한 사람과 맺는 소중한 인연"
3. 파일 저장
4. Git commit (선택 사항)
5. 끝! (배포 불필요, 서버 재시작 불필요)
```

---

## 🎨 A/B 테스트 예시

### 1. 프롬프트 버전 관리

```bash
prompts/invitation/
├── text_generate.md          # 버전 A (기본)
└── text_generate_v2.md       # 버전 B (실험)
```

### 2. 코드에서 버전 선택

```python
# A/B 테스트 플래그
use_version_b = user_id % 2 == 0

prompt_file = (
    "invitation/text_generate_v2.md" if use_version_b
    else "invitation/text_generate.md"
)

prompt = loader.load_prompt(prompt_file, variables)
```

### 3. 결과 분석

- 버전 A: 클릭률 5%
- 버전 B: 클릭률 8% ✅

→ 버전 B를 기본으로 채택

---

## 🚀 모델 교체 시나리오

### OpenAI로 전환

```python
# 1. 프롬프트는 그대로 사용
prompt_data = load_text_generation_prompt(**kwargs)

# 2. API 호출만 변경
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_data["prompt"]},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": prompt_data["schema"]  # 동일한 스키마!
    }
)
```

### Claude로 전환

```python
# 1. 프롬프트는 그대로 사용
prompt_data = load_text_generation_prompt(**kwargs)

# 2. API 호출만 변경
response = anthropic.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[
        {"role": "user", "content": prompt_data["prompt"]}
    ],
    tools=[{
        "name": "generate_wedding_texts",
        "input_schema": prompt_data["schema"]  # 동일한 스키마!
    }]
)
```

---

## 📊 프롬프트 품질 관리

### 1. Git으로 버전 관리

```bash
git log prompts/invitation/text_generate.md

# commit abc123
# Author: 기획자A
# Date: 2025-01-15
# "romantic 톤 예시 개선"

# commit def456
# Author: 개발자B
# Date: 2025-01-10
# "closing 문구 3개로 증가"
```

### 2. 프롬프트 테스트

```bash
# 프롬프트 로더 단독 테스트
cd 6.해커톤/3.model
python utils/prompt_loader.py

# Gemini API 통합 테스트
python gemini_text_api.py
```

---

## 🎯 베스트 프랙티스

### ✅ 좋은 프롬프트 구조

```markdown
# Role (명확한 역할)
당신은 X를 하는 전문가입니다.

# Task (구체적인 작업)
Y를 생성합니다.

# Inputs (입력 데이터)
- 톤: {{tone}}

# Tone Guide (톤별 예시)
## romantic
- 특징: ...
- 예시: ...

# Output Requirements (출력 요구사항)
## 1. greetings
- 3가지 버전
- 2-4문장
```

### ❌ 피해야 할 안티패턴

```markdown
# 너무 모호한 지시
당신은 좋은 문구를 작성해주세요.

# 변수명 불명확
이름: {{name}}  # 신랑? 신부?

# 예시 없음
로맨틱한 톤으로 작성  # 예시가 없어 해석이 다를 수 있음
```

---

## 🔧 트러블슈팅

### Q1. `FileNotFoundError: 프롬프트 파일을 찾을 수 없습니다`

**원인**: 파일 경로가 잘못되었거나 파일이 없음

**해결**:
```python
# 절대 경로 확인
import os
print(os.path.abspath("prompts/invitation/text_generate.md"))

# 파일 존재 여부 확인
ls -la 6.해커톤/3.model/prompts/invitation/
```

### Q2. `KeyError: 'tone'`

**원인**: 템플릿 변수를 전달하지 않음

**해결**:
```python
# ❌ 잘못된 사용
loader.load_prompt("invitation/text_generate.md")

# ✅ 올바른 사용
loader.load_prompt(
    "invitation/text_generate.md",
    {"tone": "romantic", ...}  # 모든 변수 전달
)
```

### Q3. Gemini API 스키마 에러

**원인**: JSON Schema → Gemini Schema 변환 실패

**해결**:
```python
# 스키마 검증
import json
schema = loader.load_schema("invitation/text_schema.json")
print(json.dumps(schema, indent=2))

# 필수 필드 확인
assert "type" in schema
assert "properties" in schema
```

---

## 📚 참고 자료

### 프롬프트 엔지니어링

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library)
- [Google Gemini Best Practices](https://ai.google.dev/gemini-api/docs/prompting-strategies)

### 템플릿 엔진

- [Jinja2 Template Designer](https://jinja.palletsprojects.com/en/3.1.x/templates/)

### JSON Schema

- [JSON Schema Specification](https://json-schema.org/)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)

---

## 🎉 요약

1. **프롬프트 = 리소스**: 코드가 아닌 데이터로 관리
2. **템플릿 변수**: Jinja2로 동적 값 주입
3. **스키마 분리**: JSON Schema로 출력 구조 정의
4. **모델 독립**: Gemini, OpenAI, Claude 모두 호환
5. **Git 버전 관리**: 프롬프트 변경 이력 추적
6. **A/B 테스트**: 파일만 교체하면 끝
7. **비개발자 편집**: 기획자, 디자이너도 수정 가능

**핵심 원칙**:
> "프롬프트는 제품의 핵심 자산이다. 코드보다 더 자주 바뀌고, 더 중요할 수 있다."

---

## 📞 문의

- 프롬프트 파일 수정: `prompts/` 디렉토리 참고
- 프롬프트 로더 코드: `utils/prompt_loader.py` 참고
- API 통합: `gemini_text_api.py`, `nanobanana_api.py` 참고
