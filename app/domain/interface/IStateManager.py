from typing import Optional
from abc import ABC, abstractmethod
from app.service.session.State import State

class IStateManager(ABC):
    """Interface for managing state transitions in the conversation flow"""
    
    @abstractmethod
    async def get_state(self, chat_id: str) -> State:
        """Get the current state for a chat"""
        pass
    
    @abstractmethod
    async def set_state(self, chat_id: str, state: State):
        """Set the state for a chat"""
        pass
    
    @abstractmethod
    async def clear_state(self, chat_id: str):
        """Clear all state data for a chat"""
        pass
    
    @abstractmethod
    async def advance(self, chat_id: str) -> Optional[State]:
        """Advance to the next state in the flow"""
        pass
