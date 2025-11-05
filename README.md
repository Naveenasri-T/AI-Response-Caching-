# AI Response Caching POC

A high-performance FastAPI backend with **two-layer caching** (Memcached + Redis) for AI model responses, supporting both **text** (via Groq) and **image** (via HuggingFace) processing tasks. All requests and responses are logged to PostgreSQL with JSONB columns for flexible querying.

## 🎯 Features

- **Two-Layer Caching Architecture**
  - **L1 Cache (Memcached)**: Ultra-fast, short-lived cache (5 min TTL) for very recent repeated requests
  - **L2 Cache (Redis)**: Fast, longer-lived cache (1 hour TTL) for active requests
  - Automatic cache promotion from Redis → Memcached for frequently accessed items

- **AI Task Support**
  - **Text Tasks** (via Groq API): Summarization, Sentiment, Translation, Chat/Q&A
  - **Image Tasks** (via HuggingFace): Image classification, Image captioning

- **Database Logging**
  - All requests/responses logged to PostgreSQL with JSONB columns
  - Indexed for efficient querying
  - Supports both Neon DB (cloud) and local PostgreSQL

## 🚀 Quick Start

### 1. Configure Environment

Edit `.env` with your API keys:

```bash
GROQ_API_KEY=your_groq_api_key_here
HF_API_KEY=your_huggingface_token_here
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

### 3. Access API

- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

## 📖 API Examples

**Summarization:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"task_type": "summarization", "input": "Long text here..."}'
```

**Image Captioning:**
```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
  -H "Content-Type: application/json" \
  -d '{"task_type": "image_captioning", "input": "https://example.com/image.jpg"}'
```

## 📊 Statistics

```bash
curl http://localhost:8000/api/v1/statistics?days=7
```

## 🔧 Configuration

See `.env` file for all configuration options.

Built with FastAPI, Redis, Memcached, PostgreSQL, Groq, and HuggingFace
