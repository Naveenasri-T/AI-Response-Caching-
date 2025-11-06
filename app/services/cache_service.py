import json
import hashlib
import redis
from pymemcache.client.base import Client as MemcacheClient
from typing import Optional, Tuple, Any
import logging

from app.core.config import (
    REDIS_URL, 
    MEMCACHE_HOST, 
    MEMCACHE_PORT,
    REDIS_TTL,
    MEMCACHE_TTL
)

logger = logging.getLogger(__name__)


class CacheService:
    """
    Two-layer caching system:
    - L1: Memcached (fastest, shortest TTL for very recent requests)
    - L2: Redis (fast, longer TTL for active requests)
    """
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=5)
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
        if not self.redis_client:
            logger.warning("Redis client is not available - L2 cache disabled")
        
        try:
            self.memcached_client = MemcacheClient((MEMCACHE_HOST, MEMCACHE_PORT), connect_timeout=5, timeout=5)
            logger.info("Memcached client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Memcached: {e}")
            self.memcached_client = None
        if not self.memcached_client:
            logger.warning("Memcached client is not available - L1 cache disabled")
    
    def generate_cache_key(self, task_type: str, input_data: Any, params: dict = None) -> str:
        """
        Generate a deterministic cache key based on task type, input, and parameters.
        """
        # Create a deterministic string representation
        key_parts = {
            "task_type": task_type,
            "input": input_data,
            "params": params or {}
        }
        key_string = json.dumps(key_parts, sort_keys=True, ensure_ascii=False)
        
        # Hash for consistent key length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        return f"ai_cache:{task_type}:{key_hash[:16]}"
    
    def get_from_cache(self, key: str) -> Tuple[Optional[Any], Optional[str]]:
        """
        Try to retrieve from L1 (Memcached) first, then L2 (Redis).
        Returns: (cached_value, cache_source) or (None, None)
        """
        # Try L1: Memcached (fastest)
        if self.memcached_client:
            try:
                mc_value = self.memcached_client.get(key)
                if mc_value:
                    try:
                        # Memcached returns bytes
                        decoded = mc_value.decode('utf-8') if isinstance(mc_value, bytes) else mc_value
                        result = json.loads(decoded)
                        logger.info(f"Cache HIT in Memcached for key: {key[:30]}...")
                        return result, "memcached"
                    except Exception as e:
                        logger.warning(f"Failed to decode Memcached value: {e}")
            except Exception as e:
                logger.warning(f"Memcached get error: {e}")
        else:
            logger.debug("Memcached client not configured, skipping L1 lookup")
        
        # Try L2: Redis (still fast)
        if self.redis_client:
            try:
                redis_value = self.redis_client.get(key)
                if redis_value:
                    try:
                        result = json.loads(redis_value)
                        logger.info(f"Cache HIT in Redis for key: {key[:30]}...")
                        
                        # Promote to L1 for frequent access
                        self._promote_to_memcached(key, result)
                        
                        return result, "redis"
                    except Exception as e:
                        logger.warning(f"Failed to decode Redis value: {e}")
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        else:
            logger.debug("Redis client not configured, skipping L2 lookup")
        
        logger.info(f"Cache MISS for key: {key[:30]}...")
        return None, None
    
    def set_in_cache(self, key: str, value: Any, 
                     ttl_redis: int = None, ttl_memcached: int = None):
        """
        Store value in both L1 (Memcached) and L2 (Redis) caches.
        """
        ttl_redis = ttl_redis or REDIS_TTL
        ttl_memcached = ttl_memcached or MEMCACHE_TTL
        
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            
            # Store in L1: Memcached
            if self.memcached_client:
                try:
                    self.memcached_client.set(key, serialized.encode('utf-8'), expire=ttl_memcached)
                    logger.debug(f"Cached in Memcached with TTL {ttl_memcached}s")
                except Exception as e:
                    logger.warning(f"Failed to cache in Memcached: {e}")
            else:
                logger.debug("Memcached client not configured, skipping L1 set")
            
            # Store in L2: Redis
            if self.redis_client:
                try:
                    self.redis_client.setex(key, ttl_redis, serialized)
                    logger.debug(f"Cached in Redis with TTL {ttl_redis}s")
                except Exception as e:
                    logger.warning(f"Failed to cache in Redis: {e}")
            else:
                logger.debug("Redis client not configured, skipping L2 set")
                    
        except Exception as e:
            logger.error(f"Failed to serialize cache value: {e}")
    
    def _promote_to_memcached(self, key: str, value: Any):
        """
        Promote frequently accessed Redis items to Memcached for faster access.
        """
        if self.memcached_client:
            try:
                serialized = json.dumps(value, ensure_ascii=False)
                self.memcached_client.set(key, serialized.encode('utf-8'), expire=MEMCACHE_TTL)
                logger.debug(f"Promoted to Memcached: {key[:30]}...")
            except Exception as e:
                logger.warning(f"Failed to promote to Memcached: {e}")
    
    def invalidate_cache(self, key: str):
        """
        Remove a key from both cache layers.
        """
        if self.memcached_client:
            try:
                self.memcached_client.delete(key)
            except Exception as e:
                logger.warning(f"Failed to delete from Memcached: {e}")
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Failed to delete from Redis: {e}")
    
    def health_check(self) -> Tuple[bool, bool]:
        """
        Check if Redis and Memcached are connected.
        Returns: (redis_ok, memcached_ok)
        """
        redis_ok = False
        memcached_ok = False
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                redis_ok = True
            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
        
        if self.memcached_client:
            try:
                self.memcached_client.set("health_check", b"ok", expire=10)
                memcached_ok = self.memcached_client.get("health_check") == b"ok"
            except Exception as e:
                logger.error(f"Memcached health check failed: {e}")
        
        return redis_ok, memcached_ok


# Global cache service instance
cache_service = CacheService()
