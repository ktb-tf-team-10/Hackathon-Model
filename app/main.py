from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.genai import types
from typing import Optional
from pydantic import BaseModel
import requests
import sys
import os
import base64
import ssl


# --- Request DTOs ---
class GroomDto(BaseModel):
    name: str
    fatherName: Optional[str] = ""
    motherName: Optional[str] = ""

class BrideDto(BaseModel):
    name: str
    fatherName: Optional[str] = ""
    motherName: Optional[str] = ""

class WeddingDto(BaseModel):
    hallName: str
    address: str
    date: str
    time: str

class GenerateInvitationRequest(BaseModel):
    groom: GroomDto
    bride: BrideDto
    wedding: WeddingDto
    weddingImageUrl: str
    styleImageUrl: str
    extraMessage: Optional[str] = ""
    additionalRequest: Optional[str] = ""
    tone: Optional[str] = "WARM"
    frame: Optional[str] = "CLASSIC"
    modelName: Optional[str] = "models/gemini-3-pro-image-preview"


# 전역 SSL 인증서 검증 비활성화
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_text_api import generate_wedding_texts
# from nanobanana_api import generate_invitation_with_nanobanana
from gemini_invitation_api import generate_invitation_with_gemini
from imagen_design_api import generate_invitation_design

app = FastAPI(
    title="Wedding OS - Model API",
    description="청첩장 AI 텍스트 및 이미지 생성 API",
    version="1.0.0"
)

# 422 Unprocessable Entity 오류 상세 로깅을 위한 핸들러
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    print("❌ Validation Error Details:")
    for error in error_details:
        print(f"   - Field: {error.get('loc')}, Message: {error.get('msg')}, Type: {error.get('type')}")
    
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Validation Error", "detail": error_details},
    )

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정 (생성된 이미지 로컬 저장용)
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
generated_images_dir = os.path.join(static_dir, "generated_images")
if not os.path.exists(generated_images_dir):
    os.makedirs(generated_images_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return {
        "message": "Wedding OS Model API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - 헬스 체크",
            "POST /api/generate-text - 텍스트 생성 (Gemini)",
            "POST /api/generate-invitation - 청첩장 이미지 생성 (Gemini/Imagen)",
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/generate-text")
async def generate_text(request: dict):
    """
    청첩장 텍스트 생성 API (Gemini Flash 2.5)
    """
    try:
        result = generate_wedding_texts(
            tone=request.get("tone", "romantic"),
            groom_name=request.get("groom_name"),
            bride_name=request.get("bride_name"),
            groom_father=request.get("groom_father"),
            groom_mother=request.get("groom_mother"),
            bride_father=request.get("bride_father"),
            bride_mother=request.get("bride_mother"),
            venue=request.get("venue"),
            wedding_date=request.get("wedding_date"),
            wedding_time=request.get("wedding_time"),
            address=request.get("address", "")
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/generate-invitation-test")
async def generate_invitation_test(
    model_type: str = Form("nanobanana"), # nanobanana, flash2.5, gemini3.0
    wedding_image: Optional[UploadFile] = File(None),
    style_image: Optional[UploadFile] = File(None),
    tone: Optional[str] = Form(None),
    groom_name: Optional[str] = Form(None),
    bride_name: Optional[str] = Form(None),
    venue: Optional[str] = Form(None),
    wedding_date: Optional[str] = Form(None),
    wedding_time: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    border_design_id: Optional[str] = Form("classic_gold"),
    groom_father: Optional[str] = Form(""),
    groom_mother: Optional[str] = Form(""),
    bride_father: Optional[str] = Form(""),
    bride_mother: Optional[str] = Form(""),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
):
    """
    청첩장 이미지 생성 테스트 API (나노바나나 vs Gemini Flash 2.5 vs Gemini 3.0)
    """
    print(f"DEBUG: model_type={model_type}")
    
    try:
        wedding_image_base64 = None
        if wedding_image:
            wedding_image_bytes = await wedding_image.read()
            wedding_image_base64 = base64.b64encode(wedding_image_bytes).decode('utf-8')

        style_image_base64 = None
        if style_image:
            style_image_bytes = await style_image.read()
            style_image_base64 = base64.b64encode(style_image_bytes).decode('utf-8')

        if model_type == "nanobanana":
            # 나노바나나 대신 Imagen으로 대체 가능성 염두에 둠
            result = {"error": "Nanobanana is currently disabled due to SSL issues."}
        elif model_type == "flash2.5" or model_type == "imagen-4.0-generate":
            # Flash 2.5 또는 Imagen 4.0 시도
            # imagen_design_api.py 내부에서 fallback 로직이 작동합니다.
            processed_texts = {
                "greeting": "환영합니다",
                "invitation": "초대합니다",
                "location": "서울 어딘가",
                "closing": "감사합니다"
            }
            result = await generate_invitation_design(
                style_image_base64=style_image_base64,
                wedding_image_base64=wedding_image_base64,
                texts=processed_texts,
                venue_info={"name": venue, "address": address}
            )
        elif model_type == "gemini3.0" or model_type == "gemini-3-pro-image":
            # Gemini 3.0 (실제로는 gemini-3-pro-image-preview 사용)
            result = generate_invitation_with_gemini(
                model_name='gemini-3-pro-image-preview',
                groom_name=groom_name,
                bride_name=bride_name,
                venue=venue,
                wedding_date=wedding_date,
                wedding_time=wedding_time,
                wedding_image_base64=wedding_image_base64,
                style_image_base64=style_image_base64,
                tone=tone
            )
        else:
            return {"success": False, "error": f"지원하지 않는 모델 타입입니다: {model_type}"}

        return {"success": True, "data": result}

    except Exception as e:
        import traceback
        print(f"❌ Error during generation ({model_type}): {e}")
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@app.post("/api/generate-invitation")
async def generate_invitation(request: GenerateInvitationRequest):
    """
    청첩장 이미지 생성 API

    Request Body:
    {
        "groom": {"name": "홍길동", "fatherName": "홍부", "motherName": "김씨"},
        "bride": {"name": "김영희", "fatherName": "김부", "motherName": "이씨"},
        "wedding": {"hallName": "○○웨딩홀", "address": "서울 ...", "date": "2026-03-21", "time": "14:00"},
        "weddingImageUrl": "https://...",
        "styleImageUrl": "https://...",
        "extraMessage": "주차 공간이 협소합니다",
        "additionalRequest": "잔잔한 분위기",
        "tone": "WARM",
        "frame": "CLASSIC"
    }
    """
    print(f"DEBUG: request={request}")

    try:
        # URL에서 이미지 다운로드 후 Base64로 변환
        wedding_image_base64 = download_image_as_base64(request.weddingImageUrl)
        style_image_base64 = download_image_as_base64(request.styleImageUrl)

        # 1. 먼저 Gemini로 문구 생성
        texts_result = generate_wedding_texts(
            tone=request.tone,
            groom_name=request.groom.name,
            bride_name=request.bride.name,
            groom_father=request.groom.fatherName,
            groom_mother=request.groom.motherName,
            bride_father=request.bride.fatherName,
            bride_mother=request.bride.motherName,
            venue=request.wedding.hallName,
            wedding_date=request.wedding.date,
            wedding_time=request.wedding.time,
            address=request.wedding.address
        )

        # 2. 이미지 생성용 텍스트 구성
        processed_texts = {
            "greeting": texts_result.get("greetings", [""])[0],
            "invitation": texts_result.get("invitations", [""])[0],
            "location": texts_result.get("location", ""),
            "closing": texts_result.get("closing", [""])[0],
            "extraMessage": request.extraMessage,
            "additionalRequest": request.additionalRequest
        }

        venue_info = {
            "name": request.wedding.hallName,
            "address": request.wedding.address
        }

        # Imagen/Gemini 디자인 생성 (이미 S3에 업로드됨)
        result = await generate_invitation_design(
            style_image_base64=style_image_base64,
            wedding_image_base64=wedding_image_base64,
            texts=processed_texts,
            venue_info=venue_info,
            model_name=request.modelName
        )

        # 이미지 URL 추출 (이미 CloudFront URL)
        image_urls = [page.get("image_url", "") for page in result.get("pages", [])]

        print(f"✅ 생성 완료: {image_urls}")

        # 응답: 이미지 URL 리스트 + 텍스트
        return {
            "success": True,
            "data": {
                "imageUrls": image_urls,
                "texts": processed_texts
            }
        }

    except Exception as e:
        import traceback
        print(f"❌ Error during generation: {e}")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# --- 유틸리티: URL에서 이미지 다운로드 후 Gemini Part로 변환 ---
def download_image_as_part(url: str) -> types.Part:
    """URL에서 이미지 다운로드 후 Gemini Part로 반환"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "image/png")
    if ";" in content_type:
        content_type = content_type.split(";")[0]

    return types.Part.from_bytes(data=response.content, mime_type=content_type)


def download_image_as_base64(url: str) -> str:
    """URL에서 이미지 다운로드 후 base64 문자열로 반환"""
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return base64.b64encode(response.content).decode('utf-8')
