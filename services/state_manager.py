
# This is a simple in-memory state manager to track conversation history
# and user context for each session. In a production system, this would be
# backed by a persistent store like Redis or PostgreSQL.

import logging
from typing import Dict, List
from collections import defaultdict

from schemas.tool_schemas import UserInfo, ChatMessage

logger = logging.getLogger(__name__)

class SessionState:
    """Holds the state for a single user session."""
    def __init__(self, user_info: UserInfo):
        self.user_info = user_info
        self.chat_history: List[ChatMessage] = []

class StateManager:
    """Manages conversation state for multiple user sessions."""
    def __init__(self):
        self.sessions: Dict[str, SessionState] = defaultdict(lambda: None)
        logger.info("In-memory StateManager initialized.")

    def get_state(self, session_id: str) -> SessionState | None:
        """Retrieves the state for a given session."""
        return self.sessions.get(session_id)

    def update_state(self, session_id: str, user_info: UserInfo, chat_history: List[ChatMessage]):
        """Creates or updates a session's state."""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(user_info)
            logger.info(f"New session created for user: {session_id}")
        else:
            self.sessions[session_id].user_info = user_info

        self.sessions[session_id].chat_history = chat_history

    def add_assistant_message(self, session_id: str, content: str):
        """Adds a message from the assistant to the chat history."""
        if session_id in self.sessions:
            self.sessions[session_id].chat_history.append(
                ChatMessage(role="assistant", content=content)
            )
        else:
            logger.warning(f"Attempted to add message to non-existent session: {session_id}")
