"""
Google Imagen 4.0 기본 프롬프트 테스트 스크립트

Gemini/Imagen API 키가 .env (GEMINI_API_KEY) 에 설정되어 있어야 합니다.
"""

from pathlib import Path

from dotenv import load_dotenv
from google.genai import types

from utils.genai_client import get_genai_client


load_dotenv()


def build_base_prompt() -> str:
    """웨딩 초대장 기본 프롬프트 생성"""
    return """
Design a luxurious Korean wedding invitation set composed of three portrait pages (aspect ratio 3:4).

Page 1 (cover):
- Soft ivory background with watercolor floral frame in dusty pink and champagne gold
- Place the couple's initials "Y & J" in the center with serif lettering
- Add a gentle ribbon motif and subtle bokeh lighting

Page 2 (greeting):
- Keep the same border/frame as the cover
- Typeset the sample greeting text in elegant Korean calligraphy:
  "서로의 마음을 모아 하나가 되는 자리에 조심스레 초대합니다."
- Leave enough whitespace so the text feels airy and premium

Page 3 (venue information):
- Maintain the same color palette
- Add a clean layout with small icons for date, time, and venue
- Include sample details:
  Date: 2025년 5월 24일 토요일 오후 2시
  Venue: 서울 더 클래식 500 컨벤션홀
- Finish with a delicate footer line saying "with love"

General guidelines:
- Use modern Korean luxury wedding aesthetics
- Keep typography legible, mix of serif titles and sans-serif body text
- Avoid caricatures or overly cartoonish elements
""".strip()


def main():
    client = get_genai_client()
    prompt = build_base_prompt()

    print("📤 Imagen 4.0 기본 프롬프트 테스트 호출 중...")
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=2,
            aspect_ratio="3:4",
            person_generation="dont_allow",
        ),
    )

    output_dir = Path("imagen_samples")
    output_dir.mkdir(exist_ok=True)

    for idx, generated_image in enumerate(response.generated_images, start=1):
        path = output_dir / f"imagen_sample_{idx}.png"
        generated_image.image.save(path)
        print(f"✅ 이미지 저장: {path}")

    print("🎉 기본 프롬프트 호출이 완료되었습니다.")


if __name__ == "__main__":
    main()
