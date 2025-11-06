# AI Response Caching POC with Streamlit UI

A production-ready AI response caching system with **two-layer caching** (Memcached + Redis) and **user-friendly Streamlit interface**. Achieves 250-600× performance improvement through intelligent caching.

## ✨ Features

### 🎨 **NEW: Streamlit UI**
- **Interactive Dashboard**: Real-time system health monitoring
- **Text Processing**: Summarization, Chat, Sentiment Analysis, Translation
- **Image Processing**: Captioning & Classification with upload support
- **Analytics Dashboard**: Visual statistics and performance metrics
- **Settings Panel**: System configuration and health checks

### ⚡ **Two-Layer Caching Architecture**
  - **L1 Cache (Memcached)**: Ultra-fast, short-lived cache (2ms, 5 min TTL)
  - **L2 Cache (Redis)**: Fast, longer-lived cache (12ms, 1 hour TTL)
  - **Performance**: 250-600× faster than direct AI model calls
  - Automatic cache promotion from Redis → Memcached

### 🤖 **AI Task Support**
  - **Text Tasks** (via Groq API): Summarization, Sentiment, Translation, Chat/Q&A
  - **Image Tasks** (via Groq Vision): Image classification, Image captioning (Llama 4 Scout)

### 📊 **Database Logging**
  - All requests/responses logged to PostgreSQL with JSONB columns
  - Indexed for efficient querying
  - Supports both Neon DB (cloud) and local PostgreSQL

## 🚀 Quick Start

### Option 1: Launch Everything (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Start Docker services
docker-compose up -d

# Launch both FastAPI + Streamlit UI
start_all.bat
```

**Access:**
- 🎨 **Streamlit UI**: http://localhost:8501
- 📚 **API Docs**: http://127.0.0.1:8000/docs
- 🏥 **Health Check**: http://127.0.0.1:8000/health

### Option 2: Start Manually

```bash
# Terminal 1 - FastAPI Backend
python -m uvicorn app.main:app --reload

# Terminal 2 - Streamlit UI
streamlit run ui/app.py
```

## 🎯 Using the Streamlit UI

### 1. Configure Environment

**⚠️ IMPORTANT: Never commit your `.env` file to Git!**

Copy the example file and add your API keys:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your actual API keys
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_neon_db_connection_string
```

**Get your API keys:**
- Groq API: https://console.groq.com/keys
- Neon DB: https://console.neon.tech/

### 2. Demo: See Caching in Action

**Try Summarization:**
1. Open UI at http://localhost:8501
2. Go to "📝 Text Processing"
3. Select "Summarization"
4. Paste a long article
5. Click "🚀 Summarize" - **First request**: ~1200ms (Model)
6. Click again with same text - **Second request**: ~2ms (Memcached) **600× faster!** 🎉

**Try Image Classification:**
1. Go to "🖼️ Image Processing"
2. Upload an image
3. Click "🚀 Process" - **First**: ~1500ms
4. Upload same image - **Second**: ~5ms **300× faster!** 🚀

## 📁 Project Structure

```
AI-Response-Caching-/
├── app/                    # FastAPI backend
│   ├── main.py            # Application entry
│   ├── routers/           # API endpoints
│   │   ├── text.py        # Text processing
│   │   ├── image.py       # Image processing
│   │   └── statistics.py  # Analytics
│   └── services/          # Business logic
│       ├── ai_service.py
│       ├── groq_vision_service.py
│       └── cache_service.py
├── ui/                    # 🎨 Streamlit UI (NEW!)
│   ├── app.py            # Main UI application
│   └── pages/            # UI pages
│       ├── home.py
│       ├── text_processing.py
│       ├── image_processing.py
│       ├── statistics.py
│       └── settings.py
├── start_all.bat         # Launch everything
├── UI_GUIDE.md           # Detailed UI documentation
└── requirements.txt      # All dependencies
```

## 📖 API Examples (CLI)

**Using curl:**

**Summarization:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/text/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "max_length": 150}'
```

**Image Captioning:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/image/caption" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

**Statistics:**
```bash
curl http://127.0.0.1:8000/api/v1/statistics
```

**Or just use the Streamlit UI!** Much easier and more visual! 🎨

## 🎨 UI Features

### Home Dashboard
- System health status (API, Redis, Memcached, Database)
- Quick start guide
- Performance metrics overview

### Text Processing
- **Summarization**: Adjustable length, real-time compression ratio
- **Chat**: Conversation history, cache indicators
- **Sentiment**: Visual emotion detection
- **Translation**: 10+ languages supported

### Image Processing
- **Caption Generation**: Descriptive image analysis
- **Classification**: Top-5 predictions with confidence scores
- **Upload or URL**: Flexible image input
- **Preview**: See your image before processing

### Statistics
- Cache hit/miss pie charts
- Response time comparisons
- Task distribution graphs
- Recent activity table

### Settings
- System health checks
- Configuration overview
- API documentation links

## 📚 Documentation

- **UI Guide**: See `UI_GUIDE.md` for detailed UI documentation
- **API Docs**: http://127.0.0.1:8000/docs
- **Setup Guide**: See `SETUP_GUIDE.md`

## 🔧 Configuration

All settings in `.env` file:
- `GROQ_API_KEY`: Groq API key (required)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection (default: redis://localhost:6379/0)
- `MEMCACHE_HOST`: Memcached host (default: localhost)
- `MEMCACHE_PORT`: Memcached port (default: 11211)

## 🐛 Troubleshooting

**UI shows "Connection Error":**
- Ensure FastAPI is running: http://127.0.0.1:8000/health
- Check Docker services: `docker ps`

**"Cache Not Connected":**
```bash
docker-compose restart redis memcached
```

**Streamlit won't start:**
```bash
pip install --upgrade streamlit plotly pandas
streamlit run ui/app.py
```

## 🎉 Success Metrics

With proper caching, you'll see:
- ⚡ **Memcached hits**: ~2ms (600× faster)
- 🚀 **Redis hits**: ~12ms (100× faster)
- 💰 **Cost savings**: Only pay for cache misses
- 📊 **Hit rates**: Typically 70-90% after warmup

## 🛠️ Built With

- **Backend**: FastAPI 0.104+
- **UI**: Streamlit 1.28+
- **Caching**: Redis 7, Memcached 1.6
- **Database**: PostgreSQL (Neon DB)
- **AI**: Groq API (Text + Vision)
- **Visualization**: Plotly, Pandas

## 📖 Additional Resources

- [Groq API Docs](https://console.groq.com/docs)
- [Streamlit Docs](https://docs.streamlit.io)
- [FastAPI Docs](https://fastapi.tiangolo.com)

Built with ❤️ for demonstrating intelligent AI response caching
