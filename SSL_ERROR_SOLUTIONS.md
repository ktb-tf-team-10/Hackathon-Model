# SSL 오류 해결 방법 모음

Nanobanana API 또는 다른 HTTPS 연결 시 발생하는 SSL/TLS 오류에 대한 종합 해결 가이드입니다.

## 🔴 발생하는 주요 오류들

### 1. SSLCertVerificationError
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

### 2. TLSv1 Unrecognized Name (SNI Issue)
```
HTTPSConnectionPool(host='api.nanobanana.com', port=443): Max retries exceeded with url: /v1/generate
(Caused by SSLError(SSLError(1, '[SSL: TLSV1_UNRECOGNIZED_NAME] tlsv1 unrecognized name (_ssl.c:1017)')))
```

**분석 결과:** 
- `api.nanobanana.com` 서버가 특정 클라이언트의 SNI(Server Name Indication)를 인식하지 못해 발생하는 서버 측 오류입니다.
- `curl`이나 `urllib`에서도 동일하게 발생하며, 이는 클라이언트 환경(uv, conda 등)보다는 서버 설정의 문제입니다.

**해결 방법:**
- `nanobanana_api.py`에 HTTP 폴백 로직을 추가했습니다. HTTPS 연결 실패 시 자동으로 HTTP로 전환하여 재시도합니다.
- Gemini API (`generativelanguage.googleapis.com`)는 정상적으로 HTTPS 연결이 가능하므로 안심하고 사용하셔도 됩니다.

### 3. Max Retries Exceeded
```
Max retries exceeded with url: ... (Caused by SSLError(...))
```

---

## ✅ 해결 방법 (우선순위 순)

### 방법 1: certifi 사용 (✅ 이미 적용됨)

**현재 코드에 이미 적용된 방법입니다.**

```python
import certifi
import os

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
```

**파일 위치:**
- `utils/genai_client.py`
- `utils/ssl_fix.py`
- `nanobanana_api.py`

**확인 방법:**
```bash
cd 6.해커톤/3.model
.venv/bin/python utils/ssl_fix.py
```

---

### 방법 2: OpenSSL 재설치 (macOS/Linux)

#### macOS (Homebrew)
```bash
# OpenSSL 설치
brew install openssl

# Python에 OpenSSL 경로 추가
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install libssl-dev openssl
```

---

### 방법 3: Conda SSL 설정 (Anaconda 사용 시)

#### conda config 설정
```bash
# SSL 검증 비활성화 (임시, 권장하지 않음)
conda config --set ssl_verify false

# 또는 특정 채널만
conda config --set ssl_verify channels
```

#### Anaconda Library 경로 추가 (Windows)
```
시스템 환경변수 Path에 다음 추가:
C:\Users\[사용자명]\Anaconda3\Library\bin
```

---

### 방법 4: Python 버전 변경

일부 Python 버전 (3.13 등)에서 SSL 관련 호환성 문제가 있을 수 있습니다.

**권장 버전: Python 3.10.x**

```bash
# 현재 버전 확인
python --version

# uv로 특정 버전 설치
~/.local/bin/uv venv --python 3.10.18
```

---

### 방법 5: requests 라이브러리 설정

#### verify=False 사용 (개발 환경만!)
```python
import requests

# ⚠️  프로덕션에서 사용 금지!
response = requests.get(url, verify=False)
```

#### certifi CA 번들 명시
```python
import requests
import certifi

response = requests.get(url, verify=certifi.where())
```

#### Session 사용 (권장)
```python
import requests
import certifi

session = requests.Session()
session.verify = certifi.where()
response = session.get(url)
```

---

### 방법 6: 환경 변수 설정

#### Bash/Zsh (.bashrc, .zshrc)
```bash
export SSL_CERT_FILE=/path/to/certifi/cacert.pem
export REQUESTS_CA_BUNDLE=/path/to/certifi/cacert.pem
export CURL_CA_BUNDLE=/path/to/certifi/cacert.pem
```

#### Python 코드
```python
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
```

---

### 방법 7: Python SSL 컨텍스트 커스터마이징

```python
import ssl
import certifi

# 커스텀 SSL 컨텍스트 생성
context = ssl.create_default_context()
context.load_verify_locations(certifi.where())

# urllib 사용 시
import urllib.request
response = urllib.request.urlopen(url, context=context)

# requests는 자동으로 시스템 설정 사용
```

---

### 방법 8: TLS 버전 강제 지정

```python
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', TLSAdapter())
response = session.get(url)
```

---

### 방법 9: urllib3 경고 억제

```python
import urllib3

# InsecureRequestWarning 경고 억제
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

## 🧪 테스트 방법

### 1. SSL 설정 확인
```bash
cd 6.해커톤/3.model
.venv/bin/python utils/ssl_fix.py
```

**출력 예시:**
```
✅ SSL 전역 설정 완료
   - CA Bundle: /path/to/certifi/cacert.pem

🧪 SSL 연결 테스트:
✅ certifi 사용 성공 (상태 코드: 200)
```

### 2. Python에서 직접 테스트
```bash
.venv/bin/python -c "
import requests
import certifi
print('certifi path:', certifi.where())
response = requests.get('https://www.google.com', verify=certifi.where())
print('Status:', response.status_code)
"
```

### 3. 특정 API 테스트
```bash
.venv/bin/python -c "
import requests
import certifi
url = 'https://api.nanobanana.com/v1/health'  # 예시
response = requests.get(url, verify=certifi.where(), timeout=10)
print('Status:', response.status_code)
"
```

---

## 🔍 디버깅 방법

### SSL 상세 로그 활성화
```bash
export SSLKEYLOGFILE=/tmp/sslkeys.log
.venv/bin/python your_script.py
```

### OpenSSL 버전 확인
```bash
.venv/bin/python -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

### certifi CA 번들 확인
```bash
.venv/bin/python -c "import certifi; print(certifi.where())"
cat $(python -c "import certifi; print(certifi.where())") | head -20
```

### 환경 변수 확인
```bash
echo $SSL_CERT_FILE
echo $REQUESTS_CA_BUNDLE
```

---

## 📊 현재 프로젝트 적용 상태

### ✅ 이미 적용된 방법
1. certifi 사용 (방법 1)
2. 환경 변수 설정 (방법 6)
3. requests Session + certifi (방법 5)
4. urllib3 경고 억제 (방법 9)

### 📁 관련 파일
```
utils/
├── genai_client.py       # Gemini API SSL 설정
└── ssl_fix.py            # SSL 전역 설정 유틸리티

nanobanana_api.py         # Nanobanana API SSL 설정
requirements.txt          # certifi, urllib3 포함
```

### 🧪 테스트 스크립트
```bash
# SSL 설정 테스트
.venv/bin/python utils/ssl_fix.py

# 패키지 확인
.venv/bin/pip list | grep -E "(certifi|urllib3|requests)"
```

---

## ⚠️ 주의사항

### 프로덕션 환경
1. **verify=False는 절대 사용 금지**
   - 중간자 공격(MITM)에 취약
   - 보안 감사 실패

2. **certifi 최신 버전 유지**
   ```bash
   ~/.local/bin/uv pip install --upgrade certifi
   ```

3. **SSL 검증 로그 모니터링**
   - SSL 오류가 발생하면 즉시 알림
   - 주기적인 인증서 만료 확인

### 개발 환경
1. `verify=False`는 로컬에서만 임시로 사용
2. SSL 오류 발생 시 근본 원인 파악 우선
3. 임시 해결책으로 넘어가지 말고 제대로 수정

---

## 🆘 여전히 문제 발생 시

### 1단계: 기본 확인
```bash
# Python 버전
.venv/bin/python --version

# OpenSSL 버전
.venv/bin/python -c "import ssl; print(ssl.OPENSSL_VERSION)"

# certifi 경로
.venv/bin/python -c "import certifi; print(certifi.where())"

# 패키지 버전
.venv/bin/pip list | grep -E "(certifi|urllib3|requests|openssl)"
```

### 2단계: certifi 재설치
```bash
~/.local/bin/uv pip uninstall certifi
~/.local/bin/uv pip install certifi --upgrade
```

### 3단계: Python 환경 재생성
```bash
cd 6.해커톤/3.model
rm -rf .venv
~/.local/bin/uv venv --python 3.10.18
source .venv/bin/activate
~/.local/bin/uv pip install -r requirements.txt
```

### 4단계: 시스템 인증서 업데이트

#### macOS
```bash
# macOS 키체인 인증서 업데이트
/Applications/Python\ 3.10/Install\ Certificates.command
```

#### Linux
```bash
sudo update-ca-certificates
```

#### Windows
```
Windows Update를 통해 루트 인증서 업데이트
```

---

## 📚 참고 자료

- [certifi 공식 문서](https://github.com/certifi/python-certifi)
- [requests SSL 가이드](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification)
- [Python SSL 모듈](https://docs.python.org/3/library/ssl.html)
- [urllib3 문서](https://urllib3.readthedocs.io/)

---

## 🎯 요약

**현재 프로젝트에서는 방법 1 (certifi)이 적용되어 있습니다.**

문제가 발생하면:
1. `utils/ssl_fix.py` 실행
2. 오류 메시지 확인
3. 이 문서의 방법들 시도
4. 여전히 문제 시 Python 환경 재생성

**대부분의 SSL 오류는 certifi + 환경 변수 설정으로 해결됩니다!**
