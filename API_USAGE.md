# API Usage Guide

## Overview

This document provides detailed examples of how to use the AI Response Caching POC API.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required (POC). Can be added later.

---

## Endpoints

### 1. POST `/api/v1/predict`

Main prediction endpoint supporting multiple AI tasks.

#### Text Tasks

##### Summarization

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "summarization",
    "input": "Artificial intelligence (AI) is transforming industries worldwide. From healthcare diagnostics to financial fraud detection, AI systems are improving efficiency and accuracy. Machine learning models can process vast amounts of data to identify patterns and make predictions that would be impossible for humans to achieve manually.",
    "params": {
      "max_length": 50
    }
  }'
```

Response:
```json
{
  "output": {
    "summary": "AI is transforming industries with applications in healthcare and finance...",
    "original_length": 287,
    "summary_length": 78
  },
  "cache_source": "model",
  "response_time_ms": 1245.5,
  "model_name": "llama3-8b-8192",
  "task_type": "summarization"
}
```

##### Sentiment Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "sentiment",
    "input": "This product is amazing! I love it so much!"
  }'
```

Response:
```json
{
  "output": {
    "sentiment": "positive",
    "text": "This product is amazing! I love it so much!"
  },
  "cache_source": "redis",
  "response_time_ms": 8.2,
  "model_name": "llama3-8b-8192",
  "task_type": "sentiment"
}
```

##### Translation

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "translation",
    "input": "Hello, how are you?",
    "params": {
      "target_language": "Spanish"
    }
  }'
```

##### Chat

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "chat",
    "input": "What is the capital of France?"
  }'
```

##### Question Answering

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "qa",
    "input": "What year did World War II end?",
    "params": {
      "context": "World War II ended in 1945 after the surrender of Germany and Japan."
    }
  }'
```

#### Image Tasks

##### Image Classification

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "image_classification",
    "input": "https://example.com/dog.jpg",
    "params": {
      "top_k": 5
    }
  }'
```

Response:
```json
{
  "output": {
    "predictions": [
      {"label": "golden retriever", "score": 0.92},
      {"label": "labrador", "score": 0.05},
      {"label": "dog", "score": 0.02}
    ],
    "model": "google/vit-base-patch16-224"
  },
  "cache_source": "memcached",
  "response_time_ms": 3.1,
  "model_name": "google/vit-base-patch16-224",
  "task_type": "image_classification"
}
```

##### Image Captioning

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "image_captioning",
    "input": "https://huggingface.co/datasets/mishig/sample_images/resolve/main/cat-5.jpg"
  }'
```

Response:
```json
{
  "output": {
    "caption": "a cat sitting on a table with a laptop",
    "model": "Salesforce/blip-image-captioning-large"
  },
  "cache_source": "model",
  "response_time_ms": 2150.8,
  "model_name": "Salesforce/blip-image-captioning-large",
  "task_type": "image_captioning"
}
```

---

### 2. GET `/api/v1/health`

Check service health.

```bash
curl http://localhost:8000/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "memcached_connected": true,
  "database_connected": true,
  "timestamp": "2025-11-03T10:30:00.000Z"
}
```

---

### 3. GET `/api/v1/statistics`

Get cache performance statistics.

```bash
curl "http://localhost:8000/api/v1/statistics?days=7"
```

Response:
```json
{
  "total_requests": 1250,
  "cache_hits": 875,
  "cache_misses": 375,
  "memcached_hits": 650,
  "redis_hits": 225,
  "average_response_time_ms": 42.5,
  "cache_hit_rate": 70.0,
  "time_period": "last_7_days"
}
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Summarization
response = requests.post(
    f"{BASE_URL}/api/v1/predict",
    json={
        "task_type": "summarization",
        "input": "Long text here...",
        "params": {"max_length": 50}
    }
)
result = response.json()
print(result["output"]["summary"])

# Image Captioning
response = requests.post(
    f"{BASE_URL}/api/v1/predict",
    json={
        "task_type": "image_captioning",
        "input": "https://example.com/image.jpg"
    }
)
result = response.json()
print(result["output"]["caption"])
```

---

## JavaScript Client Example

```javascript
const BASE_URL = "http://localhost:8000";

// Summarization
async function summarize(text) {
  const response = await fetch(`${BASE_URL}/api/v1/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      task_type: 'summarization',
      input: text,
      params: { max_length: 50 }
    })
  });
  
  const result = await response.json();
  return result.output.summary;
}

// Usage
summarize("Long text here...").then(summary => {
  console.log(summary);
});
```

---

## Cache Behavior

### First Request (Cache Miss)
```
Request → Cache Check → Cache Miss → AI Model → Store in Cache → Response
Time: ~1000-2000ms (model processing)
```

### Second Request (Cache Hit - Memcached)
```
Request → Memcached Hit → Response
Time: ~1-5ms (super fast!)
```

### After 5 minutes (Memcached expired, Redis hit)
```
Request → Memcached Miss → Redis Hit → Promote to Memcached → Response
Time: ~5-15ms (still fast)
```

### After 1 hour (Both caches expired)
```
Request → Cache Miss → AI Model → Store in Cache → Response
Time: ~1000-2000ms (model processing again)
```

---

## Error Handling

### 400 Bad Request
```json
{
  "detail": "task_type and input are required"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: GROQ_API_KEY not configured"
}
```

---

## Tips for Best Performance

1. **Identical Requests**: Exact same input + params will hit cache
2. **Batch Similar Requests**: Group similar tasks together
3. **Monitor Statistics**: Use `/statistics` endpoint to track cache hit rate
4. **Tune TTLs**: Adjust `REDIS_TTL` and `MEMCACHE_TTL` in `.env` based on your use case

---

## Support

For issues or questions, please open an issue on GitHub.
