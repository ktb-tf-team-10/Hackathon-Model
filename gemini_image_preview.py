"""Gemini 3 Pro Image Preview streaming example.

This wraps the official sample into a reusable helper so we can quickly
verify image generation from the command line.
"""
import argparse
import mimetypes
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.genai import types

from utils.genai_client import get_genai_client


load_dotenv()


def save_binary(path: Path, data: bytes) -> Path:
    path.write_bytes(data)
    print(f"✅ Saved: {path}")
    return path


def generate_preview(prompt: str, output_dir: Path, prefix: str = "gemini_preview") -> None:
    client = get_genai_client()
    output_dir.mkdir(parents=True, exist_ok=True)

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    ]

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
        image_config=types.ImageConfig(image_size="1K"),
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=config,
    ):
        candidates = getattr(chunk, "candidates", None)
        if not candidates:
            continue
        content = candidates[0].content
        if not content or not content.parts:
            continue
        part = content.parts[0]
        inline = getattr(part, "inline_data", None)
        if inline and inline.data:
            ext = mimetypes.guess_extension(inline.mime_type) or ".png"
            filename = output_dir / f"{prefix}_{file_index}{ext}"
            save_binary(filename, inline.data)
            file_index += 1
        elif getattr(chunk, "text", None):
            print(chunk.text)

    if file_index == 0:
        print("⚠️ No images were produced. Check the API key/quota.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini 3 Pro Image Preview demo")
    parser.add_argument(
        "prompt",
        type=str,
        nargs="?",
        default="Generate an image of a banana wearing a costume.",
        help="Text prompt for the model",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("gemini_preview_samples"),
        help="Directory to store the generated files",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="gemini_preview",
        help="Filename prefix",
    )
    args = parser.parse_args()

    try:
        generate_preview(args.prompt, args.output, args.prefix)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Generation failed: {exc}")
        sys.exit(1)
