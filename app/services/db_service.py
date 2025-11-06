import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.config import DATABASE_URL
from app.models import Base, RequestLog

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Handles all database operations with async support.
    """
    
    def __init__(self):
        # Create async engine
        self.engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        # Create async session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """
        Initialize database tables.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def log_request(
        self,
        task_type: str,
        operation: Optional[str],
        model_name: str,
        input_json: Dict[str, Any],
        output_json: Dict[str, Any],
        cache_used: bool,
        cache_source: Optional[str],
        cache_key: Optional[str],
        response_time_ms: float
    ) -> int:
        """
        Log a request/response to the database.
        Returns the log ID.
        """
        async with self.async_session() as session:
            try:
                log = RequestLog(
                    task_type=task_type,
                    operation=operation,
                    model_name=model_name,
                    input_json=input_json,
                    output_json=output_json,
                    cache_used=cache_used,
                    cache_source=cache_source,
                    cache_key=cache_key,
                    response_time_ms=response_time_ms
                )
                
                session.add(log)
                await session.commit()
                await session.refresh(log)
                
                logger.debug(f"Logged request {log.id} to database")
                return log.id
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to log request to database: {e}")
                raise
    
    async def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get cache statistics for the last N days.
        """
        async with self.async_session() as session:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                # Total requests
                total_query = select(func.count(RequestLog.id)).where(
                    RequestLog.created_at >= cutoff_date
                )
                total_result = await session.execute(total_query)
                total_requests = total_result.scalar() or 0
                
                # Cache hits
                cache_query = select(func.count(RequestLog.id)).where(
                    RequestLog.created_at >= cutoff_date,
                    RequestLog.cache_used == True
                )
                cache_result = await session.execute(cache_query)
                cache_hits = cache_result.scalar() or 0
                
                # Memcached hits
                memcached_query = select(func.count(RequestLog.id)).where(
                    RequestLog.created_at >= cutoff_date,
                    RequestLog.cache_source == "memcached"
                )
                memcached_result = await session.execute(memcached_query)
                memcached_hits = memcached_result.scalar() or 0
                
                # Redis hits
                redis_query = select(func.count(RequestLog.id)).where(
                    RequestLog.created_at >= cutoff_date,
                    RequestLog.cache_source == "redis"
                )
                redis_result = await session.execute(redis_query)
                redis_hits = redis_result.scalar() or 0
                
                # Average response time
                avg_time_query = select(func.avg(RequestLog.response_time_ms)).where(
                    RequestLog.created_at >= cutoff_date
                )
                avg_time_result = await session.execute(avg_time_query)
                avg_response_time = float(avg_time_result.scalar() or 0)
                
                # Calculate cache hit rate
                cache_hit_rate = (cache_hits / total_requests * 100) if total_requests > 0 else 0
                cache_misses = total_requests - cache_hits
                
                return {
                    "total_requests": total_requests,
                    "cache_hits": cache_hits,
                    "cache_misses": cache_misses,
                    "memcached_hits": memcached_hits,
                    "redis_hits": redis_hits,
                    "average_response_time_ms": round(avg_response_time, 2),
                    "cache_hit_rate": round(cache_hit_rate, 2),
                    "time_period_days": days
                }
                
            except Exception as e:
                logger.error(f"Failed to get statistics: {e}")
                raise
    
    async def health_check(self) -> bool:
        """
        Check if database is connected and responsive.
        """
        try:
            async with self.async_session() as session:
                result = await session.execute(select(1))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def close(self):
        """
        Close database connections.
        """
        await self.engine.dispose()
        logger.info("Database connections closed")


# Global database service instance
db_service = DatabaseService()
