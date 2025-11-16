class RedisSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisSingleton, cls).__new__(cls)
            cls._instance.initialize(*args, **kwargs)
        return cls._instance

    def initialize(self):
        import os
        from redis.asyncio import Redis
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        db= 0
        self.redis_client = Redis(host=host, port=port, db=db, decode_responses=True)

    def get_client(self):
        return self.redis_client