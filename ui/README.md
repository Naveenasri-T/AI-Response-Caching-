# Streamlit UI - Run Instructions

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit plotly
```

### 2. Start FastAPI Backend
```bash
python -m uvicorn app.main:app --reload
```

### 3. Start Streamlit UI
```bash
streamlit run ui/app.py
```

Or use the batch file:
```bash
start_ui.bat
```

## 📁 UI Structure

```
ui/
├── __init__.py           # Package initialization
├── app.py                # Main Streamlit application
├── utils.py              # Utility functions
└── pages/
    ├── __init__.py
    ├── home.py           # Dashboard overview
    ├── text_processing.py    # Text AI features
    ├── image_processing.py   # Image AI features
    ├── statistics.py     # Analytics & stats
    └── settings.py       # Configuration
```

## 🎯 Features

### Home Page
- System health dashboard
- Quick start guide
- Performance metrics overview

### Text Processing
- **Summarization**: Condense long texts
- **Chat**: Interactive AI conversations
- **Sentiment Analysis**: Emotion detection
- **Translation**: Multi-language support

### Image Processing
- **Captioning**: Generate image descriptions
- **Classification**: Identify objects in images
- Upload or URL input support

### Statistics
- Cache hit/miss rates
- Response time comparisons
- Task distribution charts
- Recent activity logs

### Settings
- API configuration
- Cache settings
- System health checks
- Documentation links

## 🔧 Configuration

The UI connects to:
- **API**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs

## 💡 Tips

1. **First Time Setup**: Make sure FastAPI server is running before starting UI
2. **Cache Demo**: Try the same request twice to see caching in action
3. **Performance**: Watch the response time metrics to see cache benefits
4. **Statistics**: Check the statistics page for detailed analytics

## 🐛 Troubleshooting

**UI won't connect to API:**
- Ensure FastAPI server is running
- Check that Docker services are up
- Verify API URL in settings

**Images not loading:**
- Use direct image URLs (not HTML pages)
- Ensure image is publicly accessible
- Try uploading instead of URL

**Slow responses:**
- First request is always slower (cache miss)
- Check if Redis/Memcached are running
- View statistics for performance data
