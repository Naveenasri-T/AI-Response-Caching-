from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.routers import (
    health_router,
    statistics_router,
    text_router,
    image_router,
    predict_router
)
from app.services.db_service import db_service
from app.core.config import APP_NAME, DEBUG

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Trigger reload - cache services now available


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {APP_NAME}...")
    
    try:
        # Initialize database tables
        await db_service.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {APP_NAME}...")
    await db_service.close()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description="AI Response Caching POC with two-layer caching (Memcached + Redis) and Postgres logging",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(predict_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(statistics_router, prefix="/api/v1")
app.include_router(text_router, prefix="/api/v1")
app.include_router(image_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "app": APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "predict": "/api/v1/predict",
            "health": "/api/v1/health",
            "statistics": "/api/v1/statistics",
            "text": {
                "summarize": "/api/v1/text/summarize",
                "sentiment": "/api/v1/text/sentiment",
                "translate": "/api/v1/text/translate",
                "chat": "/api/v1/text/chat"
            },
            "image": {
                "caption": "/api/v1/image/caption",
                "caption_upload": "/api/v1/image/upload/caption",
                "classify": "/api/v1/image/classify",
                "classify_upload": "/api/v1/image/upload/classify"
            },
            "docs": "/docs"
        }
    }


@app.get("/ping", tags=["Health"])
async def ping():
    """
    Simple ping endpoint.
    """
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
