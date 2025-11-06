"""
API Routers Package
"""
from app.routers.health import router as health_router
from app.routers.statistics import router as statistics_router
from app.routers.text import router as text_router
from app.routers.image import router as image_router
from app.routers.predict import router as predict_router

__all__ = [
    "health_router",
    "statistics_router",
    "text_router",
    "image_router",
    "predict_router"
]
