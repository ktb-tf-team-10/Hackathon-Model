"""
나노바나나(Nanobanana) API를 사용한 청첩장 생성
단일 API 호출로 3장의 청첩장 이미지 생성
- 페이지 1: 웨딩 사진 (사용자 업로드 + 배경 디자인)
- 페이지 2: 인사말 + 초대 문구 (AI 생성 문구 + 배경 디자인)
- 페이지 3: 장소 안내 (기본 정보 + 지도 + 배경 디자인)
"""

import os
import json
import base64
from typing import Dict, List
import requests
import boto3
import uuid
import ssl
import certifi
from dotenv import load_dotenv
from google.genai import types

from utils.genai_client import get_genai_client, parse_json_response

# .env 파일 로드
load_dotenv()

# SSL 설정 (전역)
try:
    from utils.ssl_fix import configure_ssl_globally
    # 이미 ssl_fix.py에서 import 시 자동 실행되지만, 명시적 호출
    configure_ssl_globally()
except ImportError:
    # utils.ssl_fix가 없는 경우 기본 설정
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# AWS S3 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-northeast-2'
)

BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'wedding-invitation-images')


def upload_to_s3(image_bytes: bytes, file_type: str = "invitation") -> str:
    """
    생성된 이미지를 S3에 업로드

    Args:
        image_bytes: 이미지 바이트
        file_type: 파일 타입

    Returns:
        str: S3 URL
    """
    file_key = f"{file_type}/{uuid.uuid4()}.png"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=image_bytes,
        ContentType='image/png'
    )

    image_url = f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{file_key}"
    return image_url


def generate_wedding_texts_with_gemini(
    tone: str,
    groom_name: str,
    bride_name: str,
    venue: str,
    wedding_date: str,
    wedding_time: str,
    **kwargs
) -> Dict[str, str]:
    """
    Gemini를 사용하여 청첩장 문구 생성 (간소화 버전)

    Returns:
        Dict: {
            "greeting": "인사말",
            "invitation": "초대 문구",
            "location": "장소 안내"
        }
    """

    # 프롬프트 생성
    prompt = f"""
당신은 한국의 전문 청첩장 작가입니다.

다음 정보로 청첩장 문구를 생성해주세요:
- 톤: {tone}
- 신랑: {groom_name}
- 신부: {bride_name}
- 예식장: {venue}
- 날짜: {wedding_date} {wedding_time}

다음 3가지 문구를 생성하고, JSON 형식으로만 답변하세요:
1. greeting: 인사말 (2-3문장, 100-150자)
2. invitation: 초대 문구 (2문장, 80-120자)
3. location: 장소 안내 (1-2문장, 50-80자)

JSON 형식:
{{
  "greeting": "인사말 내용",
  "invitation": "초대 문구 내용",
  "location": "장소 안내 내용"
}}
"""

    # Gemini API 호출
    client = get_genai_client()
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    # JSON 파싱
    return parse_json_response(response)


def generate_invitation_with_nanobanana(
    # STEP 1: 기본 정보
    groom_name: str,
    bride_name: str,
    groom_father: str,
    groom_mother: str,
    bride_father: str,
    bride_mother: str,
    venue: str,
    venue_address: str,
    wedding_date: str,
    wedding_time: str,
    # STEP 2: 웨딩 사진
    wedding_image_base64: str,
    # STEP 3: 톤
    tone: str,
    # STEP 4: 스타일 + 테두리
    style_image_base64: str,
    border_design_id: str,
    # 선택사항
    venue_latitude: str = None,
    venue_longitude: str = None,
) -> Dict[str, any]:
    """
    나노바나나 API를 사용하여 3장의 청첩장 이미지 생성 (단일 호출)

    Returns:
        Dict: {
            "pages": [
                {"page_number": 1, "image_url": "S3 URL", "type": "cover"},
                {"page_number": 2, "image_url": "S3 URL", "type": "content"},
                {"page_number": 3, "image_url": "S3 URL", "type": "location"}
            ],
            "texts": {
                "greeting": "생성된 인사말",
                "invitation": "생성된 초대문구",
                "location": "생성된 장소안내"
            }
        }
    """

    print("=" * 80)
    print("청첩장 생성 시작...")
    print("=" * 80)

    # 1. Gemini로 문구 생성
    print("\n[1/4] Gemini로 문구 생성 중...")
    texts = generate_wedding_texts_with_gemini(
        tone=tone,
        groom_name=groom_name,
        bride_name=bride_name,
        venue=venue,
        wedding_date=wedding_date,
        wedding_time=wedding_time
    )
    print(f"✓ 문구 생성 완료")

    # 2. 지도 이미지 생성 (Google Maps Static API)
    map_image_base64 = None
    if venue_latitude and venue_longitude:
        print("\n[2/4] 지도 이미지 생성 중...")
        map_image_base64 = _generate_map_image(venue_latitude, venue_longitude, venue)
        print(f"✓ 지도 생성 완료")
    else:
        print("\n[2/4] 지도 정보 없음 - 스킵")

    # 3. 나노바나나 API로 3장의 이미지 생성
    print("\n[3/4] 나노바나나 API로 청첩장 이미지 생성 중...")

    # 통합 프롬프트 생성
    unified_prompt = _create_unified_prompt(
        groom_name=groom_name,
        bride_name=bride_name,
        texts=texts,
        venue=venue,
        venue_address=venue_address,
        wedding_date=wedding_date,
        wedding_time=wedding_time,
        tone=tone,
        border_design_id=border_design_id
    )

    # 나노바나나 API 호출 (단일 호출로 3장 생성)
    pages_images = _call_nanobanana_api(
        prompt=unified_prompt,
        wedding_image_base64=wedding_image_base64,
        style_image_base64=style_image_base64,
        map_image_base64=map_image_base64,
        border_design_id=border_design_id
    )

    # 4. S3에 업로드
    print("\n[4/4] S3에 업로드 중...")
    pages = []
    page_types = ["cover", "content", "location"]

    for idx, image_bytes in enumerate(pages_images):
        image_url = upload_to_s3(image_bytes, f"invitation-page{idx+1}")
        pages.append({
            "page_number": idx + 1,
            "image_url": image_url,
            "type": page_types[idx]
        })
        print(f"✓ 페이지 {idx + 1} 업로드 완료: {image_url[:50]}...")

    print("\n" + "=" * 80)
    print("청첩장 생성 완료!")
    print("=" * 80)

    return {
        "pages": pages,
        "texts": texts
    }


def _create_unified_prompt(
    groom_name: str,
    bride_name: str,
    texts: Dict[str, str],
    venue: str,
    venue_address: str,
    wedding_date: str,
    wedding_time: str,
    tone: str,
    border_design_id: str
) -> str:
    """
    나노바나나 API용 통합 프롬프트 생성
    """

    prompt = f"""
Create 3 pages of a Korean wedding invitation card with the following specifications:

**Overall Design Requirements:**
- Tone: {tone}
- Border Frame: {border_design_id} (apply to all pages like photo booth frames)
- Aspect Ratio: 3:4 (portrait)
- Style: Based on the provided style reference image

**Page 1 - Wedding Photo Cover:**
- Main content: The provided wedding photo
- Background: Apply the style reference design
- Frame: {border_design_id} border around the entire page
- Text overlay (optional): "{groom_name} ♥ {bride_name}"
- Keep the photo as the focal point

**Page 2 - Greeting & Invitation:**
- Background: Apply the style reference design with {border_design_id} frame
- Text content (in Korean, centered):
  * Greeting: {texts['greeting']}
  * Invitation: {texts['invitation']}
- Typography: Elegant, readable Korean fonts
- Decorative elements: Subtle floral or minimal decorations
- Color palette: Match the style reference

**Page 3 - Venue Information:**
- Background: Apply the style reference design with {border_design_id} frame
- Content:
  * Venue: {venue}
  * Address: {venue_address}
  * Date & Time: {wedding_date} {wedding_time}
  * Map: Include the provided map image
  * Additional text: {texts['location']}
- Layout: Map on top or center, text information below
- Icons: Simple location/time icons

**Technical Requirements:**
- All 3 pages must have consistent design language
- {border_design_id} frame must be visible on all pages
- Korean text must be clearly legible
- Professional print quality
- Cohesive color scheme across all pages

Generate all 3 pages in a single API call, maintaining visual consistency.
"""

    return prompt


def _call_nanobanana_api(
    prompt: str,
    wedding_image_base64: str,
    style_image_base64: str,
    map_image_base64: str,
    border_design_id: str
) -> List[bytes]:
    """
    나노바나나 API 호출 (실제 API 엔드포인트로 교체 필요)

    Returns:
        List[bytes]: 3장의 이미지 바이트 리스트
    """

    # TODO: 실제 나노바나나 API 엔드포인트로 교체
    api_url = os.environ.get('NANOBANANA_API_URL', 'https://api.nanobanana.com/v1/generate')
    api_key = os.environ.get('NANOBANANA_API_KEY')

    # API 요청 페이로드
    payload = {
        "prompt": prompt,
        "style_image": style_image_base64,
        "reference_images": [
            {"type": "wedding_photo", "data": wedding_image_base64},
        ],
        "border_frame": border_design_id,
        "num_images": 3,  # 3장 생성
        "aspect_ratio": "3:4",
        "output_format": "png"
    }

    if map_image_base64:
        payload["reference_images"].append(
            {"type": "map", "data": map_image_base64}
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 강력한 SSL 무시 설정을 위해 세션 및 어댑터 사용
    session = requests.Session()
    try:
        try:
            from utils.ssl_fix import TLSAdapter
            session.mount('https://', TLSAdapter())
        except ImportError:
            pass

        # API 호출
        response = session.post(
            api_url,
            json=payload,
            headers=headers,
            verify=False,  # 인증서 검증 안 함
            timeout=120
        )
    except Exception as e:
        print(f"나노바나나 API 호출 중 오류 발생: {e}")
        raise e
    finally:
        session.close()

    if response.status_code != 200:
        # 상세 오류 내용 출력
        print(f"❌ 나노바나나 API 오류 응답: {response.status_code}")
        print(f"   응답 본문: {response.text[:500]}")
        raise Exception(f"나노바나나 API 오류: {response.status_code} - {response.text}")

    try:
        result = response.json()
    except json.JSONDecodeError:
        # 나노바나나 서버가 JSON 외의 텍스트를 함께 반환하는 경우가 있어
        # 가장 바깥쪽 중괄호만 추출해서 재시도한다.
        raw = response.text.strip()
        start = raw.find('{')
        end = raw.rfind('}') + 1
        if start == -1 or end == -1:
            raise Exception(f"나노바나나 응답 JSON 파싱 실패: {raw[:200]}")
        cleaned = raw[start:end]
        result = json.loads(cleaned)

    # 이미지 추출 (base64 디코딩)
    images = []
    for img_data in result.get("images", []):
        image_bytes = base64.b64decode(img_data["b64_json"])
        images.append(image_bytes)

    return images


def _generate_map_image(latitude: str, longitude: str, venue_name: str) -> str:
    """
    Google Maps Static API를 사용하여 지도 이미지 생성

    Returns:
        str: 지도 이미지 base64
    """

    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')

    # Google Maps Static API
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=16&size=600x400&markers=color:red%7Clabel:{venue_name[0]}%7C{latitude},{longitude}&key={google_maps_api_key}"

    response = requests.get(map_url)
    map_image_base64 = base64.b64encode(response.content).decode('utf-8')

    return map_image_base64


# 테스트 코드
if __name__ == "__main__":
    print("=" * 80)
    print("나노바나나 API 청첩장 생성 테스트")
    print("=" * 80)

    # 실제 API 키와 이미지가 필요합니다
    print("\n이 스크립트는 실제 API 키와 이미지가 필요합니다.")
    print("FastAPI 서버를 통해 테스트하세요.")
