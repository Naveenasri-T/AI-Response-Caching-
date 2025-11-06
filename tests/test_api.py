"""
Test script to verify the AI Response Caching POC API.
Run this after starting the application with docker-compose.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def test_health_check():
    """Test health check endpoint."""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print_response("Health Check", response)
    return response.status_code == 200


def test_text_summarization():
    """Test text summarization task."""
    print("\n📝 Testing Text Summarization...")
    
    payload = {
        "task_type": "summarization",
        "input": "Artificial intelligence is revolutionizing industries worldwide. From healthcare to finance, AI systems are improving efficiency, accuracy, and decision-making. Machine learning models can analyze vast amounts of data to identify patterns and make predictions that would be impossible for humans to achieve manually.",
        "params": {"max_length": 50}
    }
    
    # First request (cache miss)
    start = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/predict", json=payload)
    first_time = time.time() - start
    print_response("Summarization - First Request (Cache Miss)", response)
    print(f"⏱️  Response Time: {first_time:.2f}s")
    
    # Second request (cache hit)
    time.sleep(1)
    start = time.time()
    response2 = requests.post(f"{BASE_URL}/api/v1/predict", json=payload)
    second_time = time.time() - start
    print_response("Summarization - Second Request (Cache Hit)", response2)
    print(f"⏱️  Response Time: {second_time:.2f}s")
    print(f"🚀 Speed Improvement: {first_time/second_time:.1f}x faster")
    
    return response.status_code == 200


def test_sentiment_analysis():
    """Test sentiment analysis task."""
    print("\n😊 Testing Sentiment Analysis...")
    
    payload = {
        "task_type": "sentiment",
        "input": "I absolutely love this product! It exceeded all my expectations and the customer service was amazing!"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/predict", json=payload)
    print_response("Sentiment Analysis", response)
    return response.status_code == 200


def test_image_captioning():
    """Test image captioning task."""
    print("\n🖼️  Testing Image Captioning...")
    
    # Using a sample image URL
    payload = {
        "task_type": "image_captioning",
        "input": "https://huggingface.co/datasets/mishig/sample_images/resolve/main/cat-5.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/predict", json=payload)
    print_response("Image Captioning", response)
    return response.status_code == 200


def test_statistics():
    """Test statistics endpoint."""
    print("\n📊 Testing Statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/statistics?days=7")
    print_response("Cache Statistics", response)
    return response.status_code == 200


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  AI Response Caching POC - API Test Suite")
    print("="*60)
    
    try:
        # Test connection
        print("\n🔌 Connecting to API...")
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ API not responding at {BASE_URL}")
            print("   Make sure the server is running: docker-compose up")
            return
        
        print("✅ API is running!")
        
        # Run tests
        results = {
            "Health Check": test_health_check(),
            "Text Summarization": test_text_summarization(),
            "Sentiment Analysis": test_sentiment_analysis(),
            "Image Captioning": test_image_captioning(),
            "Statistics": test_statistics()
        }
        
        # Print summary
        print("\n" + "="*60)
        print("  Test Summary")
        print("="*60)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{status} - {test_name}")
        
        total = len(results)
        passed = sum(results.values())
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️  Some tests failed. Check the logs above.")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("   Make sure the server is running: docker-compose up")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
