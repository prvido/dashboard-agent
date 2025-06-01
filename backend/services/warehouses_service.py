"""
Warehouse service module.
This module handles the business logic for warehouse operations, including:
- Creating and managing DuckDB warehouse files
- Interacting with Supabase storage for warehouse persistence
- Managing warehouse metadata in the database
- Coordinating dataset storage within warehouses
"""

from typing import Dict, Optional, List
from datetime import datetime, UTC
from supabase import create_client, Client
import os
import uuid
import duckdb
import tempfile
from .utils.validation import (
    validate_user_id,
    validate_warehouse_id,
    validate_name,
    validate_bucket_exists,
    BUCKET_NAME,
    STORAGE_PATH,
    MAX_NAME_LENGTH
)

from services.datasets_service import DatasetService

class WarehouseService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.bucket_name = BUCKET_NAME
        self.storage_path = STORAGE_PATH
        self.dataset_service = DatasetService(supabase)

    def _initialize_duckdb(self, path: str):
        conn = duckdb.connect(path)
        try:
            conn.execute("CREATE TABLE metadata (key VARCHAR, value VARCHAR)")
            conn.execute("INSERT INTO metadata VALUES ('version', '1.0')")
            conn.commit()
        finally:
            conn.close()

    def _create_and_upload_duckdb(self, file_path: str):
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = os.path.join(tmp_dir, "warehouse.duckdb")
            
            # Create and initialize DuckDB
            self._initialize_duckdb(temp_file)

            # Upload to Supabase Storage
            try:
                with open(temp_file, "rb") as f:
                    response = self.supabase.storage.from_(self.bucket_name).upload(
                        path=file_path,
                        file=f,
                        file_options={"contentType": "application/octet-stream"},
                    )
            except Exception as e:
                raise ValueError(f"Failed to upload DuckDB file to Supabase: {str(e)}")

    def create_warehouse(self, user_id: str, name: str, description: Optional[str] = None) -> Dict:
        validate_user_id(user_id)
        validate_name(name, "warehouse")
        validate_bucket_exists(self.supabase)

        warehouse_id = str(uuid.uuid4())
        file_path = f"{self.storage_path}/{warehouse_id}.duckdb"

        self._create_and_upload_duckdb(file_path)

        url = self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)

        warehouse_data = {
            "id": warehouse_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "bucket": self.bucket_name,
            "storage_path": file_path,
            "url": url,
        }
        
        response = self.supabase.table("user_warehouses").insert(warehouse_data).execute()

        return response.data[0]

    def get_warehouse(self, user_id: str, warehouse_id: str) -> Dict:
        """Get a warehouse by ID for a specific user."""
        validate_user_id(user_id)
        validate_warehouse_id(warehouse_id)

        response = self.supabase.table("user_warehouses") \
            .select("*") \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .execute()

        if not response.data:
            raise ValueError(f"Warehouse with ID {warehouse_id} not found")

        return response.data[0]

    def update_warehouse(self, user_id: str, warehouse_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Dict:
        """Update a warehouse's name or description."""
        validate_user_id(user_id)
        validate_warehouse_id(warehouse_id)

        warehouse = self.get_warehouse(user_id, warehouse_id)

        update_data = {}
        if name is not None:
            validate_name(name, "warehouse")
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if not update_data:
            raise ValueError("No valid fields to update")

        response = self.supabase.table("user_warehouses") \
            .update(update_data) \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            raise ValueError(f"Failed to update warehouse with ID {warehouse_id}")

        return response.data[0]

    def delete_warehouse(self, user_id: str, warehouse_id: str) -> None:
        """Soft delete a warehouse by marking it as deleted and removing its DuckDB file."""
        validate_user_id(user_id)
        validate_warehouse_id(warehouse_id)

        warehouse = self.get_warehouse(user_id, warehouse_id)

        try:
            # Delete the warehouse file from storage
            self.supabase.storage.from_(self.bucket_name).remove([warehouse["storage_path"]])
        except Exception as e:
            raise ValueError(f"Failed to delete warehouse file: {str(e)}")

        # Update the warehouse record to mark it as deleted
        response = self.supabase.table("user_warehouses") \
            .update({"is_deleted": True}) \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .execute()

        if not response.data:
            raise ValueError(f"Failed to update warehouse with ID {warehouse_id}")

    def get_all_warehouses(self, user_id: str, q: Optional[str] = None) -> List[Dict]:
        validate_user_id(user_id)

        query = self.supabase.table("user_warehouses") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_deleted", False)

        if q:
            # Search in both name and description fields
            query = query.or_(f"name.ilike.%{q}%,description.ilike.%{q}%")

        response = query.execute()
        return response.data
    
    def get_warehouse_schema(self, user_id: str, warehouse_id: str) -> Dict:
        validate_user_id(user_id)
        validate_warehouse_id(warehouse_id)

        warehouse = self.get_warehouse(user_id, warehouse_id)

        if not warehouse:
            raise ValueError(f"Warehouse with ID {warehouse_id} not found")
        
        # Get all datasets (tables) for this warehouse
        datasets = self.dataset_service.get_user_datasets(user_id, warehouse_id=warehouse_id)
        
        # Format tables information
        tables = {}
        for dataset in datasets:
            tables[dataset["name"]] = {
                "description": dataset.get("description", ""),
                "columns": dataset.get("columns", [])
            }
        
        # Return complete schema including warehouse metadata
        return {
            "id": warehouse["id"],
            "name": warehouse["name"],
            "description": warehouse["description"],
            "tables": tables
        }
