import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration (Postgres/Neon)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/ai_cache_db")

# Redis Configuration (L2 Cache)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))  # 1 hour

# Memcached Configuration (L1 Cache)
MEMCACHE_HOST = os.getenv("MEMCACHE_HOST", "memcached")
MEMCACHE_PORT = int(os.getenv("MEMCACHE_PORT", 11211))
MEMCACHE_TTL = int(os.getenv("MEMCACHE_TTL", 300))  # 5 minutes

# Groq API Configuration (Text AI)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# HuggingFace Configuration (Image AI)
HF_API_KEY = os.getenv("HF_API_KEY", "")
HF_IMAGE_CLASSIFICATION_MODEL = os.getenv("HF_IMAGE_CLASSIFICATION_MODEL", "google/vit-base-patch16-224-in21k")
HF_IMAGE_CAPTIONING_MODEL = os.getenv("HF_IMAGE_CAPTIONING_MODEL", "Salesforce/blip-image-captioning-base")

# Application Settings
APP_NAME = os.getenv("APP_NAME", "AI Response Caching POC")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
