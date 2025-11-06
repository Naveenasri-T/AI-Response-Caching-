"""
Statistics Router
Handles cache performance and usage statistics endpoints
"""
from fastapi import APIRouter, HTTPException
import logging

from app.schemas import CacheStatistics
from app.services.db_service import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("", response_model=CacheStatistics)
async def get_statistics(days: int = 7):
    """
    Get cache performance statistics for the last N days.
    
    Args:
        days: Number of days to retrieve statistics for (default: 7)
    
    Returns:
        CacheStatistics: Cache performance metrics including hit rates and response times
    """
    try:
        stats = await db_service.get_statistics(days)
        
        return CacheStatistics(
            total_requests=stats["total_requests"],
            cache_hits=stats["cache_hits"],
            cache_misses=stats["cache_misses"],
            memcached_hits=stats["memcached_hits"],
            redis_hits=stats["redis_hits"],
            average_response_time_ms=stats["average_response_time_ms"],
            cache_hit_rate=stats["cache_hit_rate"],
            time_period=f"last_{days}_days"
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve statistics"
        )
