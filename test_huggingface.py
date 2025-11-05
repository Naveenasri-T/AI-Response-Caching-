"""
Test HuggingFace API models to see which ones work with your token.
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

# Test models
CAPTIONING_MODELS = [
    "microsoft/git-base",
    "nlpconnect/vit-gpt2-image-captioning",
    "Salesforce/blip-image-captioning-base",
    "Salesforce/blip-image-captioning-large",
]

CLASSIFICATION_MODELS = [
    "google/vit-base-patch16-224",
    "microsoft/resnet-50",
]

def test_model(model_name: str, task_type: str = "caption"):
    """Test if a model is accessible"""
    url = f"https://api-inference.huggingface.co/models/{model_name}"
    
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }
    
    # Use a tiny 1x1 pixel image for testing
    test_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    try:
        response = requests.post(url, headers=headers, data=test_image, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ {model_name} - WORKS!")
            return True
        elif response.status_code == 403:
            print(f"❌ {model_name} - 403 Forbidden (no access)")
            return False
        elif response.status_code == 503:
            print(f"⏳ {model_name} - Model is loading (might work later)")
            return False
        else:
            print(f"⚠️  {model_name} - Status {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"❌ {model_name} - Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing HuggingFace API Access...")
    print(f"API Key: {HF_API_KEY[:20]}..." if HF_API_KEY else "No API Key found!")
    print("\n" + "="*60)
    
    print("\n🖼️  TESTING IMAGE CAPTIONING MODELS:")
    print("-"*60)
    working_caption_models = []
    for model in CAPTIONING_MODELS:
        if test_model(model, "caption"):
            working_caption_models.append(model)
    
    print("\n🏷️  TESTING IMAGE CLASSIFICATION MODELS:")
    print("-"*60)
    working_class_models = []
    for model in CLASSIFICATION_MODELS:
        if test_model(model, "classification"):
            working_class_models.append(model)
    
    print("\n" + "="*60)
    print("\n📋 SUMMARY:")
    print("-"*60)
    
    if working_caption_models:
        print(f"\n✅ Working Captioning Models ({len(working_caption_models)}):")
        for model in working_caption_models:
            print(f"   - {model}")
        print(f"\n💡 Update .env with:")
        print(f"   HF_IMAGE_CAPTIONING_MODEL={working_caption_models[0]}")
    else:
        print("\n❌ No captioning models working. Your token might need permissions.")
    
    if working_class_models:
        print(f"\n✅ Working Classification Models ({len(working_class_models)}):")
        for model in working_class_models:
            print(f"   - {model}")
    else:
        print("\n❌ No classification models working.")
    
    print("\n" + "="*60)
