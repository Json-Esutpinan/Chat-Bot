from app.domain.interface.ICacheRepository import ICacheRepository
from app.infrastructure.Redis.RedisSingleton import RedisSingleton

class RedisRepository(ICacheRepository):
    def __init__(self):
        self.redis_client = RedisSingleton().get_client()
        super().__init__()
        
    async def hget(self, key, field):
        return await self.redis_client.hget(key, field)
    
    async def hset(self, key, field, value):
        await self.redis_client.hset(key, field, value)
    
    async def delete(self, key):
        await self.redis_client.delete(key)
    
    async def rpush(self, key, value):
        return await self.redis_client.rpush(key, value)
    
    async def lrange(self, key, start, end):
        return await self.redis_client.lrange(key, start, end)