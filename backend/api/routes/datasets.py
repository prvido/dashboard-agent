"""
Warehouse manager routes and endpoints.
This module handles:
- GET /datasets: Returns metadata for all datasets uploaded by the authenticated user.
- POST /datasets: Create a new dataset in a wareshouse
- GET /datasets/{dataset_id}: Get a dataset by ID
- PUT /datasets/{dataset_id}: Update a dataset by ID
- DELETE /datasets/{dataset_id}: Delete a dataset by ID
"""

from flask import Blueprint, request, jsonify
from services.datasets_service import DatasetService
from core.security import Security
from supabase import create_client, Client
from core.config import settings
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

# Create blueprint
datasets_bp = Blueprint("datasets", __name__, url_prefix="/api/datasets")

# Initialize dataset service
dataset_service = DatasetService(supabase)

@datasets_bp.route("", methods=["GET"])
@Security.require_auth
def get_datasets():

    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)

    # Get optional warehouse_id from query parameters
    warehouse_id = request.args.get("warehouse_id")

    try:
        datasets = dataset_service.get_user_datasets(user_id, warehouse_id)
        return jsonify(datasets), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting datasets: {str(e)}")
        return jsonify({"error": "Failed to retrieve datasets. Please try again later."}), 500

@datasets_bp.route("/<string:dataset_id>", methods=["GET"])
@Security.require_auth
def get_dataset(dataset_id: str):

    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)

    try:
        # Get dataset from the service
        dataset = dataset_service.get_dataset(user_id, dataset_id)
        if not dataset:
            return jsonify({"error": f"Dataset with ID {dataset_id} not found"}), 404
        return jsonify(dataset), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting dataset {dataset_id}: {str(e)}")
        return jsonify({"error": f"Failed to retrieve dataset {dataset_id}. Please try again later."}), 500

@datasets_bp.route("", methods=["POST"])
@Security.require_auth
def create_dataset():
    """Create a new dataset in a warehouse."""
    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)

    # Check if file is present in the request
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Get warehouse_id from form data
    warehouse_id = request.form.get("warehouse_id")
    if not warehouse_id:
        return jsonify({"error": "Warehouse ID is required"}), 400

    # Get dataset name from form data
    name = request.form.get("name")
    if not name:
        return jsonify({"error": "Dataset name is required"}), 400

    # Get optional description
    description = request.form.get("description")

    # Get file type from extension
    file_type = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if not file_type:
        return jsonify({"error": "Could not determine file type"}), 400

    try:
        # Read file data
        file_data = file.read()
        
        # Create dataset
        dataset = dataset_service.create_dataset(
            user_id=user_id,
            warehouse_id=warehouse_id,
            name=name,
            file_data=file_data,
            file_type=file_type,
            description=description
        )
        
        return jsonify(dataset), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@datasets_bp.route("/<string:dataset_id>", methods=["PUT"])
@Security.require_auth
def update_dataset(dataset_id: str):
    """Update an existing dataset in a warehouse."""
    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)

    # Check if file is present in the request
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    # Get file type from extension
    file_type = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if not file_type:
        return jsonify({"error": "Could not determine file type"}), 400

    try:
        # Read file data
        file_data = file.read()
        
        # Update dataset
        dataset = dataset_service.update_dataset(
            user_id=user_id,
            dataset_id=dataset_id,
            file_data=file_data,
            file_type=file_type
        )
        
        return jsonify(dataset), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating dataset {dataset_id}: {str(e)}")
        return jsonify({"error": f"Failed to update dataset {dataset_id}. Please try again later."}), 500

@datasets_bp.route("/<string:dataset_id>", methods=["DELETE"])
@Security.require_auth
def delete_dataset(dataset_id: str):
    """Delete a dataset from a warehouse."""
    # Get user ID from the authenticated token
    token = request.headers.get("Authorization").split(" ")[1]
    user_id = Security.get_user_id_from_token(token)

    try:
        # Delete dataset
        dataset_service.delete_dataset(
            user_id=user_id,
            dataset_id=dataset_id
        )
        
        return jsonify({"message": "Dataset marked as deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete dataset {dataset_id}. Please try again later."}), 500