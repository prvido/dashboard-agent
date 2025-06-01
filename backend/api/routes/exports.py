"""
Exports routes and endpoints.
This module handles:
- GET /exports/download/<file_id>: Download a public file from Supabase storage
"""

from flask import Blueprint, send_file, jsonify, after_this_request
from core.config import settings
from supabase import create_client, Client
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

# Create blueprint
exports_bp = Blueprint("exports", __name__, url_prefix="/api/exports")

@exports_bp.route("/download/<file_id>", methods=["GET"])
def download_file(file_id: str):
    """
    Download a public file from Supabase storage.
    This endpoint does not require authentication.
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Download the file from the "exports" bucket
            data = supabase.storage.from_("exports").download(f"{file_id}.csv")
            
            with open(temp_path, "wb") as f:
                f.write(data)

            # Set up cleanup after the response is sent
            @after_this_request
            def cleanup(response):
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    logger.error(f"Error cleaning up temporary file {temp_path}: {str(e)}")
                return response

            # Send with forced download and friendly name
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=f"{file_id}.csv",
                mimetype="text/csv"
            )

        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return jsonify({"error": "File not found"}), 404

    except Exception as e:
        logger.error(f"Internal error in download route: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
