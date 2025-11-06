"""
Health Check Router
Handles service health monitoring endpoints
"""
from fastapi import APIRouter
import logging

from app.schemas import HealthCheck
from app.services.cache_service import cache_service
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        HealthCheck: Service health status including Redis, Memcached, and Database connectivity
    """
    redis_ok, memcached_ok = cache_service.health_check()
    database_ok = await db_service.health_check()
    
    overall_status = "healthy" if (redis_ok and memcached_ok and database_ok) else "degraded"
    
    return HealthCheck(
        status=overall_status,
        redis_connected=redis_ok,
        memcached_connected=memcached_ok,
        database_connected=database_ok
    )
