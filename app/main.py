from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
import sys
import os
import base64
import ssl

# 전역 SSL 인증서 검증 비활성화
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_text_api import generate_wedding_texts
from nanobanana_api import generate_invitation_with_nanobanana

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

@app.get("/")
async def root():
    return {
        "message": "Wedding OS Model API",
        "version": "1.0.0",
        "endpoints": [
            "GET /health - 헬스 체크",
            "POST /api/generate-text - 텍스트 생성 (Gemini)",
            "POST /api/generate-invitation - 청첩장 이미지 생성 (나노바나나)",
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


@app.post("/api/generate-invitation")
async def generate_invitation(
    wedding_image: Optional[UploadFile] = File(None),
    style_image: Optional[UploadFile] = File(None),
    tone: Optional[str] = Form(None),
    groom_name: Optional[str] = Form(None),
    bride_name: Optional[str] = Form(None),
    venue: Optional[str] = Form(None),
    wedding_date: Optional[str] = Form(None),
    wedding_time: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    border_design_id: Optional[str] = Form(None),
    groom_father: Optional[str] = Form(""),
    groom_mother: Optional[str] = Form(""),
    bride_father: Optional[str] = Form(""),
    bride_mother: Optional[str] = Form(""),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    floor_hall: Optional[str] = Form(""),
):
    """
    청첩장 이미지 생성 API (나노바나나)
    """
    # 받은 데이터 로깅 (디버깅용)
    print("DEBUG: Received Form Data:")
    print(f"  - wedding_image: {wedding_image.filename if wedding_image else 'Missing'}")
    print(f"  - style_image: {style_image.filename if style_image else 'Missing'}")
    print(f"  - tone: {tone}")
    print(f"  - groom_name: {groom_name}")
    print(f"  - bride_name: {bride_name}")
    print(f"  - venue: {venue}")
    print(f"  - wedding_date: {wedding_date}")
    print(f"  - wedding_time: {wedding_time}")
    print(f"  - address: {address}")
    print(f"  - border_design_id: {border_design_id}")
    print(f"  - latitude: {latitude}")
    print(f"  - longitude: {longitude}")
    print(f"  - floor_hall: {floor_hall}")

    # 필수 필드 검증
    missing = []
    if not wedding_image: missing.append("wedding_image")
    if not style_image: missing.append("style_image")
    if not tone: missing.append("tone")
    if not groom_name: missing.append("groom_name")
    if not bride_name: missing.append("bride_name")
    if not venue: missing.append("venue")
    if not wedding_date: missing.append("wedding_date")
    if not wedding_time: missing.append("wedding_time")
    if not address: missing.append("address")
    if not border_design_id: missing.append("border_design_id")

    if missing:
        return {"success": False, "error": f"필수 필드가 누락되었습니다: {', '.join(missing)}"}

    try:
        # 이미지 파일을 Base64로 변환
        wedding_image_bytes = await wedding_image.read()
        wedding_image_base64 = base64.b64encode(wedding_image_bytes).decode('utf-8')

        style_image_bytes = await style_image.read()
        style_image_base64 = base64.b64encode(style_image_bytes).decode('utf-8')

        # 나노바나나 API 호출
        result = generate_invitation_with_nanobanana(
            # STEP 1
            groom_name=groom_name,
            bride_name=bride_name,
            groom_father=groom_father,
            groom_mother=groom_mother,
            bride_father=bride_father,
            bride_mother=bride_mother,
            venue=venue,
            venue_address=address,
            wedding_date=wedding_date,
            wedding_time=wedding_time,
            venue_latitude=latitude or 37.5665,
            venue_longitude=longitude or 126.9780,
            # STEP 2
            wedding_image_base64=wedding_image_base64,
            # STEP 3
            tone=tone,
            # STEP 4
            style_image_base64=style_image_base64,
            border_design_id=border_design_id,
        )

        return {"success": True, "data": result}

    except Exception as e:
        import traceback
        print(f"❌ Error during generation: {e}")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
