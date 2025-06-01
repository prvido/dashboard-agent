"""
Chat manager routes and endpoints.
This module handles:
- GET /chats: Returns metadata for all chat sessions created by the authenticated user.
- POST /chats: Create a new chat session
- PUT /chats/{chat_id}: Update a chat session by ID
- DELETE /chats/{chat_id}: Delete a chat session by ID
- POST /chats/{chat_id}/messages: Send a message to a chat session
- GET /chats/{chat_id}/messages: Get all messages from a chat session
"""

from flask import Blueprint, request, jsonify, Response
from services.chat_service import ChatService
from services.agent_service import AgentService
from services.utils.responses_api_handler import ResponsesAPIHandler
from core.security import Security
from supabase import create_client, Client
from core.config import settings
import logging
import json
import uuid
import sys
from flask import stream_with_context
from typing import Any
from services.utils.formatting import format_chunk
from services.warehouses_service import WarehouseService    
# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

# Create blueprint
chats_bp = Blueprint("chats", __name__, url_prefix="/api/chats")

# Initialize chat service
chat_service = ChatService(supabase)

# Initialize agent service
agent_service = AgentService(supabase)

# Initialize logger
logger = logging.getLogger(__name__)

@chats_bp.route("", methods=["POST"])
@Security.require_auth
def create_chat():
    """Create a new chat session."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chat = chat_service.create_chat(
            user_id=user_id,
            title=data.get("title", "New Chat"),
            metadata=data.get("metadata", {})
        )
        return jsonify(chat), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@chats_bp.route("", methods=["GET"])
@Security.require_auth
def get_chats():
    """Get all chat sessions for the authenticated user."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chats = chat_service.get_user_chats(user_id)
        return jsonify(chats), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@chats_bp.route("/<string:chat_id>", methods=["GET"])
@Security.require_auth
def get_chat(chat_id: str):
    """Get a specific chat session by ID."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chat = chat_service.get_chat(user_id, chat_id)
        return jsonify(chat), 200
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return jsonify({"error": error_message}), 404
        return jsonify({"error": error_message}), 400
    except Exception as e:
        logger.error(f"Error getting chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chats_bp.route("/<string:chat_id>", methods=["PUT"])
@Security.require_auth
def update_chat(chat_id: str):
    """Update a chat session by ID."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chat = chat_service.update_chat(
            user_id=user_id,
            chat_id=chat_id,
            title=data.get("title"),
            metadata=data.get("metadata")
        )
        return jsonify(chat), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@chats_bp.route("/<string:chat_id>", methods=["DELETE"])
@Security.require_auth
def delete_chat(chat_id: str):
    """Delete a chat session by ID."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chat_service.delete_chat(user_id, chat_id)
        return jsonify({"message": "Chat deleted successfully"}), 200
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return jsonify({"error": error_message}), 404
        return jsonify({"error": error_message}), 400
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@chats_bp.route("/<string:chat_id>/messages", methods=["POST"])
@Security.require_auth
def send_message(chat_id: str):
    """Send a message to a chat session and get the agent's response."""
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    # Validate required fields
    required_fields = [{'field': 'agent_id', 'type': str}, {'field': 'payload', 'type': dict}]
    for field in required_fields:
        if field['field'] not in data or not isinstance(data[field['field']], field['type']):
            return jsonify({"error": f"Missing or invalid {field['field']}"}), 400
    
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        chat = chat_service.get_chat(user_id, chat_id)

        chat_service.save_message(
            chat_id=chat_id,
            user_id=user_id,
            agent_id=data["agent_id"],
            sender="user",
            payload=data.get("payload", {}),
            metadata=data.get("metadata", {})
        )

        agent = agent_service.get_agent(user_id, data["agent_id"])
        if not agent:
            return jsonify({"error": 'Agent not found'}), 400     

        instructions = agent.get("config", {}).get("instructions", "")
        tools = agent.get("config", {}).get("tools", [])

        model = data.get("payload", {}).get("model")

        messages = chat_service.get_chat_messages(chat_id, user_id)

        input = []
        for m in messages:
            if m["sender"] == "user":
                input += [it for it in m.get('payload', {}).get('input', []) if it['role'] != 'developer']
            elif m["sender"] == "assistant":
                payload = m.get('payload', '[]')
                for response in payload:
                    if response['type'] != 'function_call_output':
                        outputs = response['response'].get('output', [])
                        for output in outputs:
                            if output['type'] == 'message':
                                input += [{'role': output['role'], 'content': content['text']} for content in output['content'] if content['type'] == 'output_text']
                            elif output['type'] == 'function_call':
                                input.append(output)
                    else:
                        response['output'] = json.dumps(response['output'])
                        input.append({k: v for k, v in response.items() if k in ['type', 'call_id', 'output']})
        
        warehouse_id = data.get('metadata', {}).get('warehouse_id', None)
        if warehouse_id:
            warehouse_service = WarehouseService(supabase)
            schema = warehouse_service.get_warehouse_schema(user_id, warehouse_id)
            input.insert(0, {"role": "developer", "content": f"Warehouse Schema: {json.dumps(schema)}"})
        else:
            input.insert(0, {"role": "developer", "content": f"Warning: The user don't have any warehouse created. He should create a new warehouse to analyse data"})

        print(data.get('metadata'))
        print(f'Input\n----------\n{input}\n----------')

        def generate_response():
            yield format_chunk('internal.process.started', {"internal_status": "started", "type": "internal.process.started"})
            for chunk_type, chunk in agent_service.run_agent(user_id, instructions, tools, input, model):
                if chunk_type == 'internal.process.completed':
                    chat_service.save_message(
                        chat_id=chat_id,
                        user_id=user_id,
                        agent_id=data["agent_id"],
                        sender="assistant",
                        payload=chunk['responses'],
                        metadata=data.get("metadata", {})
                    )
                    yield 'event: internal.process.completed\ndata: {"internal_status": "completed", "type": "internal.process.completed"}\n\n'
                else:
                    yield format_chunk(chunk_type, chunk)
       
        return Response(
            stream_with_context(generate_response()),
            mimetype='text/event-stream'
        )
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@chats_bp.route("/<string:chat_id>/messages", methods=["GET"])
@Security.require_auth
def get_messages(chat_id: str):
    """Get all messages from a chat session."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    # Get optional limit parameter from query string
    try:
        limit = int(request.args.get("limit")) if request.args.get("limit") else None
    except ValueError:
        return jsonify({"error": "Limit parameter must be a number"}), 400
    
    try:
        messages = chat_service.get_chat_messages(chat_id, user_id, limit)
        return jsonify(messages), 200
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message.lower():
            return jsonify({"error": error_message}), 404
        return jsonify({"error": error_message}), 400
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

