"""
Dataset manager service layer.
This module handles:
- Dataset CRUD operations
- Data validation and cleaning
- Dataset versioning
- Data sharing and permission management
- Data preview and sampling
- Dataset metadata management
- Data transformation and processing
"""

from typing import Dict, Optional, List, Any
from datetime import datetime, UTC
from supabase import create_client, Client
import uuid
import logging
from .utils.validation import (
    validate_user_id,
    validate_warehouse_id,
    validate_name,
    STORAGE_PATH
)
from .file_handler import FileHandler
from .duckdb_handler import DuckDBHandler

logger = logging.getLogger(__name__)

class DatasetService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.storage_path = STORAGE_PATH
        self.file_handler = FileHandler()
        self.duckdb_handler = DuckDBHandler()


    def get_user_datasets(self, user_id: str, warehouse_id: Optional[str] = None) -> List[Dict]:
        validate_user_id(user_id)
        
        query = self.supabase.table("user_datasets") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_deleted", False)

        if warehouse_id:
            validate_warehouse_id(warehouse_id)
            query = query.eq("warehouse_id", warehouse_id)

        response = query.execute()

        if not response.data:
            return []

        return response.data

    def get_dataset(self, user_id: str, dataset_id: str) -> Optional[Dict]:
        validate_user_id(user_id)
        
        if not dataset_id:
            raise ValueError("Dataset ID is required")

        response = self.supabase.table("user_datasets") \
            .select("*") \
            .eq("id", dataset_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()

        if not response or not response.data:
            return None

        return response.data

    def create_dataset(self, user_id: str, warehouse_id: str, name: str, file_data: bytes, file_type: str, description: Optional[str] = None, tags: Optional[List[str]] = None) -> Dict:
        validate_user_id(user_id)
        validate_warehouse_id(warehouse_id)
        validate_name(name, "dataset")

        warehouse_response = self.supabase.table("user_warehouses") \
            .select("id, storage_path, bucket") \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .maybe_single() \
            .execute()

        if not warehouse_response.data:
            raise ValueError(f"Warehouse with ID {warehouse_id} not found or does not belong to user {user_id}")

        warehouse_data = warehouse_response.data
        warehouse_db_path = warehouse_data.get("storage_path")
        bucket_name = warehouse_data.get("bucket")

        if not warehouse_db_path:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no path configured")
        if not bucket_name:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no bucket configured")

        self.file_handler.set_bucket(bucket_name)

        dataset_id = str(uuid.uuid4())
        file_size = len(file_data)
        now_iso = datetime.now(UTC).isoformat()

        initial_dataset_data = {
            "id": dataset_id,
            "user_id": user_id,
            "warehouse_id": warehouse_id,
            "name": name,
            "type": file_type,
            "description": description,
            "size": str(file_size),
            "columns": [],
            "tags": tags or [],
            "preview_data": [],
            "created_at": now_iso,
            "updated_at": now_iso
        }

        insert_response = self.supabase.table("user_datasets").insert(initial_dataset_data).execute()
        if not insert_response.data or len(insert_response.data) == 0:
            raise ValueError("Failed to create initial dataset record")

        local_warehouse_path = self.file_handler.create_empty_temp_file(".duckdb")
        self.file_handler.download_file(warehouse_db_path, local_warehouse_path)

        try:
            local_upload_path = self.file_handler.create_temp_file(file_data, file_type)

            columns, preview_data = self.duckdb_handler.process_data(
                local_warehouse_path,
                local_upload_path,
                name,
                file_type
            )

            self.file_handler.upload_file(local_warehouse_path, warehouse_db_path)

            update_data = {
                "columns": columns,
                "preview_data": preview_data,
                "updated_at": datetime.now(UTC).isoformat()
            }
            update_response = self.supabase.table("user_datasets") \
                .update(update_data) \
                .eq("id", dataset_id) \
                .execute()

            if not update_response.data or len(update_response.data) == 0:
                logger.warning(f"Failed to update metadata for dataset {dataset_id} after successful DuckDB processing.")
                return initial_dataset_data

            return {**initial_dataset_data, **update_data}

        except Exception as e:
            try:
                self.supabase.table("user_datasets").delete().eq("id", dataset_id).execute()
            except Exception as del_e:
                logger.error(f"Failed to delete metadata record for {dataset_id} during error handling: {del_e}")
            raise ValueError(f"Failed to process and store dataset file in warehouse: {e}") from e

        finally:
            self.file_handler.cleanup(local_warehouse_path, local_upload_path)
        
    def update_dataset(self, user_id: str, dataset_id: str, file_data: bytes, file_type: str) -> Dict:
        validate_user_id(user_id)

        dataset_response = self.supabase.table("user_datasets") \
            .select("*") \
            .eq("id", dataset_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()
        
        if not dataset_response.data:
            raise ValueError(f"Dataset with ID {dataset_id} not found or does not belong to user {user_id}")

        dataset_data = dataset_response.data
        warehouse_id = dataset_data.get("warehouse_id")
        name = dataset_data.get("name")

        warehouse_response = self.supabase.table("user_warehouses") \
            .select("id, storage_path, bucket") \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()
        
        if not warehouse_response.data:
            raise ValueError(f"Warehouse with ID {warehouse_id} not found or does not belong to user {user_id}")

        warehouse_data = warehouse_response.data
        warehouse_db_path = warehouse_data.get("storage_path")
        bucket_name = warehouse_data.get("bucket")

        if not warehouse_db_path:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no path configured")
        if not bucket_name:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no bucket configured")

        self.file_handler.set_bucket(bucket_name)

        file_size = len(file_data)
        now_iso = datetime.now(UTC).isoformat()

        local_warehouse_path = None
        local_upload_path = None

        try:
            local_warehouse_path = self.file_handler.create_empty_temp_file(".duckdb")
            local_upload_path = self.file_handler.create_temp_file(file_data, file_type)

            logger.info(f"Downloading warehouse file from {warehouse_db_path}")
            self.file_handler.download_file(warehouse_db_path, local_warehouse_path)

            logger.info(f"Processing dataset with DuckDB at {local_warehouse_path}")

            columns, preview_data = self.duckdb_handler.process_data(
                local_warehouse_path,
                local_upload_path,
                name,
                file_type
            )

            logger.info(f"Uploading updated warehouse file to {warehouse_db_path}")
            self.file_handler.upload_file(local_warehouse_path, warehouse_db_path)

            update_data = {
                "columns": columns,
                "preview_data": preview_data,
                "size": str(file_size),
                "type": file_type,
                "updated_at": now_iso
            }
            update_response = self.supabase.table("user_datasets") \
                .update(update_data) \
                .eq("id", dataset_id) \
                .execute()

            if not update_response.data or len(update_response.data) == 0:
                raise ValueError(f"Failed to update metadata for dataset {dataset_id}")

            return {**dataset_data, **update_data}

        except Exception as e:
            raise ValueError(f"Failed to process and update dataset file in warehouse: {e}") from e

        finally:
            self.file_handler.cleanup(local_warehouse_path, local_upload_path)

    def delete_dataset(self, user_id: str, dataset_id: str) -> None:
        validate_user_id(user_id)

        dataset_response = self.supabase.table("user_datasets") \
            .select("*") \
            .eq("id", dataset_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()
        
        if not dataset_response.data:
            raise ValueError(f"Dataset with ID {dataset_id} not found or does not belong to user {user_id}")

        dataset_data = dataset_response.data
        warehouse_id = dataset_data.get("warehouse_id")
        name = dataset_data.get("name")

        warehouse_response = self.supabase.table("user_warehouses") \
            .select("id, storage_path, bucket") \
            .eq("id", warehouse_id) \
            .eq("user_id", user_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()
        
        if not warehouse_response.data:
            raise ValueError(f"Warehouse with ID {warehouse_id} not found or does not belong to user {user_id}")

        warehouse_data = warehouse_response.data
        warehouse_db_path = warehouse_data.get("storage_path")
        bucket_name = warehouse_data.get("bucket")

        if not warehouse_db_path:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no path configured")
        if not bucket_name:
            raise ValueError(f"Warehouse with ID {warehouse_id} has no bucket configured")

        self.file_handler.set_bucket(bucket_name)
        local_warehouse_path = None

        try:
            local_warehouse_path = self.file_handler.create_empty_temp_file(".duckdb")
            logger.info(f"Downloading warehouse file from {warehouse_db_path}")
            self.file_handler.download_file(warehouse_db_path, local_warehouse_path)

            # Delete the table from the warehouse file
            self.duckdb_handler.delete_table(local_warehouse_path, name)

            logger.info(f"Uploading updated warehouse file to {warehouse_db_path}")
            self.file_handler.upload_file(local_warehouse_path, warehouse_db_path)

            # Update the dataset record to mark it as deleted
            update_response = self.supabase.table("user_datasets") \
                .update({"is_deleted": True}) \
                .eq("id", dataset_id) \
                .execute()

            if not update_response.data:
                raise ValueError(f"Failed to update dataset metadata for {dataset_id}")

        except Exception as e:
            raise ValueError(f"Failed to delete dataset from warehouse: {e}") from e

        finally:
            self.file_handler.cleanup(local_warehouse_path)