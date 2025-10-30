from app.domain.interface.ICacheRepository import ICacheRepository

class ChatLogManager:
    def __init__(self,cache_repo:ICacheRepository):
        self.cache = cache_repo

    def add_message(self, key,message: str, message_type: str = "text"):
        self.cache.rpush(f"{key}:messages", f"{message_type}: {message}")

    def get_messages(self, key):
        return self.cache.lrange(f"{key}:messages", 0, -1)

    def clear_log(self, key):
        self.cache.delete(key)
        self.cache.delete(f"{key}:messages")