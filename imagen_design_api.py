"""
Google Imagen 3 API를 사용한 청첩장 디자인 생성
STEP 5-6: 스타일 참조 이미지 + 사용자 이미지 + 문구를 바탕으로 청첩장 디자인 생성
"""

import os
import json
import base64
from typing import Dict, List, Optional
import requests
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
import boto3
from io import BytesIO
from PIL import Image
import uuid
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# AWS S3 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='ap-northeast-2'
)

BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'wedding-invitation-images')

# Google Cloud 설정
PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
LOCATION = 'us-central1'
aiplatform.init(project=PROJECT_ID, location=LOCATION)


def upload_to_s3(image_bytes: bytes, file_type: str = "design") -> str:
    """
    생성된 이미지를 S3에 업로드

    Args:
        image_bytes: 이미지 바이트
        file_type: 파일 타입 (design, edited, etc.)

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


def generate_invitation_design(
    style_image_base64: str,
    wedding_image_base64: str,
    texts: Dict[str, str],
    design_request: str = "",
    venue_info: Dict[str, str] = None
) -> Dict[str, any]:
    """
    Imagen 3를 사용하여 청첩장 디자인 생성

    Args:
        style_image_base64: 스타일 참조 이미지 (base64)
        wedding_image_base64: STEP4에서 업로드한 웨딩 사진 (base64)
        texts: STEP2,3에서 선택한 문구들
            {
                "greeting": "인사말",
                "invitation": "초대문구",
                "location": "장소안내",
                "closing": "마무리인사"
            }
        design_request: 추가 디자인 요청사항 (선택)
        venue_info: 예식장 정보 (지도 생성용)
            {
                "name": "예식장명",
                "address": "주소",
                "latitude": "위도",
                "longitude": "경도"
            }

    Returns:
        Dict: {
            "pages": [
                {"page_number": 1, "image_url": "S3 URL", "type": "cover"},
                {"page_number": 2, "image_url": "S3 URL", "type": "greeting"},
                ...
            ]
        }
    """

    # 프롬프트 파일 읽기
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "image_generation_prompt.md")
    with open(prompt_path, 'r', encoding='utf-8') as f:
        base_prompt = f.read()

    # 5개 페이지 생성
    pages = []

    # 1. 커버 페이지 (웨딩 사진)
    page1_prompt = base_prompt.format(
        page_type="웨딩 사진 커버 페이지",
        style_description="스타일 참조 이미지를 기반으로 한 디자인",
        main_content=f"중앙에 웨딩 사진 배치",
        additional_elements="우아한 테두리와 장식",
        text_content="",
        design_notes=design_request if design_request else "깔끔하고 모던한 디자인"
    )

    page1_url = _generate_single_page(page1_prompt, wedding_image_base64, style_image_base64)
    pages.append({
        "page_number": 1,
        "image_url": page1_url,
        "type": "cover",
        "description": "웨딩 사진 커버"
    })

    # 2. 인사말 페이지
    page2_prompt = base_prompt.format(
        page_type="인사말 페이지",
        style_description="스타일 참조 이미지의 폰트와 색상 적용",
        main_content="인사말 텍스트",
        additional_elements="꽃 장식 또는 패턴",
        text_content=texts.get('greeting', ''),
        design_notes="가독성 좋은 폰트 사용"
    )

    page2_url = _generate_single_page(page2_prompt, None, style_image_base64)
    pages.append({
        "page_number": 2,
        "image_url": page2_url,
        "type": "greeting",
        "description": "인사말"
    })

    # 3. 초대 문구 페이지
    page3_prompt = base_prompt.format(
        page_type="초대 문구 페이지",
        style_description="스타일 참조 이미지와 일관된 디자인",
        main_content="초대 문구",
        additional_elements="우아한 라인과 장식",
        text_content=texts.get('invitation', ''),
        design_notes="따뜻하고 환영하는 느낌"
    )

    page3_url = _generate_single_page(page3_prompt, None, style_image_base64)
    pages.append({
        "page_number": 3,
        "image_url": page3_url,
        "type": "invitation",
        "description": "초대 문구"
    })

    # 4. 장소 안내 페이지 (지도 포함)
    map_image = None
    if venue_info:
        map_image = _generate_map_image(venue_info)

    page4_prompt = base_prompt.format(
        page_type="장소 안내 페이지",
        style_description="스타일 참조 이미지 기반",
        main_content="장소 안내 문구 + 지도",
        additional_elements="찾아오시는 길 아이콘",
        text_content=texts.get('location', ''),
        design_notes="지도와 텍스트의 조화"
    )

    page4_url = _generate_single_page(page4_prompt, map_image, style_image_base64)
    pages.append({
        "page_number": 4,
        "image_url": page4_url,
        "type": "location",
        "description": "장소 안내 + 지도"
    })

    # 5. 마무리 인사 페이지
    page5_prompt = base_prompt.format(
        page_type="마무리 인사 페이지",
        style_description="스타일 참조 이미지와 일관",
        main_content="마무리 인사",
        additional_elements="감사 인사와 장식",
        text_content=texts.get('closing', ''),
        design_notes="따뜻하고 감사한 느낌"
    )

    page5_url = _generate_single_page(page5_prompt, None, style_image_base64)
    pages.append({
        "page_number": 5,
        "image_url": page5_url,
        "type": "closing",
        "description": "마무리 인사"
    })

    return {"pages": pages}


def _generate_single_page(
    prompt: str,
    content_image_base64: Optional[str],
    style_image_base64: str
) -> str:
    """
    Imagen 3를 사용하여 단일 페이지 생성

    Args:
        prompt: 생성 프롬프트
        content_image_base64: 컨텐츠 이미지 (웨딩 사진, 지도 등)
        style_image_base64: 스타일 참조 이미지

    Returns:
        str: S3 URL
    """

    # Imagen 3 API 엔드포인트
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-generate-001"
    )

    # 이미지 생성 요청
    instances = [
        {
            "prompt": prompt,
            "image": {
                "bytesBase64Encoded": style_image_base64
            },
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "3:4",  # 청첩장 비율
                "safetySetting": "block_some",
                "personGeneration": "allow_all"
            }
        }
    ]

    if content_image_base64:
        instances[0]["image"]["contentImage"] = {
            "bytesBase64Encoded": content_image_base64
        }

    response = endpoint.predict(instances=instances)

    # 생성된 이미지 추출
    generated_image_base64 = response.predictions[0]["bytesBase64Encoded"]
    image_bytes = base64.b64decode(generated_image_base64)

    # S3에 업로드
    image_url = upload_to_s3(image_bytes, "design")

    return image_url


def _generate_map_image(venue_info: Dict[str, str]) -> str:
    """
    Google Maps Static API를 사용하여 지도 이미지 생성

    Args:
        venue_info: 예식장 정보

    Returns:
        str: 지도 이미지 base64
    """

    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    lat = venue_info.get('latitude')
    lng = venue_info.get('longitude')
    venue_name = venue_info.get('name')

    # Google Maps Static API
    map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{lng}&zoom=16&size=600x400&markers=color:red%7C{lat},{lng}&key={google_maps_api_key}"

    response = requests.get(map_url)
    map_image_base64 = base64.b64encode(response.content).decode('utf-8')

    return map_image_base64


def edit_invitation_design(
    original_design_pages: List[Dict],
    edit_request: str,
    reference_image_base64: Optional[str] = None
) -> Dict[str, any]:
    """
    청첩장 부분 수정 (STEP 7)

    Args:
        original_design_pages: 원본 디자인 페이지들
        edit_request: 수정 요청사항
        reference_image_base64: 참고 이미지 (선택)

    Returns:
        Dict: 수정된 페이지들
    """

    # 프롬프트에 수정 요청사항 추가
    edit_prompt = f"""
    원본 청첩장 디자인을 다음과 같이 수정해주세요:

    수정 요청사항:
    {edit_request}

    원본 디자인의 전체적인 스타일과 톤은 유지하되, 요청사항만 반영해주세요.
    """

    # 각 페이지별로 수정 (실제로는 사용자가 특정 페이지만 지정할 수도 있음)
    edited_pages = []

    for page in original_design_pages:
        # 원본 이미지 다운로드
        original_url = page["image_url"]
        response = requests.get(original_url)
        original_image_base64 = base64.b64encode(response.content).decode('utf-8')

        # Imagen 3 Edit API 사용
        edited_url = _edit_single_page(
            original_image_base64,
            edit_prompt,
            reference_image_base64
        )

        edited_pages.append({
            **page,
            "image_url": edited_url,
            "edited": True
        })

    return {"pages": edited_pages}


def _edit_single_page(
    original_image_base64: str,
    edit_prompt: str,
    reference_image_base64: Optional[str]
) -> str:
    """
    단일 페이지 수정

    Args:
        original_image_base64: 원본 이미지
        edit_prompt: 수정 프롬프트
        reference_image_base64: 참고 이미지

    Returns:
        str: 수정된 이미지 S3 URL
    """

    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/imagen-3.0-edit-001"
    )

    instances = [
        {
            "prompt": edit_prompt,
            "image": {
                "bytesBase64Encoded": original_image_base64
            },
            "parameters": {
                "sampleCount": 1,
                "editMode": "inpainting-insert"  # 또는 "inpainting-remove", "product-image"
            }
        }
    ]

    if reference_image_base64:
        instances[0]["referenceImage"] = {
            "bytesBase64Encoded": reference_image_base64
        }

    response = endpoint.predict(instances=instances)

    # 수정된 이미지 추출
    edited_image_base64 = response.predictions[0]["bytesBase64Encoded"]
    image_bytes = base64.b64decode(edited_image_base64)

    # S3에 업로드
    image_url = upload_to_s3(image_bytes, "edited")

    return image_url


# 테스트 코드
if __name__ == "__main__":
    print("=" * 80)
    print("Imagen 3 청첩장 디자인 생성 테스트")
    print("=" * 80)

    # 테스트는 실제 API 키와 이미지가 필요합니다
    print("\n이 스크립트는 실제 Gemini API 키와 이미지가 필요합니다.")
    print("FastAPI 서버를 통해 테스트하세요.")
