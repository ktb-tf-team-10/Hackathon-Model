# 청첩장 이미지 생성 테스트 API 명세서

Nanobanana (Gemini 3 Pro) 로컬 튜닝 및 순차적 생성 로직이 적용된 최신 API 명세입니다.

## 기본 정보
- **Endpoint**: `/api/generate-invitation-test`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`

## Request Parameters (Form Data)

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :--- | :--- |
| `model_type` | string | **필수** | `"nanobanana"`로 고정 |
| `wedding_image` | file | 선택 | 신랑신부 웨딩 사진 (Page 1 생성 시 사용) |
| `style_image` | file | 선택 | 스타일 참조 이미지 (전체 페이지 생성 시 사용) |
| `groom_name` | string | 선택 | 신랑 이름 |
| `bride_name` | string | 선택 | 신부 이름 |
| `venue` | string | 선택 | 예식장 이름 |
| `wedding_date` | string | 선택 | 예식 날짜 (예: 2025년 5월 5일) |
| `wedding_time` | string | 선택 | 예식 시간 (예: 낮 12시) |
| `address` | string | 선택 | 예식장 주소 |
| `tone` | string | 선택 | 청첩장 톤 (elegant, romantic, modern 등) |
| `border_design_id` | string | 선택 | 테두리 디자인 ID |
| `latitude` | float | 선택 | 예식장 위도 (지도 생성용) |
| `longitude` | float | 선택 | 예식장 경도 (지도 생성용) |
| `prompt_override_1` | string | **선택** | **Page 1 (표지) 프롬프트 오버라이드** |
| `prompt_override_2` | string | **선택** | **Page 2 (문구) 프롬프트 오버라이드** |
| `prompt_override_3` | string | **선택** | **Page 3 (장소) 프롬프트 오버라이드** |

## Response Body (JSON)

```json
{
  "success": true,
  "data": {
    "pages": [
      {
        "page_number": 1,
        "image_url": "http://localhost:8000/static/generated_images/invitation-page1_uuid.jpg",
        "type": "cover"
      },
      {
        "page_number": 2,
        "image_url": "http://localhost:8000/static/generated_images/invitation-page2_uuid.jpg",
        "type": "content"
      },
      {
        "page_number": 3,
        "image_url": "http://localhost:8000/static/generated_images/invitation-page3_uuid.jpg",
        "type": "location"
      }
    ],
    "texts": {
      "greeting": "...",
      "invitation": "...",
      "location": "..."
    }
  }
}
```

## Logic Flow (Internal)
1. **Gemini Text Generation**: `texts` 생성.
2. **Sequential Image Generation**:
   - **Page 1**: `Wedding Photo` + `Style Image` + `Prompt 1` -> **Image A**
   - **Page 2**: **Image A** + `Style Image` + `Prompt 2` -> **Image B**
   - **Page 3**: **Image B** + `Style Image` + `Map Image`(if lat/lon provided) + `Prompt 3` -> **Image C**
