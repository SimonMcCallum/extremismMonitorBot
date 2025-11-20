"""
Redis cache utilities for Discord bot.
"""
import json
from typing import Any, Optional
import redis.asyncio as redis

from config import settings
from utils.logger import log


class CacheManager:
    """Manages Redis cache operations."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection."""
        try:
            self.redis = await redis.from_url(
                settings.redis_url,
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.redis.ping()
            log.info("Redis connection established")
        except Exception as e:
            log.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            log.info("Redis connection closed")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis:
            return None

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            log.warning(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not self.redis:
            return False

        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            log.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis:
            return False

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            log.warning(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis:
            return False

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            log.warning(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        if not self.redis:
            return None

        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            log.warning(f"Cache increment error for key {key}: {e}")
            return None


# Global cache manager instance
cache = CacheManager()
