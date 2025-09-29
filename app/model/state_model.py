from enum import Enum, auto
from redis import Redis
from typing import Optional

class State(Enum):
    START             = auto()
    WAIT_CONFIRMATION = auto()
    WAIT_DESCRIPTION  = auto()
    WAIT_LOCATION     = auto()
    WAIT_PHOTO        = auto()
    COMPLETED         = auto()

TRANSITIONS = {
    State.START:            State.WAIT_CONFIRMATION,
    State.WAIT_CONFIRMATION:State.WAIT_DESCRIPTION,
    State.WAIT_DESCRIPTION: State.WAIT_LOCATION,
    State.WAIT_LOCATION:    State.WAIT_PHOTO,
    State.WAIT_PHOTO:       State.COMPLETED,
}

class SessionManager:
    def __init__(self, redis_client: Redis, session_key: str):
        self.redis = redis_client
        self.key   = session_key

    def get_state(self) -> State:
        raw = self.redis.hget(self.key, "state")
        return State[raw] if raw else State.START

    def set_state(self, state: State) -> None:
        self.redis.hset(self.key, "state", state.name)
    
    def clear_state(self) -> None:
        self.redis.delete(self.key)

    def advance(self) -> Optional[State]:
        curr = self.get_state()
        nxt  = TRANSITIONS.get(curr)
        if nxt:
            self.set_state(nxt)
            return nxt
        self.redis.delete(self.key)
        return None
