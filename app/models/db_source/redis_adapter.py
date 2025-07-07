import json
import logging
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import REDIS_URL


class AsyncRedisAdapter:
    def __init__(self, decode_responses: bool = True):
        self.redis = redis.Redis.from_url(REDIS_URL, decode_responses=decode_responses)
        self.logger = logging.getLogger(__name__)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            self.logger.exception(f"Redis SET error: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            value = await self.redis.get(key)
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            self.logger.exception(f"Redis GET error: {e}")
            return None

    async def delete(self, key: str) -> bool:
        try:
            return await self.redis.delete(key) > 0
        except Exception as e:
            self.logger.exception(f"Redis DELETE error: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            return await self.redis.exists(key) == 1
        except Exception as e:
            self.logger.exception(f"Redis EXISTS error: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            self.logger.exception(f"Redis EXPIRE error: {e}")
            return False

    async def close(self):
        await self.redis.close()


redis_adapter = AsyncRedisAdapter()
