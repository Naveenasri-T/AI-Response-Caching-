# Tests

This folder contains all test scripts for the AI Response Caching application.

## Test Files

### Python Test Files
- `test_api.py` - API endpoint tests
- `test_groq.py` - Groq text processing tests
- `test_huggingface.py` - HuggingFace image processing tests

### PowerShell Test Scripts
- `test_cache.ps1` - Cache functionality tests
- `test_summarize.ps1` - Text summarization tests
- `test_summarize_improved.ps1` - Improved summarization with metrics tests
- `test_image_classification.ps1` - Image classification tests

## Running Tests

### Python Tests
```bash
# From project root
python tests/test_api.py
python tests/test_groq.py
python tests/test_huggingface.py
```

### PowerShell Tests
```powershell
# From project root
.\tests\test_cache.ps1
.\tests\test_summarize.ps1
.\tests\test_summarize_improved.ps1
.\tests\test_image_classification.ps1
```

## Prerequisites
- FastAPI application running on `http://localhost:8000`
- Docker containers (Redis, Memcached) running
- Valid API keys configured in `.env` file
