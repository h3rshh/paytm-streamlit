#!/usr/bin/env python3
"""Quick API test for debugging"""

import requests
import json

API_BASE_URL = "http://13.232.164.205:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Health Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_image_with_sample():
    """Test image endpoint with a sample image"""
    try:
        # Create a small test image
        from PIL import Image
        import io
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        params = {"conf": 0.1}  # Very low confidence
        
        print(f"Sending test image to: {API_BASE_URL}/predict/image")
        response = requests.post(
            f"{API_BASE_URL}/predict/image",
            files=files,
            params=params,
            timeout=30
        )
        
        print(f"Image Prediction Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Image Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Image Error: {response.text}")
            
    except Exception as e:
        print(f"Image test failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 Testing API endpoints...")
    print("=" * 50)
    
    if test_health():
        print("\n✅ Health check passed")
        print("\n🖼️ Testing image endpoint...")
        test_image_with_sample()
    else:
        print("\n❌ Health check failed - API not accessible")