"""
Quick test to check Groq API connectivity and model availability.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not found in environment")
    exit(1)

print(f"✅ GROQ_API_KEY found: {GROQ_API_KEY[:20]}...")

# Test API call
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Try with different model names
models_to_try = [
    "llama3-8b-8192",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

for model in models_to_try:
    print(f"\n🧪 Testing model: {model}")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS with {model}")
        print(f"Response: {result['choices'][0]['message']['content']}")
        break
    else:
        print(f"❌ FAILED with {model}: {response.status_code}")
        print(f"Error: {response.text}")

print("\nDone!")
