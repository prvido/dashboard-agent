"""
Tools manager routes and endpoints.
This module handles:
- GET /tools: Returns all available tools from the tool registry
- POST /tools/run: Runs a specific tool with the provided payload
"""

from flask import Blueprint, jsonify, request
from core.security import Security
from tools.tool_registry import ToolRegistry
import logging

logger = logging.getLogger(__name__)

# Create blueprint
tools_bp = Blueprint("tools", __name__, url_prefix="/api/tools")

@tools_bp.route("", methods=["GET"])
@Security.require_auth
def get_tools():
    """Get all available tools from the tool registry."""
    try:
        # Get all tools from the registry
        tools = ToolRegistry.get_all_tools()
        
        # Convert tools to a list of dictionaries with tool information
        tools_list = []
        for tool_name, tool_class in tools.items():
            # Create a temporary instance to get tool metadata
            temp_instance = tool_class(user_id="temp")
            tools_list.append({
                "name": tool_name,
                "description": temp_instance.description,
                "parameters": temp_instance.parameters
            })
            
        return jsonify(tools_list), 200
    except Exception as e:
        logger.error(f"Error getting tools: {str(e)}")
        return jsonify({"error": "Failed to retrieve tools. Please try again later."}), 500

@tools_bp.route("/run", methods=["POST"])
@Security.require_auth
def run_tool():
    """Run a specific tool with the provided payload."""
    try:
        # Get user ID from the authenticated token
        token = request.headers.get("Authorization").split(" ")[1]
        user_id = Security.get_user_id_from_token(token)

        # Get tool name and payload from request
        data = request.get_json()
        tool_name = data.get("tool_name")
        tool_payload = data.get("tool_payload", {})

        if not tool_name:
            return jsonify({"error": "Tool name is required"}), 400

        # Get the tool class from registry
        tool_class = ToolRegistry.get_tool(tool_name)
        if not tool_class:
            return jsonify({"error": f"Tool {tool_name} not found"}), 404

        # Create tool instance and run it
        tool_instance = tool_class(user_id=user_id)
        result = tool_instance.run(**tool_payload)

        return jsonify({"result": result}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error running tool {tool_name}: {str(e)}")
        return jsonify({"error": f"Failed to run tool {tool_name}. Please try again later."}), 500
