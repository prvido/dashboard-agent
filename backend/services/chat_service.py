"""
Chat and dataset service layer.
This module handles:
- Chat message processing
- Dataset file handling
- Chat history storage and retrieval
- Real-time chat updates
- Dataset validation and processing logic
- Chat session management
- Integration with OpenAI for chat responses
"""

from datetime import datetime, UTC
import uuid
from typing import Optional, Dict, List
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def get_user_chats(self, user_id: str) -> List[Dict]:
        """Get all chats for a user."""
        response = self.supabase.table("user_chats") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .execute()
        
        if not response.data:
            return []
            
        return response.data

    def get_chat(self, user_id: str, chat_id: str) -> Optional[Dict]:
        """Get a specific chat by ID."""
        response = self.supabase.table("user_chats") \
            .select("*") \
            .eq("id", chat_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()
            
        if not response or not response.data:
            raise ValueError(f"Chat with ID {chat_id} not found or does not belong to user {user_id}")
            
        return response.data

    def create_chat(self, user_id: str, title: str = "New Chat", metadata: Optional[dict] = None) -> Dict:
        """Create a new chat session."""
        chat_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        
        chat_data = {
            'id': chat_id,
            'created_at': now,
            'user_id': user_id,
            'title': title,
            'metadata': metadata or {},
            'is_deleted': False
        }
        
        response = self.supabase.table('user_chats').insert(chat_data).execute()
        
        if not response or not response.data:
            raise ValueError("Failed to create chat")
            
        return response.data[0]

    def update_chat(self, user_id: str, chat_id: str, title: Optional[str] = None, metadata: Optional[dict] = None) -> Dict:
        """Update an existing chat."""
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if metadata is not None:
            update_data['metadata'] = metadata
            
        if not update_data:
            raise ValueError("No update data provided")
            
        response = self.supabase.table('user_chats') \
            .update(update_data) \
            .eq('id', chat_id) \
            .eq('user_id', user_id) \
            .eq('is_deleted', False) \
            .execute()
            
        if not response.data:
            raise ValueError(f"Chat with ID {chat_id} not found or does not belong to user {user_id}")
            
        return response.data[0]

    def delete_chat(self, user_id: str, chat_id: str) -> None:
        """Soft delete a chat."""
        response = self.supabase.table('user_chats') \
            .update({'is_deleted': True}) \
            .eq('id', chat_id) \
            .eq('user_id', user_id) \
            .eq('is_deleted', False) \
            .execute()
            
        if not response or not response.data:
            raise ValueError(f"Chat with ID {chat_id} not found or does not belong to user {user_id}")

    def save_message(self, chat_id:str, user_id:str, agent_id:str, sender:str, payload: dict, metadata: dict) -> Dict:
        message_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        
        message_data = {
            'id': message_id,
            'created_at': now,
            'updated_at': now,
            'chat_id': chat_id,
            'user_id': user_id,
            'sender': sender,
            'payload': payload or {},
            'metadata': metadata or {},
            'agent_id': agent_id,
            'is_deleted': False
        }
        
        response = self.supabase.table('chat_messages').insert(message_data).execute()
        
        if not response or not response.data:
            raise ValueError("Failed to save message")
            
        return response.data[0]

    def get_chat_messages(self, chat_id: str, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        # First verify the chat exists and belongs to the user
        self.get_chat(user_id, chat_id)
        
        descending = limit is not None

        query = self.supabase.table("chat_messages") \
            .select("*") \
            .eq("chat_id", chat_id) \
            .eq("is_deleted", False) \
            .order("created_at", desc=descending)
            
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        
        if not response or not response.data:
            return []
            
        # If we limited, reverse to get chronological order
        messages = response.data
        if descending:
            messages = list(reversed(messages))
            
        return messages

