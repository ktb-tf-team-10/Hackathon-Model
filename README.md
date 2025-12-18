# Wedding OS - AI Model Server

결혼식 청첩장 생성을 위한 AI 모델 API 서버 (FastAPI + Gemini + Nanobanana)

## 📋 개요

이 서버는 Wedding OS 프론트엔드와 백엔드 사이에서 AI 모델 호출을 담당합니다.

### 주요 기능

1. **텍스트 생성** (Gemini Flash 2.5)
   - 청첩장 문구 자동 생성 (인사말, 초대문구, 장소안내, 마무리)
   - 6가지 톤 지원: formal, casual, modern, classic, romantic, minimal

2. **이미지 생성** (Nanobanana API)
   - 3페이지 청첩장 이미지 생성
   - 커버, 본문, 위치 페이지 자동 레이아웃
   - S3 자동 업로드 및 URL 반환

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 루트로 이동
cd ~/kakao_bootcamp/1.Wedding_OS_Project/6.해커톤/3.model

# 가상환경 활성화
source .venv/bin/activate

# 패키지 설치 확인
python check_setup.py
```

### 2. 서버 시작

**방법 1: 자동 스크립트 (권장)**
```bash
cd ~/kakao_bootcamp/1.Wedding_OS_Project/6.해커톤
./START_MODEL_SERVER.sh
```

**방법 2: 수동 실행**
```bash
cd ~/kakao_bootcamp/1.Wedding_OS_Project/6.해커톤/3.model
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload
```

### 3. 서버 확인

```bash
# Health Check
curl http://localhost:8102/health

# Swagger UI (브라우저)
open http://localhost:8102/docs
```

## 📁 프로젝트 구조

```
3.model/
├── app/
│   ├── __init__.py
│   └── main.py                    # FastAPI 메인 서버
├── utils/
│   ├── genai_client.py            # Google GenAI 클라이언트 (SSL 수정 포함)
│   └── prompt_loader.py           # 프롬프트 로더 유틸리티
├── prompts/                       # 프롬프트 리소스 파일
│   ├── invitation/                # 텍스트 생성용
│   │   ├── system.md
│   │   ├── text_generate.md
│   │   └── text_schema.json
│   └── nanobanana/                # 이미지 생성용
│       ├── system.md
│       ├── page1_cover.md
│       ├── page2_content.md
│       └── page3_location.md
├── gemini_text_api.py             # Gemini 텍스트 생성 API
├── nanobanana_api.py              # Nanobanana 이미지 생성 API
├── check_setup.py                 # 설치 확인 스크립트
├── requirements.txt               # Python 패키지 목록
├── .env                           # API 키 (비공개)
├── README.md                      # 이 파일
├── QUICK_START.md                 # 빠른 시작 가이드
├── API_TEST_EXAMPLES.md           # API 테스트 예시
├── SSL_FIX_GUIDE.md               # SSL 오류 해결 가이드
└── PROMPT_MANAGEMENT_GUIDE.md     # 프롬프트 관리 가이드
```

## 🔧 기술 스택

| 항목 | 기술 | 버전 |
|------|------|------|
| Python | CPython | 3.10.18+ |
| 패키지 관리자 | uv | latest |
| 웹 프레임워크 | FastAPI | 0.115.0 |
| ASGI 서버 | Uvicorn | 0.32.0 |
| AI SDK | google-genai | 1.53.0 |
| 템플릿 엔진 | Jinja2 | 3.1.2 |
| HTTP 클라이언트 | requests | 2.31.0 |
| 클라우드 스토리지 | boto3 (AWS S3) | 1.34.69 |
| 이미지 처리 | Pillow | 10.3.0 |
| SSL 인증서 | certifi | 2023.7.22+ |

## 📡 API 엔드포인트

### 1. Health Check

```http
GET /health
```

**응답**
```json
{
  "status": "ok"
}
```

### 2. 텍스트 생성 API

```http
POST /api/generate-text
Content-Type: application/json
```

**요청 본문**
```json
{
  "tone": "romantic",
  "groom_name": "홍길동",
  "bride_name": "김영희",
  "groom_father": "홍판서",
  "groom_mother": "김씨",
  "bride_father": "김판서",
  "bride_mother": "이씨",
  "venue": "더 클래식 500",
  "wedding_date": "2025년 5월 20일 토요일",
  "wedding_time": "오후 2시 30분",
  "address": "서울특별시 강남구 테헤란로 123"
}
```

**응답**
```json
{
  "success": true,
  "data": {
    "greetings": ["인사말1", "인사말2", "인사말3"],
    "invitations": ["초대1", "초대2", "초대3"],
    "location": "장소안내",
    "closing": ["마무리1", "마무리2", "마무리3"]
  }
}
```

### 3. 청첩장 이미지 생성 API

```http
POST /api/generate-invitation
Content-Type: multipart/form-data
```

**요청 (Multipart Form)**
```
wedding_image: [파일]
style_image: [파일]
tone: "romantic"
groom_name: "홍길동"
bride_name: "김영희"
groom_father: "홍판서"
groom_mother: "김씨"
bride_father: "김판서"
bride_mother: "이씨"
venue: "더 클래식 500"
wedding_date: "2025년 5월 20일 토요일"
wedding_time: "오후 2시 30분"
address: "서울특별시 강남구 테헤란로 123"
border_design_id: "border1"
latitude: 37.5665 (Optional)
longitude: 126.9780 (Optional)
floor_hall: "3층 그랜드홀" (Optional)
```

**응답**
```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "page_number": 1,
        "image_url": "https://s3.amazonaws.com/bucket/page1.png",
        "type": "cover"
      },
      {
        "page_number": 2,
        "image_url": "https://s3.amazonaws.com/bucket/page2.png",
        "type": "content"
      },
      {
        "page_number": 3,
        "image_url": "https://s3.amazonaws.com/bucket/page3.png",
        "type": "location"
      }
    ],
    "texts": {
      "greeting": "생성된 인사말",
      "invitation": "생성된 초대 문구",
      "location": "생성된 장소 안내"
    }
  }
}
```

## 🔑 환경 변수

`.env` 파일에 다음 API 키를 설정하세요:

```bash
# Gemini API (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# Nanobanana API (필수)
HUGGINGFACE_API_KEY=your_huggingface_key
HF_TOKEN=your_huggingface_token

# AWS S3 (선택)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=wedding-invitation-images
```

## 🐛 트러블슈팅

### SSL 인증서 오류

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**해결 방법**: `SSL_FIX_GUIDE.md` 참고

### ModuleNotFoundError

```bash
# 패키지 재설치
~/.local/bin/uv pip install -r requirements.txt

# 확인
python check_setup.py
```

### 포트 이미 사용 중

```bash
# 기존 프로세스 종료
lsof -ti:8102 | xargs kill -9

# 서버 재시작
./START_MODEL_SERVER.sh
```

## 📚 문서

- **QUICK_START.md**: 빠른 시작 가이드
- **API_TEST_EXAMPLES.md**: API 테스트 예시 (curl, Python, JavaScript)
- **SSL_FIX_GUIDE.md**: SSL 인증서 오류 해결
- **PROMPT_MANAGEMENT_GUIDE.md**: 프롬프트 관리 가이드 (16장)

## 🚢 배포 가이드

### 로컬 개발 환경

```bash
# 서버 시작
uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload

# 로그 확인
tail -f nohup.out
```

### 프로덕션 환경

```bash
# 백그라운드 실행
nohup uvicorn app.main:app --host 0.0.0.0 --port 8102 &

# 프로세스 확인
ps aux | grep uvicorn

# 서버 종료
kill [PID]
```

### Docker (선택)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8102"]
```

## 🧪 테스트

### 설치 확인

```bash
.venv/bin/python check_setup.py
```

### 텍스트 생성 테스트

```bash
.venv/bin/python gemini_text_api.py
```

### API 테스트

```bash
# Health Check
curl http://localhost:8102/health

# 텍스트 생성
curl -X POST http://localhost:8102/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{"tone":"romantic","groom_name":"홍길동",...}'
```

## 🔐 보안 주의사항

1. **API 키 관리**
   - `.env` 파일을 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.env` 추가 확인

2. **CORS 설정**
   - 프로덕션에서는 특정 도메인만 허용
   - `app/main.py`의 `allow_origins` 수정

3. **SSL 인증서**
   - 개발 환경: certifi 사용 (현재 설정)
   - 프로덕션 환경: 엄격한 SSL 검증 활성화

## 📊 성능

| 작업 | 평균 응답 시간 | 비고 |
|------|---------------|------|
| Health Check | < 10ms | 즉시 응답 |
| 텍스트 생성 | 3-5초 | Gemini API 호출 |
| 이미지 생성 | 30-60초 | Nanobanana + S3 업로드 |

## 🆘 지원

문제가 발생하면 다음을 확인하세요:

1. `check_setup.py` 실행 결과
2. `.env` 파일의 API 키 확인
3. `SSL_FIX_GUIDE.md` 참고
4. 서버 로그 확인 (`tail -f nohup.out`)

## 📄 라이선스

이 프로젝트는 해커톤 프로젝트입니다.

## 👥 개발자

- Wedding OS Team
- 2025 카카오 부트캠프 해커톤

## 🔄 변경 이력

### 2025-12-18
- ✅ SSL 인증서 오류 해결 (certifi 적용)
- ✅ google-genai SDK로 마이그레이션 (v1.53.0)
- ✅ FastAPI 서버 프로덕션 구성
- ✅ 프롬프트 파일 기반 관리 시스템
- ✅ Nanobanana 이미지 생성 API 추가
- ✅ 종합 문서화 완료

### 이전 버전
- google-generativeai 사용 (deprecated)
- 하드코딩된 프롬프트
- 2단계 API 호출 (Gemini x2)
# Hackathon-Model
