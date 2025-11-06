"""
Test Groq Vision API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.groq_vision_service import classify_image_groq, caption_image_groq
import requests

print("Testing Groq Vision API...")
print("=" * 60)

# Download test image
test_url = "https://images.unsplash.com/photo-1518791841217-8f162f1e1131"
print(f"\nDownloading test image: {test_url}")
response = requests.get(test_url, timeout=10)
image_bytes = response.content
print(f"Downloaded {len(image_bytes)} bytes")

# Test captioning
print("\n" + "=" * 60)
print("Testing Image Captioning")
print("=" * 60)
try:
    result = caption_image_groq(image_bytes)
    print("✅ Captioning successful!")
    print(f"Caption: {result['caption']}")
    print(f"Model: {result['model_used']}")
except Exception as e:
    print(f"❌ Captioning failed: {e}")

# Test classification
print("\n" + "=" * 60)
print("Testing Image Classification")
print("=" * 60)
try:
    result = classify_image_groq(image_bytes)
    print("✅ Classification successful!")
    print(f"Predictions:")
    for pred in result['predictions']:
        print(f"  - {pred['label']}: {pred['score']:.2f}")
    print(f"Model: {result['model_used']}")
except Exception as e:
    print(f"❌ Classification failed: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
