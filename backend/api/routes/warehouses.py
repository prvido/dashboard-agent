"""
Warehouse manager routes and endpoints.
This module handles:
- GET /warehouses: Returns metadata for all warehouses uploaded by the authenticated user.
- POST /warehouses: Create a new warehouse
- GET /warehouses/{warehouse_id}: Get a warehouse by ID
- PUT /warehouses/{warehouse_id}: Update a warehouse by ID
- DELETE /warehouses/{warehouse_id}: Delete a warehouse by ID
"""

from flask import Blueprint, request, jsonify
from services.warehouses_service import WarehouseService
from core.security import Security
from supabase import create_client, Client
from core.config import settings
from services.file_handler import FileHandler
from services.duckdb_handler import DuckDBHandler

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

# Create blueprint
warehouses_bp = Blueprint("warehouses", __name__, url_prefix="/api/warehouses")

# Initialize warehouse service
warehouse_service = WarehouseService(supabase)


@warehouses_bp.route("", methods=["GET"])
@Security.require_auth
def get_all_warehouses():
    """Get all warehouses for the authenticated user."""
    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        warehouses = warehouse_service.get_all_warehouses(user_id=user_id)
        return jsonify(warehouses), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@warehouses_bp.route("", methods=["POST"])
@Security.require_auth
def create_warehouse():
    """Create a new warehouse."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Warehouse name is required"}), 400
    
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    warehouse = warehouse_service.create_warehouse(
        user_id=user_id,
        name=data["name"],
        description=data.get("description")
    )
    
    return jsonify(warehouse), 201


@warehouses_bp.route("/<string:warehouse_id>", methods=["GET"])
@Security.require_auth
def get_warehouse(warehouse_id: str):
    """Get a warehouse by ID."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        warehouse = warehouse_service.get_warehouse(user_id=user_id, warehouse_id=warehouse_id)
        return jsonify(warehouse), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@warehouses_bp.route("/<string:warehouse_id>", methods=["PUT"])
@Security.require_auth
def update_warehouse(warehouse_id: str):
    """Update a warehouse's name or description."""
    data = request.get_json()
    if not data or not any(key in data for key in ["name", "description"]):
        return jsonify({"error": "At least one of name or description must be provided"}), 400
    
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        warehouse = warehouse_service.update_warehouse(
            user_id=user_id,
            warehouse_id=warehouse_id,
            name=data.get("name"),
            description=data.get("description")
        )
        return jsonify(warehouse), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@warehouses_bp.route("/<string:warehouse_id>", methods=["DELETE"])
@Security.require_auth
def delete_warehouse(warehouse_id: str):
    """Delete a warehouse."""
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        warehouse_service.delete_warehouse(user_id=user_id, warehouse_id=warehouse_id)
        return "", 204
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500


@warehouses_bp.route("/<string:warehouse_id>/query", methods=["POST"])
@Security.require_auth
def query_warehouse(warehouse_id: str):
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)
    
    try:
        # Get the query from request body
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Query parameter is required"}), 400
            
        query = data["query"]
        
        # Get warehouse details
        warehouse = warehouse_service.get_warehouse(user_id=user_id, warehouse_id=warehouse_id)
        
        # Initialize file handler
        file_handler = FileHandler()
        file_handler.set_bucket(warehouse["bucket"])
        
        # Download warehouse file temporarily
        local_path = file_handler.create_empty_temp_file(".duckdb")
        try:
            file_handler.download_file(warehouse["storage_path"], local_path)
            
            # Execute query using DuckDBHandler
            duckdb_handler = DuckDBHandler()
            result = duckdb_handler.execute_query(local_path, query)
            
            return jsonify({"data": result}), 200
            
        finally:
            # Clean up temporary file
            file_handler.cleanup(local_path)
            
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        # Return the actual error message from DuckDB
        return jsonify({"error": str(e)}), 500

