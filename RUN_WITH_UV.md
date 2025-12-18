# uv로 Python 스크립트 실행하기

## 🎯 방법 1: .venv 사용 (권장)

### 1-1. 가상환경 활성화 후 실행
```bash
# 가상환경 활성화
source .venv/bin/activate

# Python 스크립트 실행
python gemini_text_api.py
python check_setup.py

# 가상환경 비활성화
deactivate
```

### 1-2. 가상환경 활성화 없이 직접 실행
```bash
# .venv의 python 직접 사용
.venv/bin/python gemini_text_api.py
.venv/bin/python check_setup.py
```

---

## 🚀 방법 2: uv run 사용

### 2-1. uv run으로 실행 (가상환경 자동 사용)
```bash
# uv run은 자동으로 .venv 찾아서 실행
~/.local/bin/uv run python gemini_text_api.py
~/.local/bin/uv run python check_setup.py
```

### 2-2. uv run --python 특정 버전 지정
```bash
# Python 3.10 명시
~/.local/bin/uv run --python 3.10 python gemini_text_api.py

# 설치된 정확한 버전 사용
~/.local/bin/uv run --python 3.10.18 python gemini_text_api.py
```

---

## 📦 FastAPI 서버 실행

### uvicorn 설치 확인
```bash
# .venv에 uvicorn 설치되어 있는지 확인
.venv/bin/pip list | grep uvicorn

# 없으면 설치
~/.local/bin/uv pip install uvicorn fastapi
```

### FastAPI 서버 실행 (app/main.py가 있는 경우)
```bash
# 방법 1: .venv 직접 사용
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8391 --reload

# 방법 2: 가상환경 활성화 후
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8391 --reload

# 방법 3: uv run 사용
~/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8391 --reload
```

---

## 🛠️ 현재 프로젝트 구조 확인

```bash
# 현재 디렉토리 구조
6.해커톤/3.model/
├── .venv/              # Python 3.10.18 가상환경
├── prompts/            # 프롬프트 파일들
├── utils/              # 유틸리티
├── gemini_text_api.py  # Gemini API
├── check_setup.py      # 설치 확인
├── requirements.txt    # 패키지 목록
└── .env                # 환경 변수
```

**현재 문제**: `app/main.py` 파일이 없어서 FastAPI 서버 실행 안 됨
```
ModuleNotFoundError: No module named 'app'
```

---

## 🔧 FastAPI 서버 만들기 (필요 시)

### app/main.py 생성
```bash
mkdir -p app
touch app/__init__.py
```

**app/main.py 예시**:
```python
from fastapi import FastAPI
from gemini_text_api import generate_wedding_texts

app = FastAPI(title="Wedding OS - Model API")

@app.get("/")
async def root():
    return {"message": "Wedding OS Model API"}

@app.post("/api/generate-text")
async def generate_text(request: dict):
    result = generate_wedding_texts(
        tone=request["tone"],
        groom_name=request["groom_name"],
        # ... 나머지 파라미터
    )
    return {"success": True, "data": result}
```

### FastAPI 서버 실행
```bash
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8391 --reload
```

---

## 📝 실행 예시

### ✅ 성공 예시
```bash
(3.model) $ .venv/bin/python check_setup.py
============================================================
🔍 Wedding OS - Model Server 설치 확인
============================================================
✅ Python 3.10.18
...
🎉 모든 확인 완료!
```

### ✅ uv run 사용
```bash
$ ~/.local/bin/uv run python check_setup.py
# 또는 alias 설정 후
$ uv run python check_setup.py
```

---

## 💡 Alias 설정 (선택 사항)

### ~/.zshrc 또는 ~/.bashrc에 추가
```bash
# uv 명령어 alias
alias uv='~/.local/bin/uv'
alias uvx='~/.local/bin/uvx'

# 프로젝트 전용 alias
alias model-python='.venv/bin/python'
alias model-pip='~/.local/bin/uv pip'
alias model-run='source .venv/bin/activate'
```

### 적용
```bash
source ~/.zshrc  # 또는 source ~/.bashrc
```

### 사용
```bash
# alias 사용
uv run python gemini_text_api.py
model-python check_setup.py
model-run  # 가상환경 활성화
```

---

## 🎯 권장 사용법

### 개발 중
```bash
# 1. 가상환경 활성화
source .venv/bin/activate

# 2. 스크립트 실행
python gemini_text_api.py
python check_setup.py

# 3. 작업 종료 시 비활성화
deactivate
```

### 일회성 실행
```bash
# 가상환경 활성화 없이 바로 실행
.venv/bin/python gemini_text_api.py
```

### CI/CD 환경
```bash
# uv run 사용 (가상환경 자동 감지)
~/.local/bin/uv run python gemini_text_api.py
```

---

## ❌ 에러 해결

### 1. `ModuleNotFoundError: No module named 'app'`
**원인**: app/main.py 파일 없음
**해결**: FastAPI 서버 파일 생성 또는 다른 스크립트 실행

### 2. `command not found: python`
**원인**: 가상환경 미활성화
**해결**:
```bash
source .venv/bin/activate
# 또는
.venv/bin/python 스크립트명
```

### 3. `Address already in use`
**원인**: 포트가 이미 사용 중
**해결**:
```bash
# 사용 중인 프로세스 확인
lsof -i :8391

# 프로세스 종료
kill -9 [PID]

# 또는 다른 포트 사용
uvicorn app.main:app --port 8392
```

---

## 🔍 현재 설정 확인

```bash
# Python 버전
.venv/bin/python --version
# Python 3.10.18

# 설치된 패키지
.venv/bin/pip list

# uv 위치
which uv  # ~/.local/bin/uv (alias 설정 시)
ls ~/.local/bin/uv  # 실제 파일 확인
```

---

## 📚 정리

| 방법 | 명령어 | 장점 |
|------|--------|------|
| **가상환경 활성화** | `source .venv/bin/activate` | IDE 통합 좋음 |
| **직접 실행** | `.venv/bin/python script.py` | 빠르고 명확 |
| **uv run** | `uv run python script.py` | 자동 환경 감지 |

**권장**: 개발 시 가상환경 활성화, 스크립트 실행 시 직접 실행
