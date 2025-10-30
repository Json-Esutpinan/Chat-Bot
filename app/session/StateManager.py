from typing import Optional
from State import State
from app.domain.interface.ICacheRepository import ICacheRepository

TRANSITIONS = {
    State.START:            State.WAIT_CONFIRMATION,
    State.WAIT_CONFIRMATION:State.WAIT_DESCRIPTION,
    State.WAIT_DESCRIPTION: State.WAIT_LOCATION,
    State.WAIT_LOCATION:    State.WAIT_PHOTO,
    State.WAIT_PHOTO:       State.COMPLETED,
}

class StateManager:
    def __init__(self, cache_repo: ICacheRepository):
        self.redis = cache_repo

    def get_state(self, key) -> State:
        raw = self.redis.hget(key, "state")
        return State[raw] if raw else State.START

    def set_state(self, state: State, key) -> None:
        self.redis.hset(key, "state", state.name)
    
    def clear_state(self, key) -> None:
        self.redis.delete(key)

    def advance(self, key) -> Optional[State]:
        curr = self.get_state()
        nxt  = TRANSITIONS.get(curr)
        if nxt:
            self.set_state(nxt)
            return nxt
        self.redis.delete(key)
        self.redis.delete(f"{key}:messages")
        return None