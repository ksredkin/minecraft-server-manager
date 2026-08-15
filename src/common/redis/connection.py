from redis.asyncio import Redis

from src.common.core.config import settings

r = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
