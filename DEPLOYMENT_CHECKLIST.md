# 배포 체크리스트

백엔드 개발자가 이 모델 서버를 배포하기 전 확인해야 할 사항입니다.

## ✅ 사전 준비 (로컬 환경)

### 1. Python 환경

- [ ] Python 3.10.18 이상 설치됨
- [ ] `uv` 패키지 관리자 설치됨 (`~/.local/bin/uv`)
- [ ] `.venv` 가상환경 생성 완료
- [ ] 모든 패키지 설치 완료 (`uv pip install -r requirements.txt`)

**확인 명령어**
```bash
.venv/bin/python --version
.venv/bin/python check_setup.py
```

### 2. 환경 변수

- [ ] `.env` 파일 존재
- [ ] `GEMINI_API_KEY` 설정됨 (실제 키)
- [ ] `HUGGINGFACE_API_KEY` 설정됨
- [ ] `HF_TOKEN` 설정됨
- [ ] AWS S3 키 설정됨 (선택사항)

**확인 명령어**
```bash
cat .env | grep -E "(GEMINI|HUGGINGFACE|HF_TOKEN)"
```

### 3. 프롬프트 파일

- [ ] `prompts/invitation/` 디렉토리 존재
- [ ] `prompts/nanobanana/` 디렉토리 존재
- [ ] 모든 `.md` 및 `.json` 파일 존재

**확인 명령어**
```bash
ls -la prompts/invitation/
ls -la prompts/nanobanana/
```

### 4. API 테스트

- [ ] `gemini_text_api.py` 단독 실행 성공
- [ ] FastAPI 서버 시작 성공
- [ ] `/health` 엔드포인트 200 OK
- [ ] `/api/generate-text` 정상 응답

**확인 명령어**
```bash
.venv/bin/python gemini_text_api.py
curl http://localhost:8102/health
curl -X POST http://localhost:8102/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{"tone":"romantic","groom_name":"테스트",...}'
```

## 🚀 배포 전 최종 확인

### 1. 보안

- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] API 키가 Git에 커밋되지 않음
- [ ] CORS 설정 확인 (`allow_origins` 특정 도메인으로 제한)
- [ ] SSL 인증서 설정 확인 (프로덕션 환경)

**app/main.py CORS 설정 수정 예시**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # ← 수정 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 성능

- [ ] 응답 시간 측정 완료
  - Health Check: < 10ms
  - 텍스트 생성: 3-5초
  - 이미지 생성: 30-60초
- [ ] 동시 요청 처리 테스트 완료
- [ ] 메모리 사용량 확인

### 3. 에러 처리

- [ ] SSL 인증서 오류 해결됨 (`SSL_FIX_GUIDE.md` 참고)
- [ ] 모든 API 엔드포인트에 try/except 있음
- [ ] 에러 로그 설정 완료
- [ ] 실패 시 적절한 HTTP 상태 코드 반환

### 4. 문서화

- [ ] `README.md` 최신 상태
- [ ] `API_TEST_EXAMPLES.md` 정확함
- [ ] `SSL_FIX_GUIDE.md` 이해함
- [ ] 배포 환경별 설정 문서화

## 🌐 프로덕션 배포

### 1. 서버 환경

- [ ] Python 3.10+ 설치됨
- [ ] uv 또는 pip 설치됨
- [ ] 방화벽에서 포트 8102 열림 (또는 사용할 포트)
- [ ] SSL 인증서 설치됨 (HTTPS 사용 시)

### 2. 환경 변수 설정

**프로덕션 .env 파일**
```bash
# 프로덕션 API 키로 교체
GEMINI_API_KEY=prod_key_here
HUGGINGFACE_API_KEY=prod_key_here
HF_TOKEN=prod_token_here

# AWS S3 설정 (필수)
AWS_ACCESS_KEY_ID=prod_aws_key
AWS_SECRET_ACCESS_KEY=prod_aws_secret
S3_BUCKET_NAME=wedding-os-production

# 환경 표시
ENVIRONMENT=production
```

### 3. 서버 실행

**방법 1: systemd (권장)**
```bash
# /etc/systemd/system/wedding-model.service
[Unit]
Description=Wedding OS Model API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/3.model
ExecStart=/path/to/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8102
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start wedding-model
sudo systemctl enable wedding-model
```

**방법 2: Docker**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 패키지 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 앱 복사
COPY . .

# 포트 노출
EXPOSE 8102

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8102"]
```

```bash
docker build -t wedding-model-api .
docker run -d -p 8102:8102 --env-file .env wedding-model-api
```

**방법 3: Gunicorn + Uvicorn (고성능)**
```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8102
```

### 4. 모니터링

- [ ] 로그 파일 위치 설정
- [ ] 에러 알림 설정
- [ ] 성능 모니터링 도구 설정 (예: Prometheus, Grafana)
- [ ] Health Check 엔드포인트 모니터링

**로그 설정 예시**
```python
# app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/wedding-model.log'),
        logging.StreamHandler()
    ]
)
```

### 5. 백업 및 복구

- [ ] `.env` 파일 백업
- [ ] `prompts/` 디렉토리 백업
- [ ] 데이터베이스 백업 (해당되는 경우)
- [ ] 복구 절차 문서화

## 🧪 배포 후 테스트

### 1. 기본 기능

```bash
# Health Check
curl https://your-domain.com/health

# 텍스트 생성
curl -X POST https://your-domain.com/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{"tone":"romantic",...}'

# 이미지 생성 (파일 업로드)
curl -X POST https://your-domain.com/api/generate-invitation \
  -F "wedding_image=@test.jpg" \
  -F "style_image=@style.jpg" \
  -F "tone=romantic" \
  ...
```

### 2. 부하 테스트

```bash
# Apache Bench
ab -n 100 -c 10 https://your-domain.com/health

# 또는 wrk
wrk -t12 -c400 -d30s https://your-domain.com/health
```

### 3. 에러 시나리오

- [ ] 잘못된 API 키 → 401 Unauthorized
- [ ] 잘못된 요청 본문 → 422 Unprocessable Entity
- [ ] 누락된 필드 → 422 Unprocessable Entity
- [ ] 서버 과부하 → 503 Service Unavailable

## 📊 모니터링 체크리스트

### 1. 시스템 리소스

- [ ] CPU 사용률 < 80%
- [ ] 메모리 사용률 < 80%
- [ ] 디스크 공간 충분
- [ ] 네트워크 대역폭 확인

### 2. 애플리케이션

- [ ] API 응답 시간 모니터링
- [ ] 에러 발생률 < 1%
- [ ] 요청 처리량 확인
- [ ] 동시 연결 수 확인

### 3. 로그

- [ ] 에러 로그 정기 확인
- [ ] 경고 로그 검토
- [ ] API 호출 통계 수집

## 🚨 트러블슈팅

### 일반적인 문제

1. **SSL 인증서 오류**
   - 해결: `SSL_FIX_GUIDE.md` 참고
   - certifi 패키지 설치 확인

2. **포트 충돌**
   ```bash
   lsof -ti:8102 | xargs kill -9
   ```

3. **메모리 부족**
   - Gunicorn worker 수 조정
   - 캐싱 전략 검토

4. **응답 시간 지연**
   - Gemini API 할당량 확인
   - 네트워크 레이턴시 측정
   - 로드 밸런싱 고려

### 긴급 복구

```bash
# 서버 재시작
sudo systemctl restart wedding-model

# 로그 확인
sudo journalctl -u wedding-model -f

# 디버그 모드
ENVIRONMENT=debug uvicorn app.main:app --reload
```

## 📞 지원

문제 발생 시:

1. `check_setup.py` 실행
2. 로그 파일 확인
3. `SSL_FIX_GUIDE.md` 참고
4. GitHub Issues 등록

## ✅ 최종 확인

배포 전 이 항목들을 모두 확인하세요:

- [ ] 모든 환경 변수 설정됨
- [ ] SSL 인증서 정상 작동
- [ ] API 테스트 모두 통과
- [ ] 보안 설정 완료
- [ ] 모니터링 설정 완료
- [ ] 백업 절차 수립
- [ ] 문서화 완료
- [ ] 팀원에게 배포 알림

---

**배포 완료 시 체크**

- [ ] 프로덕션 URL 접속 확인
- [ ] Health Check 200 OK
- [ ] API 테스트 성공
- [ ] 모니터링 대시보드 확인
- [ ] 로그 정상 수집
- [ ] 백업 자동화 확인

🎉 배포 완료!
