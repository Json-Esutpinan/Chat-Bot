from app.domain.interface.ICacheRepository import ICacheRepository
from infrastructure.RedisSingleton import RedisSingleton

class RedisRepository(ICacheRepository):
    def __init__(self):
        self.redis_client = RedisSingleton().get_client()
        super().__init__()
        
    def hget(self, key, field):
        return self.redis_client.hget(key, field)
    
    def hset(self, key, field, value):
        self.redis_client.hset(key, field, value)
    
    def delete(self, key):
        self.redis_client.delete(key)
    
    def rpush(self, key, value):
        return self.redis_client.rpush(key, value)
    
    def lrange(self, key, start, end):
        return self.redis_client.lrange(key, start, end)