import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_generate_text():
    print("\n--- Testing Gemini Text Generation ---")
    url = "http://localhost:8000/api/generate-text"
    payload = {
        "tone": "romantic",
        "groom_name": "김철수",
        "bride_name": "이영희",
        "groom_father": "김아빠",
        "groom_mother": "김엄마",
        "bride_father": "이아빠",
        "bride_mother": "이엄마",
        "venue": "서울 웨딩홀",
        "wedding_date": "2025년 5월 1일",
        "wedding_time": "오후 1시",
        "address": "서울시 강남구"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Result: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

def test_generate_invitation(model_type="nanobanana"):
    print(f"\n--- Testing Invitation Generation ({model_type}) ---")
    url = "http://localhost:8102/api/generate-invitation-test"
    
    # 더미 데이터
    files = {
        "wedding_image": ("wedding.png", b"dummy_image_data", "image/png"),
        "style_image": ("style.png", b"dummy_image_data", "image/png")
    }
    
    data = {
        "model_type": model_type,
        "tone": "romantic",
        "groom_name": "김철수",
        "bride_name": "이영희",
        "venue": "서울 웨딩홀",
        "wedding_date": "2025년 5월 1일",
        "wedding_time": "오후 1시",
        "address": "서울시 강남구",
        "border_design_id": "classic_gold"
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Success!")
                # print(f"Result: {json.dumps(result['data'], ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ Failed: {result.get('error')}")
                if "traceback" in result:
                    print(f"Traceback: {result['traceback']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Wedding OS Model API Test Script")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    # 텍스트 테스트
    # test_generate_text()
    
    # 이미지 테스트 (모델별)
    test_generate_invitation("nanobanana")
    test_generate_invitation("flash2.5")
    test_generate_invitation("gemini3.0")

