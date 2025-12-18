# Model Server API 테스트 예시

## 🌐 Base URL
```
http://localhost:8102
```

---

## 📋 API 목록

### 1. Health Check
```bash
curl http://localhost:8102/health
```

**응답**:
```json
{
  "status": "ok"
}
```

---

### 2. 텍스트 생성 API (Gemini)

#### Endpoint
```
POST /api/generate-text
```

#### Request (JSON)
```bash
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
    "wedding_time": "오후 2시 30분",
    "address": "서울특별시 강남구 테헤란로 123"
  }'
```

#### Response
```json
{
  "success": true,
  "data": {
    "greetings": [
      "두 사람의 아름다운 시작을 함께 축복해주세요...",
      "평생을 함께할 사람을 만나 백년가약을 맺게 되었습니다...",
      "사랑하는 사람과 영원을 약속하는 날입니다..."
    ],
    "invitations": [
      "홍길동 ♥ 김영희의 결혼식에 초대합니다",
      "두 사람이 하나 되는 소중한 자리에 함께해주세요",
      "저희의 새로운 시작을 축복해주시면 감사하겠습니다"
    ],
    "location": "더 클래식 500 | 서울특별시 강남구 테헤란로 123",
    "closing": [
      "귀한 걸음 해주셔서 감사합니다",
      "오셔서 축복해주시면 큰 기쁨이 되겠습니다",
      "함께해주시는 모든 분들께 감사드립니다"
    ]
  }
}
```

---

### 3. 청첩장 이미지 생성 API (나노바나나)

#### Endpoint
```
POST /api/generate-invitation
```

#### Request (Multipart Form Data)

**옵션 1: curl 사용**
```bash
curl -X POST http://localhost:8102/api/generate-invitation \
  -F "wedding_image=@/path/to/wedding_photo.jpg" \
  -F "style_image=@/path/to/style_reference.jpg" \
  -F "tone=romantic" \
  -F "groom_name=홍길동" \
  -F "bride_name=김영희" \
  -F "groom_father=홍판서" \
  -F "groom_mother=김씨" \
  -F "bride_father=김판서" \
  -F "bride_mother=이씨" \
  -F "venue=더 클래식 500" \
  -F "wedding_date=2025년 5월 20일 토요일" \
  -F "wedding_time=오후 2시 30분" \
  -F "address=서울특별시 강남구 테헤란로 123" \
  -F "border_design_id=border1" \
  -F "latitude=37.5665" \
  -F "longitude=126.9780" \
  -F "floor_hall=3층 그랜드홀"
```

**옵션 2: Python requests 사용**
```python
import requests

url = "http://localhost:8102/api/generate-invitation"

files = {
    'wedding_image': open('/path/to/wedding_photo.jpg', 'rb'),
    'style_image': open('/path/to/style_reference.jpg', 'rb')
}

data = {
    'tone': 'romantic',
    'groom_name': '홍길동',
    'bride_name': '김영희',
    'groom_father': '홍판서',
    'groom_mother': '김씨',
    'bride_father': '김판서',
    'bride_mother': '이씨',
    'venue': '더 클래식 500',
    'wedding_date': '2025년 5월 20일 토요일',
    'wedding_time': '오후 2시 30분',
    'address': '서울특별시 강남구 테헤란로 123',
    'border_design_id': 'border1',
    'latitude': 37.5665,
    'longitude': 126.9780,
    'floor_hall': '3층 그랜드홀'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**옵션 3: JavaScript (fetch) 사용**
```javascript
const formData = new FormData();

// 파일 첨부
formData.append('wedding_image', weddingImageFile);
formData.append('style_image', styleImageFile);

// 데이터 추가
formData.append('tone', 'romantic');
formData.append('groom_name', '홍길동');
formData.append('bride_name', '김영희');
formData.append('groom_father', '홍판서');
formData.append('groom_mother', '김씨');
formData.append('bride_father', '김판서');
formData.append('bride_mother', '이씨');
formData.append('venue', '더 클래식 500');
formData.append('wedding_date', '2025년 5월 20일 토요일');
formData.append('wedding_time', '오후 2시 30분');
formData.append('address', '서울특별시 강남구 테헤란로 123');
formData.append('border_design_id', 'border1');
formData.append('latitude', '37.5665');
formData.append('longitude', '126.9780');
formData.append('floor_hall', '3층 그랜드홀');

fetch('http://localhost:8102/api/generate-invitation', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

#### Response
```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "page_number": 1,
        "image_url": "https://s3.amazonaws.com/bucket/invitation-page1-xxx.png",
        "type": "cover"
      },
      {
        "page_number": 2,
        "image_url": "https://s3.amazonaws.com/bucket/invitation-page2-xxx.png",
        "type": "content"
      },
      {
        "page_number": 3,
        "image_url": "https://s3.amazonaws.com/bucket/invitation-page3-xxx.png",
        "type": "location"
      }
    ],
    "texts": {
      "greeting": "두 사람의 아름다운 시작을 함께 축복해주세요",
      "invitation": "홍길동 ♥ 김영희의 결혼식에 초대합니다",
      "location": "더 클래식 500 | 서울특별시 강남구 테헤란로 123 | 3층 그랜드홀"
    }
  }
}
```

---

## 🎨 Border Design 옵션

### border1 - 클래식 프레임
- 우아한 골드 테두리
- 빈티지 장식 모티브
- 색상: 골드(#D4AF37), 브론즈(#8B7355)

### border2 - 플로럴 프레임
- 꽃무늬 장식 테두리
- 부드러운 꽃잎 패턴
- 색상: 핑크(#FFB6C1), 화이트(#FFFFFF), 민트(#98D8C8)

### border3 - 미니멀 프레임
- 심플한 라인 테두리
- 모던하고 깔끔한 디자인
- 색상: 다크 그레이(#2C3E50), 라이트 그레이(#ECF0F1)

### border4 - 로맨틱 프레임
- 하트와 리본 장식
- 사랑스러운 디테일
- 색상: 핫핑크(#FF69B4), 골드(#FFD700), 화이트(#FFFFFF)

---

## 🎯 Tone 옵션

| Tone | 특징 | 예시 |
|------|------|------|
| `formal` | 격식 있는 | "~합니다", "~드립니다" |
| `casual` | 편안한 | "~해요", "~할게요" |
| `modern` | 모던한 | 간결하고 세련됨 |
| `classic` | 클래식한 | 전통적이고 우아함 |
| `romantic` | 로맨틱한 | 사랑과 감성 |
| `minimal` | 미니멀한 | 최소한의 문장 |

---

## 🧪 Swagger UI로 테스트

브라우저에서 아래 URL 접속:
```
http://localhost:8102/docs
```

- Interactive API 문서
- 직접 테스트 가능
- Request/Response 예시 자동 생성

---

## 📊 에러 응답 형식

### 실패 시
```json
{
  "success": false,
  "error": "Error message here",
  "traceback": "Full traceback (개발 환경에서만)"
}
```

---

## 🔧 디버깅

### 서버 로그 확인
```bash
# 백그라운드 실행 시
tail -f nohup.out

# 또는 uvicorn 로그 직접 확인
```

### API 응답 시간 측정
```bash
time curl -X POST http://localhost:8102/api/generate-text \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

## 🚀 프론트엔드 통합 예시

### React + Axios
```javascript
import axios from 'axios';

// 텍스트 생성
const generateText = async (formData) => {
  const response = await axios.post(
    'http://localhost:8102/api/generate-text',
    formData
  );
  return response.data;
};

// 이미지 생성
const generateInvitation = async (weddingImage, styleImage, formData) => {
  const data = new FormData();
  data.append('wedding_image', weddingImage);
  data.append('style_image', styleImage);

  Object.keys(formData).forEach(key => {
    data.append(key, formData[key]);
  });

  const response = await axios.post(
    'http://localhost:8102/api/generate-invitation',
    data,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
  return response.data;
};
```

---

## 📝 참고사항

### 필수 파라미터
- ✅ 모든 `Form(...)` 파라미터는 필수
- ℹ️ `latitude`, `longitude`, `floor_hall`은 선택 (Optional)

### 파일 크기 제한
- 웨딩 사진: 최대 10MB 권장
- 스타일 이미지: 최대 10MB 권장

### 응답 시간
- 텍스트 생성: ~3-5초 (Gemini API)
- 이미지 생성: ~30-60초 (나노바나나 API + S3 업로드)

### CORS 설정
- 현재 모든 Origin 허용 (`allow_origins=["*"]`)
- 프로덕션 환경에서는 특정 도메인만 허용 권장
