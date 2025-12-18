# 모델 서버 빠른 시작 가이드

## 🚀 한 줄 명령어로 서버 시작

```bash
cd ~/kakao_bootcamp/1.Wedding_OS_Project/6.해커톤
./START_MODEL_SERVER.sh
```

---

## 📋 수동 실행 (단계별)

### 1. 디렉토리 이동
```bash
cd ~/kakao_bootcamp/1.Wedding_OS_Project/6.해커톤/3.model
```

### 2. 가상환경 활성화
```bash
source .venv/bin/activate
```

### 3. 서버 시작
```bash
# 기본 포트 (8102)
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload

# 다른 포트 사용
uvicorn app.main:app --host 0.0.0.0 --port 8391 --reload
```

---

## 🔧 서버 관리

### 서버 상태 확인
```bash
# 포트 8102 사용 중인 프로세스 확인
lsof -i :8102

# 서버 로그 확인 (백그라운드 실행 시)
tail -f nohup.out
```

### 서버 종료
```bash
# PID로 종료
kill [PID]

# 포트로 종료
lsof -ti:8102 | xargs kill -9
```

### 서버 재시작
```bash
# 기존 서버 종료
lsof -ti:8102 | xargs kill -9

# 새 서버 시작
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload &
```

---

## 🌐 API 테스트

### 1. 브라우저에서 확인
```
http://localhost:8102
http://localhost:8102/docs  (Swagger UI)
http://localhost:8102/health
```

### 2. curl로 테스트
```bash
# Health Check
curl http://localhost:8102/health

# 텍스트 생성 API
curl -X POST http://localhost:8102/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{
    "tone": "romantic",
    "groom_name": "홍길동",
    "bride_name": "김영희",
    "groom_father": "홍판서",
    "groom_mother": "김씨",
    "bride_father": "김판서",
    "bride_mother": "이씨",
    "venue": "더 클래식 500",
    "wedding_date": "2025년 5월 20일 토요일",
    "wedding_time": "오후 2시",
    "address": "서울특별시 강남구 논현동 123-45"
  }'
```

---

## 📁 프로젝트 구조

```
3.model/
├── .venv/              # Python 3.10.18 가상환경
├── app/
│   ├── __init__.py
│   └── main.py         # FastAPI 서버
├── prompts/            # AI 프롬프트 파일들
│   ├── invitation/     # 텍스트 생성
│   └── nanobanana/     # 이미지 생성
├── utils/
│   └── prompt_loader.py
├── gemini_text_api.py  # Gemini API
├── check_setup.py      # 설치 확인
├── .env                # API 키 (비공개)
└── requirements.txt    # 패키지 목록
```

---

## 🔑 환경 변수 설정

### .env 파일 확인
```bash
cat .env

# 필수 항목
GEMINI_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
HF_TOKEN=your_key_here
```

### API 키 설정 확인
```bash
source .venv/bin/activate
python check_setup.py
```

---

## ⚡ 빠른 명령어 모음

```bash
# 서버 시작 (가장 간단)
../START_MODEL_SERVER.sh

# 서버 시작 (수동)
source .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload &

# 서버 종료
lsof -ti:8102 | xargs kill -9

# 서버 상태 확인
lsof -i :8102

# 설치 확인
.venv/bin/python check_setup.py

# 프롬프트 로더 테스트
.venv/bin/python utils/prompt_loader.py

# Gemini API 테스트 (실제 키 필요)
.venv/bin/python gemini_text_api.py
```

---

## 🐛 문제 해결

### 1. "Address already in use"
```bash
# 해결: 기존 프로세스 종료
lsof -ti:8102 | xargs kill -9
```

### 2. "ModuleNotFoundError: No module named 'app'"
```bash
# 해결: app/main.py 파일 확인
ls -la app/main.py

# 없으면 START_MODEL_SERVER.sh 실행 (자동 생성)
../START_MODEL_SERVER.sh
```

### 3. "ImportError: cannot import name 'Schema'"
```bash
# 이미 수정됨 - gemini_text_api.py에서 자동 처리
# 확인: .venv/bin/python -c "import gemini_text_api"
```

### 4. Python 버전 에러
```bash
# 현재 Python 확인
.venv/bin/python --version
# Python 3.10.18 (정상)

# 다른 버전이면 재생성
rm -rf .venv
~/.local/bin/uv venv --python 3.10.18
~/.local/bin/uv pip install -r requirements.txt
```

---

## 📊 포트 매핑

| 서버 | 포트 | URL |
|------|------|-----|
| 프론트엔드 | 5173 | http://localhost:5173 |
| 백엔드 | 8101 | http://localhost:8101 |
| **모델 서버** | **8102** | **http://localhost:8102** |

---

## 🎯 배포 전 체크리스트

- [ ] `.env` 파일에 실제 API 키 입력
- [ ] `check_setup.py` 실행 → 모두 ✅
- [ ] `gemini_text_api.py` 테스트 성공
- [ ] FastAPI 서버 시작 성공
- [ ] `/docs` 접속 확인
- [ ] `/api/generate-text` API 테스트 성공

---

## 📚 추가 문서

- `PROMPT_MANAGEMENT_GUIDE.md` - 프롬프트 관리 가이드
- `RUN_WITH_UV.md` - uv 사용 가이드
- `PROMPT_STRUCTURE_SUMMARY.md` - 프롬프트 구조 요약
- `README.md` - 전체 프로젝트 README
