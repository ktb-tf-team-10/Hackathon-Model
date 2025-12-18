# SSL 인증서 오류 해결 가이드

## 문제 상황

macOS 환경에서 `google-genai` SDK 사용 시 SSL 인증서 검증 오류가 발생했습니다.

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

## 원인

- macOS Python 환경에서 SSL 인증서 경로가 올바르게 설정되지 않음
- `certifi` 패키지의 CA 번들을 사용하지 않고 시스템 인증서를 찾으려다 실패

## 해결 방법

### 1. certifi 패키지 설치

```bash
~/.local/bin/uv pip install certifi
```

### 2. genai_client.py 수정

`utils/genai_client.py` 파일의 `_build_client()` 함수에 SSL 설정 추가:

```python
import certifi
import os

@lru_cache(maxsize=1)
def _build_client(api_key: str) -> genai.Client:
    """
    Google GenAI 클라이언트를 생성합니다.

    SSL 인증서 검증 우회 설정 포함 (개발 환경용)
    """
    # SSL 인증서 검증 비활성화 (macOS SSL 인증서 문제 해결)
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

    # HTTP 클라이언트 설정
    http_options = {
        "api_version": "v1alpha",
    }

    return genai.Client(
        api_key=api_key,
        http_options=http_options
    )
```

### 3. requirements.txt 업데이트

```txt
# Google AI APIs
google-genai==1.53.0
google-cloud-aiplatform==1.60.0
certifi>=2023.7.22  # ← SSL 인증서 관리
```

## 검증 방법

### 1. 패키지 설치 확인

```bash
.venv/bin/python check_setup.py
```

출력 예시:
```
📦 패키지 확인:
   ✅ Gemini API
   ✅ Google Cloud AI Platform
   ✅ SSL 인증서
```

### 2. Gemini API 테스트

```bash
.venv/bin/python gemini_text_api.py
```

정상 출력:
```json
{
  "greetings": ["...", "...", "..."],
  "invitations": ["...", "...", "..."],
  "location": "...",
  "closing": ["...", "...", "..."]
}
```

### 3. FastAPI 서버 테스트

```bash
# 서버 시작
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8102 --reload

# API 호출 테스트
curl -X POST http://localhost:8102/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{
    "tone": "romantic",
    "groom_name": "홍길동",
    "bride_name": "김영희",
    ...
  }'
```

## 코드 변경 사항 요약

| 파일 | 변경 내용 |
|------|----------|
| `utils/genai_client.py` | SSL 인증서 경로 설정 추가 |
| `requirements.txt` | `certifi>=2023.7.22` 추가 |
| `check_setup.py` | `certifi` 패키지 확인 추가 |

## 프로덕션 환경 주의사항

현재 구현은 **개발 환경**을 위한 임시 해결책입니다.

### 프로덕션 환경 권장 사항:

1. **올바른 SSL 인증서 설정**
   - 서버에 최신 CA 인증서 설치
   - 시스템 인증서 저장소 업데이트

2. **환경별 설정 분리**
   ```python
   if os.getenv("ENVIRONMENT") == "production":
       # 프로덕션: 엄격한 SSL 검증
       client = genai.Client(api_key=api_key)
   else:
       # 개발: certifi 사용
       os.environ['SSL_CERT_FILE'] = certifi.where()
       client = genai.Client(api_key=api_key)
   ```

3. **보안 검토**
   - SSL 인증서 검증 우회는 중간자 공격(MITM) 위험
   - 프로덕션에서는 반드시 엄격한 SSL 검증 활성화

## 참고 자료

- [certifi 공식 문서](https://github.com/certifi/python-certifi)
- [Google GenAI SDK](https://github.com/googleapis/python-genai)
- [Python SSL 문서](https://docs.python.org/3/library/ssl.html)

## 트러블슈팅

### 여전히 SSL 오류 발생 시

1. certifi 재설치
   ```bash
   ~/.local/bin/uv pip uninstall certifi
   ~/.local/bin/uv pip install certifi
   ```

2. Python 환경 변수 확인
   ```bash
   .venv/bin/python -c "import certifi; print(certifi.where())"
   ```

3. 시스템 시간 확인
   ```bash
   date
   # 시스템 시간이 정확하지 않으면 SSL 인증서 검증 실패
   ```

### macOS 전용 해결책

macOS에서 Python SSL 인증서 설치:
```bash
/Applications/Python\ 3.10/Install\ Certificates.command
```

## 변경 이력

- **2025-12-18**: 초기 SSL 오류 해결 (certifi 적용)
- **2025-12-18**: genai_client.py 리팩토링 완료
- **2025-12-18**: 프로덕션 주의사항 문서화
