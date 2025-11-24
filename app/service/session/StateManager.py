from typing import Optional
from app.service.session.State import State
from app.domain.interface.ICacheRepository import ICacheRepository
from app.domain.interface.IStateManager import IStateManager

TRANSITIONS = {
    State.START:            State.WAIT_CONFIRMATION,
    State.WAIT_CONFIRMATION:State.WAIT_DESCRIPTION,
    State.WAIT_DESCRIPTION: State.WAIT_LOCATION,
    State.WAIT_LOCATION:    State.WAIT_PHOTO,
    State.WAIT_PHOTO:       State.COMPLETED,
}

class StateManager(IStateManager):
    key_prefix = "state"
    def __init__(self,cache_repo: ICacheRepository):
        self.redis = cache_repo

    async def get_state(self, chat_id: str) -> State:
        raw = await self.redis.hget(chat_id, "state")
        return State[raw] if raw else State.START

    async def set_state(self, chat_id:str,state: State):
        await self.redis.hset(chat_id, "state", state.name)
    
    async def clear_state(self, chat_id: str):
        await self.redis.delete(chat_id)

    async def advance(self, chat_id:str) -> Optional[State]:
        curr = await self.get_state(chat_id)
        nxt  = TRANSITIONS.get(curr)
        if nxt:
            await self.set_state(chat_id,nxt)
            return nxt
        await self.redis.delete(chat_id)
        await self.redis.delete(f"{chat_id}:messages")
        return