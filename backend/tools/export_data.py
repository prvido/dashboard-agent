from typing import Any, Dict
from .base import BaseTool
import pandas as pd
from supabase import create_client, Client
from services.file_handler import FileHandler
from services.warehouses_service import WarehouseService
from core.config import settings
import uuid
from datetime import datetime

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

class ExportDataTool(BaseTool):
    def __init__(self, user_id: str):
        super().__init__(
            name="export_data",
            description="Export data to a CSV file with a SQL query",
            parameters={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string",
                        "description": "ID of the warehouse to query"
                    },
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    }
                },
                "required": ["warehouse_id", "query"]
            },
            user_id=user_id
        )

    def run(self, **kwargs) -> Any:
        from services.duckdb_handler import DuckDBHandler
        
        warehouse_id = kwargs.get("warehouse_id")
        query = kwargs.get("query")
        
        if not warehouse_id or not query:
            raise ValueError("Both warehouse_id and query are required")
            
        # Get warehouse details
        warehouse_service = WarehouseService(supabase)
        warehouse = warehouse_service.get_warehouse(user_id=self.user_id, warehouse_id=warehouse_id)
        
        file_handler = FileHandler()
        file_handler.set_bucket(warehouse["bucket"])
        local_path = file_handler.create_empty_temp_file(".duckdb")
        
        try:
            file_handler.download_file(warehouse["storage_path"], local_path)
            
            handler = DuckDBHandler()
            results = handler.execute_query(local_path, query)

            df = pd.DataFrame(results)
            
            file_id = str(uuid.uuid4())
            csv_filename = f"{file_id}.csv"
            
            temp_csv_path = file_handler.create_empty_temp_file(".csv")
            df.to_csv(temp_csv_path, index=False, encoding="utf-8")
            
            file_handler.set_bucket("exports")
            file_handler.upload_file(temp_csv_path, csv_filename)
            
            return {
                "download_url": f"{settings.BASE_URL}/api/exports/download/{file_id}",
                "filename": csv_filename,
                "row_count": len(df)
            }
            
        finally:
            file_handler.cleanup(local_path)
            if 'temp_csv_path' in locals():
                file_handler.cleanup(temp_csv_path)

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this tool."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        } 