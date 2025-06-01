"""
File handling service for managing file operations including temporary files
and storage operations.
"""

import os
import uuid
import tempfile
from typing import List
import logging
import requests
from core.config import settings
from core.security import supabase

logger = logging.getLogger(__name__)

class FileHandler:
    def __init__(self):
        self._bucket_name = None

    def set_bucket(self, bucket_name: str) -> None:
        self._bucket_name = bucket_name

    def create_temp_file(self, file_data: bytes, file_type: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}")
        local_path = temp_file.name
        temp_file.write(file_data)
        temp_file.close()
        return local_path

    def create_empty_temp_file(self, suffix: str) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        local_path = temp_file.name
        temp_file.close()
        return local_path


    def download_file(self, storage_path: str, local_path: str) -> None:
        try:
            download_url = f"{settings.SUPABASE_URL}/storage/v1/object/{self._bucket_name}/{storage_path}"
            cache_buster = f"?t={uuid.uuid4()}"  # prevents CDN cache

            headers = {
                "Authorization": f"Bearer {settings.SUPABASE_API_KEY}"
            }

            response = requests.get(download_url + cache_buster, headers=headers)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

        except Exception as e:
            raise IOError(f"Failed to download file via REST: {str(e)}")




    def upload_file(self, local_path: str, storage_path: str) -> None:
        if not self._bucket_name:
            raise ValueError("Bucket name must be set before performing storage operations")

        try:
            # First try to remove the existing file if it exists
            try:
                supabase.storage.from_(self._bucket_name).remove([storage_path])
            except Exception as e:
                pass

            # Read the file
            with open(local_path, "rb") as f:
                file_data = f.read()
            
            # Upload using Supabase SDK
            res = supabase.storage.from_(self._bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options={"upsert": "true"}
            )
            
            # The response is already an error if the upload failed
            if not res:
                raise IOError(f"Failed to upload file to {storage_path}")

        except Exception as e:
            raise IOError(f"Failed to upload file: {str(e)}")

    def cleanup(self, *file_paths: str) -> None:
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Error removing temporary file {path}: {e}") 