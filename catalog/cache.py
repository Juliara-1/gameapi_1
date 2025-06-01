import os
import json
from redis import Redis

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_db = int(os.getenv("REDIS_DB", 1))

class RedisCache:
    def __init__(self):
        self.redis = Redis(host=redis_host, port=redis_port, db=redis_db)

    def get(self, key):
        """Получить данные из кеша по ключу."""
        cached_result = self.redis.get(key)
        if cached_result:
            return json.loads(cached_result)
        return None

    def set(self, key, value, timeout=None):
        """Сохранить данные в кеш."""
        self.redis.set(key, json.dumps(value), ex=timeout)

    def delete(self, key):
        """Удалить данные из кеша по ключу."""
        self.redis.delete(key)