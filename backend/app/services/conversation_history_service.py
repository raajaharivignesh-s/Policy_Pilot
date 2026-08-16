"""
Conversation History Service

This service manages server-side conversation history accumulation.
It provides methods to retrieve, append to, truncate, and initialize
conversation history for different conversation_id values.

Each conversation history is stored as a list of message dictionaries:
    {"role": "user" | "assistant", "content": str}

Requirements:
- Server accumulates history for conversation_id (Req 1.2.1)
- History is truncated to 20 entries when it exceeds limit (Req 1.2.4)
- New conversation_id gets empty history list initialized (Req 1.2.5)
"""

import threading
from typing import Dict, List


class ConversationHistoryService:
    """
    Manages server-side conversation history accumulation.

    This service provides an in-memory store for conversation histories,
    keyed by conversation_id. Each history is a list of message dictionaries
    with 'role' and 'content' fields.

    The service is thread-safe and handles concurrent access to histories.
    """

    def __init__(self):
        """Initialize the conversation history service."""
        self._history_store: Dict[str, List[Dict[str, str]]] = {}
        self._lock = threading.Lock()  # For thread-safe operations

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """
        Retrieve history for a conversation_id.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            List of message dictionaries for the conversation, or empty list
            if no history exists for this conversation_id.
        """
        with self._lock:
            return self._history_store.get(conversation_id, []).copy()

    def append_to_history(
        self,
        conversation_id: str,
        role: str,
        content: str
    ) -> None:
        """
        Append a message to the conversation history.

        If the conversation_id doesn't exist in the store, it will be
        initialized with an empty history list first.

        Args:
            conversation_id: Unique identifier for the conversation
            role: Message role - must be either "user" or "assistant"
            content: Message content as a string

        Raises:
            ValueError: If role is not "user" or "assistant"
        """
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

        if not content or not content.strip():
            raise ValueError("Content cannot be empty or whitespace only")

        with self._lock:
            # Initialize history if it doesn't exist
            if conversation_id not in self._history_store:
                self._history_store[conversation_id] = []

            # Append the new message
            self._history_store[conversation_id].append({
                "role": role,
                "content": content.strip()
            })

            # Auto-truncate if history exceeds 20 entries
            self.truncate_history(conversation_id, max_entries=20)

    def truncate_history(
        self,
        conversation_id: str,
        max_entries: int = 20
    ) -> None:
        """
        Truncate history to the most recent entries.

        If the history for this conversation_id exceeds max_entries,
        keep only the most recent max_entries entries.

        Args:
            conversation_id: Unique identifier for the conversation
            max_entries: Maximum number of entries to keep (default: 20)

        Note:
            If conversation_id doesn't exist or history has <= max_entries,
            this method does nothing.
        """
        with self._lock:
            if conversation_id not in self._history_store:
                return

            history = self._history_store[conversation_id]
            if len(history) > max_entries:
                # Keep only the most recent max_entries entries
                self._history_store[conversation_id] = history[-max_entries:]

    def initialize_history(self, conversation_id: str) -> None:
        """
        Initialize an empty history for a new conversation_id.

        If the conversation_id already exists, this method does nothing
        (does not clear existing history).

        Args:
            conversation_id: Unique identifier for the conversation
        """
        with self._lock:
            if conversation_id not in self._history_store:
                self._history_store[conversation_id] = []

    def clear_history(self, conversation_id: str) -> None:
        """
        Clear all history for a conversation_id.

        Args:
            conversation_id: Unique identifier for the conversation

        Note:
            If conversation_id doesn't exist, this method does nothing.
        """
        with self._lock:
            if conversation_id in self._history_store:
                del self._history_store[conversation_id]

    def get_conversation_ids(self) -> List[str]:
        """
        Get a list of all conversation_ids with stored history.

        Returns:
            List of conversation_id strings
        """
        with self._lock:
            return list(self._history_store.keys())

    def get_total_messages(self, conversation_id: str) -> int:
        """
        Get the total number of messages in a conversation's history.

        Args:
            conversation_id: Unique identifier for the conversation

        Returns:
            Number of messages in the history, or 0 if conversation_id
            doesn't exist.
        """
        with self._lock:
            if conversation_id not in self._history_store:
                return 0
            return len(self._history_store[conversation_id])


# Create a singleton instance of the service
conversation_history_service = ConversationHistoryService()