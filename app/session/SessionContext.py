from StateManager import StateManager
from ChatLogManager import ChatLogManager

class SessionContext:
    def __init__(self, session_key: str, state_manager: StateManager, chat_log: ChatLogManager):
        self.key = session_key
        self.state = state_manager
        self.session = chat_log

    def advance_state(self):
        return self.state.advance()

    def add_message(self, message: str, message_type: str = "text"):
        self.session.add_message(self.key,message, message_type)

    def get_messages(self):
        return self.session.get_messages(self.key)

    def get_state(self):
        return self.state.get_state(self.key)
    
    def set_state(self, state):
        self.state.set_state(state, self.key)

    def clear(self):
        self.state.clear_state(self.key)
        self.session.clear_log(self.key)
