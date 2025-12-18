"""
Google Imagen 및 Gemini API를 사용한 청첩장 디자인 생성
다양한 모델을 선택하여 테스트할 수 있도록 구성되었습니다.
"""

import os
import json
import base64
import asyncio
from typing import Dict, List, Optional, Any
import boto3
import uuid
from dotenv import load_dotenv
from google.genai import types

# 프로젝트 내부 유틸리티 사용
from utils.genai_client import get_genai_client

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

# 로컬 저장 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
GENERATED_DIR = os.path.join(STATIC_DIR, "generated_images")

# 서버 URL 설정 (환경 변수에서 가져오거나 기본값 사용)
MODEL_SERVER_URL = os.environ.get('MODEL_SERVER_URL', 'http://localhost:8102')

def save_locally(image_bytes: bytes, file_type: str = "design") -> str:
    """
    생성된 이미지를 로컬 파일 시스템에 저장하고 URL을 반환
    """
    if not os.path.exists(GENERATED_DIR):
        os.makedirs(GENERATED_DIR, exist_ok=True)
        
    filename = f"{file_type}_{uuid.uuid4()}.png"
    filepath = os.path.join(GENERATED_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
        
    # 클라이언트가 접근 가능한 URL 반환
    return f"{MODEL_SERVER_URL}/static/generated_images/{filename}"

def upload_to_s3(image_bytes: bytes, file_type: str = "design") -> str:
    file_key = f"{file_type}/{uuid.uuid4()}.png"
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=image_bytes,
        ContentType='image/png'
    )
    return f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{file_key}"

async def generate_invitation_design(
    style_image_base64: str,
    wedding_image_base64: str,
    texts: Dict[str, str],
    design_request: str = "",
    venue_info: Dict[str, str] = None,
    model_name: str = "gemini-3-pro-image-preview"  # 기본 모델
) -> Dict[str, any]:
    """
    청첩장 디자인 생성 (병렬 처리)
    
    Args:
        model_name: 사용할 모델명 (gemini-3-pro-image-preview, imagen-4.0-generate-001 등)
    """
    
    tasks = []
    
    # 1. 커버 페이지
    page1_prompt = f"Wedding invitation cover. Style: Reference. Content: Couple photo. {design_request}"
    tasks.append(_generate_single_page_task(page1_prompt, wedding_image_base64, style_image_base64, 1, "cover", "웨딩 사진 커버", model_name))

    # 2. 인사말 페이지
    page2_prompt = f"Wedding greeting page. Text: {texts.get('greeting', '')}. Style: Reference."
    tasks.append(_generate_single_page_task(page2_prompt, None, style_image_base64, 2, "greeting", "인사말", model_name))

    # 3. 초대 문구 페이지
    page3_prompt = f"Wedding invitation text page. Text: {texts.get('invitation', '')}. Style: Reference."
    tasks.append(_generate_single_page_task(page3_prompt, None, style_image_base64, 3, "invitation", "초대 문구", model_name))

    # 4. 장소 안내 페이지
    page4_prompt = f"Wedding venue info page. Text: {texts.get('location', '')}. Style: Reference."
    tasks.append(_generate_single_page_task(page4_prompt, None, style_image_base64, 4, "location", "장소 안내", model_name))

    # 5. 마무리 인사 페이지
    page5_prompt = f"Wedding closing page. Text: {texts.get('closing', '')}. Style: Reference."
    tasks.append(_generate_single_page_task(page5_prompt, None, style_image_base64, 5, "closing", "마무리 인사", model_name))

    # 모든 페이지 병렬 생성
    pages = await asyncio.gather(*tasks)
    
    return {
        "pages": sorted(pages, key=lambda x: x["page_number"]),
        "model_used": model_name
    }

async def _generate_single_page_task(prompt, content_img, style_img, page_num, p_type, desc, model_name):
    """병렬 실행을 위한 래퍼 함수"""
    loop = asyncio.get_event_loop()
    url = await loop.run_in_executor(None, _generate_single_page_sync, prompt, content_img, style_img, model_name)
    return {
        "page_number": page_num,
        "image_url": url,
        "type": p_type,
        "description": desc
    }

def _generate_single_page_sync(prompt: str, content_image_base64: Optional[str], style_image_base64: str, model_name: str) -> str:
    client = get_genai_client()
    
    # 모델명에 접두어가 없으면 추가 (test.sh 결과 반영)
    if not model_name.startswith("models/"):
        full_model_name = f"models/{model_name}"
    else:
        full_model_name = model_name

    try:
        if "imagen" in full_model_name.lower():
            print(f"🎨 [Page] Requesting Imagen 4.0: {full_model_name}")
            
            # 사용자 제공 Imagen 4.0 설정 적용
            config = dict(
                number_of_images=1,
                output_mime_type="image/png",
                person_generation="ALLOW_ALL",
                aspect_ratio="3:4",
                image_size="1K",
            )
            
            result = client.models.generate_images(
                model=full_model_name,
                prompt=f"{prompt}. Professional wedding invitation card design. High quality.",
                config=config
            )
            
            if result.generated_images:
                from io import BytesIO
                img_buffer = BytesIO()
                result.generated_images[0].image.save(img_buffer, format='PNG')
                url = save_locally(img_buffer.getvalue(), "design-imagen")
                print(f"✅ [Page] Imagen success: {url}")
                return url
                
        else:
            print(f"🚀 [Page] Requesting Gemini 3 Pro: {full_model_name}")
            
            parts = [types.Part.from_text(text=f"{prompt}. Create a professional wedding invitation card image. 3:4 aspect ratio.")]
            if style_image_base64:
                parts.append(types.Part.from_bytes(data=base64.b64decode(style_image_base64), mime_type="image/png"))
            if content_image_base64:
                parts.append(types.Part.from_bytes(data=base64.b64decode(content_image_base64), mime_type="image/png"))

            # 사용자 제공 Gemini 3 Pro 설정 반영
            tools = [types.Tool(googleSearch=types.GoogleSearch())]
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(image_size="1K"),
                tools=tools
            )

            response = client.models.generate_content(
                model=full_model_name,
                contents=[types.Content(role="user", parts=parts)],
                config=generate_content_config
            )
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        url = save_locally(part.inline_data.data, "design-gemini")
                        print(f"✅ [Page] Gemini success: {url}")
                        return url
            
    except Exception as e:
        print(f"❌ [Page] Failed with {full_model_name}: {e}")
        # 재귀적 Fallback 방지 및 최종 수단
        if "imagen" in full_model_name.lower():
            print("🔄 Falling back to models/gemini-3-pro-image-preview...")
            return _generate_single_page_sync(prompt, content_image_base64, style_image_base64, "models/gemini-3-pro-image-preview")

    print(f"⚠️ [Page] Returning placeholder for failed generation.")
    return "https://via.placeholder.com/600x800.png?text=Generation+Failed"
