#!/usr/bin/env python3
"""
설치 확인 스크립트

uv venv로 설치한 패키지들이 정상적으로 작동하는지 확인합니다.
"""

import sys
import os


def check_python_version():
    """Python 버전 확인"""
    version = sys.version.split()[0]
    major, minor = map(int, version.split('.')[:2])

    print(f"✅ Python {version}")

    if major == 3 and minor == 10:
        print("   ✅ Python 3.10.x (정상)")
    else:
        print(f"   ⚠️  Python 3.10.x 권장 (현재: {version})")

    return True


def check_packages():
    """필수 패키지 확인"""
    packages = {
        'google.genai': 'Gemini API',
        'google.cloud.aiplatform': 'Google Cloud AI Platform',
        'boto3': 'AWS S3',
        'PIL': 'Pillow (이미지 처리)',
        'requests': 'HTTP 요청',
        'dotenv': 'python-dotenv',
        'jinja2': 'Jinja2 (템플릿 엔진)',
        'certifi': 'SSL 인증서',
    }

    print("\n📦 패키지 확인:")
    all_ok = True

    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"   ✅ {desc}")
        except ImportError as e:
            print(f"   ❌ {desc}: {e}")
            all_ok = False

    return all_ok


def check_prompt_files():
    """프롬프트 파일 존재 확인"""
    base_path = os.path.dirname(__file__)

    files = [
        "prompts/invitation/system.md",
        "prompts/invitation/text_generate.md",
        "prompts/invitation/text_schema.json",
        "prompts/nanobanana/system.md",
        "prompts/nanobanana/page1_cover.md",
        "prompts/nanobanana/page2_content.md",
        "prompts/nanobanana/page3_location.md",
        "utils/prompt_loader.py",
    ]

    print("\n📄 프롬프트 파일 확인:")
    all_ok = True

    for file in files:
        path = os.path.join(base_path, file)
        if os.path.exists(path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (없음)")
            all_ok = False

    return all_ok


def check_prompt_loader():
    """프롬프트 로더 동작 확인"""
    print("\n🔧 프롬프트 로더 테스트:")

    try:
        from utils.prompt_loader import PromptLoader, GeminiPromptBuilder

        loader = PromptLoader()
        print("   ✅ PromptLoader 임포트 성공")

        # 간단한 로드 테스트
        prompt = loader.load_prompt(
            "invitation/system.md"
        )
        print("   ✅ 프롬프트 파일 로드 성공")

        schema = loader.load_schema("invitation/text_schema.json")
        print("   ✅ JSON 스키마 로드 성공")

        builder = GeminiPromptBuilder()
        print("   ✅ GeminiPromptBuilder 생성 성공")

        return True

    except Exception as e:
        print(f"   ❌ 프롬프트 로더 에러: {e}")
        return False


def check_env_file():
    """환경 변수 파일 확인"""
    print("\n🔑 환경 변수 파일 확인:")

    base_path = os.path.dirname(__file__)
    env_path = os.path.join(base_path, ".env")

    if os.path.exists(env_path):
        print(f"   ✅ .env 파일 존재")

        # API 키 확인 (값은 표시하지 않음)
        with open(env_path, 'r') as f:
            content = f.read()

        keys = ['GEMINI_API_KEY', 'HUGGINGFACE_API_KEY', 'HF_TOKEN']
        for key in keys:
            if key in content and not content.split(key)[1].split('\n')[0].strip().endswith('...'):
                print(f"   ✅ {key} 설정됨")
            else:
                print(f"   ⚠️  {key} 미설정 또는 기본값")

        return True
    else:
        print(f"   ❌ .env 파일 없음")
        print("      .env.example을 복사하여 .env 생성 필요")
        return False


def main():
    """메인 체크 함수"""
    print("=" * 60)
    print("🔍 Wedding OS - Model Server 설치 확인")
    print("=" * 60)

    results = []

    results.append(("Python 버전", check_python_version()))
    results.append(("필수 패키지", check_packages()))
    results.append(("프롬프트 파일", check_prompt_files()))
    results.append(("프롬프트 로더", check_prompt_loader()))
    results.append(("환경 변수", check_env_file()))

    print("\n" + "=" * 60)
    print("📊 결과 요약")
    print("=" * 60)

    all_passed = True
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"   {name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print("🎉 모든 확인 완료! 서버를 시작할 수 있습니다.")
        print("\n다음 단계:")
        print("  1. .env 파일에 실제 API 키 입력")
        print("  2. FastAPI 서버 실행")
        print("  3. python gemini_text_api.py (테스트)")
        return 0
    else:
        print("⚠️  일부 항목에 문제가 있습니다. 위 내용을 확인하세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
