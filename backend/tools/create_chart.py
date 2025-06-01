from typing import Any, Dict
from .base import BaseTool
from services.warehouses_service import WarehouseService
from services.file_handler import FileHandler
from core.config import settings
from supabase import create_client, Client

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

class CreateChartTool(BaseTool):
    def __init__(self, user_id: str):
        super().__init__(
            name="create_chart",
            description="Create a chart from a DuckDB SQL query result without a prior get_data call. Specify the chart type, query, and columns to use. Column names must match exactly the query output.",
            parameters={
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "enum": ["bar", "line", "donut", "table", "scatter"],
                        "description": "Chart type to create."
                    },
                    "x": {
                        "type": "string",
                        "description": "Column name for the x-axis. Must match query output exactly."
                    },
                    "y": {
                        "type": "string",
                        "description": "Column name for the y-axis. Must match query output exactly."
                    },
                    "categories": {
                        "type": "string",
                        "description": "Optional. Column name for grouping data, used mainly for bar and donut charts."
                    },
                    "query": {
                        "type": "string",
                        "description": "DuckDB SQL query selecting the required columns."
                    },
                    "warehouse_id": {
                        "type": "string",
                        "description": "ID of the warehouse storing the data."
                    },
                    "title": {
                        "type": "string",
                        "description": "Title of the chart."
                    }
                },
                "required": ["kind", "x", "y", "query", "warehouse_id", "title"]
            },
            user_id=user_id
        )

    def run(self, **kwargs) -> Any:
        # Validate required parameters
        required_params = ["kind", "x", "y", "query", "warehouse_id", "title"]
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")

        # Validate chart kind
        valid_kinds = ["bar", "line", "donut", "table", "scatter"]
        if kwargs["kind"] not in valid_kinds:
            raise ValueError(f"Invalid chart kind. Must be one of: {', '.join(valid_kinds)}")

        # Validate warehouse exists
        warehouse_service = WarehouseService(supabase)
        warehouse = warehouse_service.get_warehouse(user_id=self.user_id, warehouse_id=kwargs["warehouse_id"])
        if not warehouse:
            raise ValueError(f"Warehouse with ID {kwargs['warehouse_id']} not found")

        # Initialize file handler and download warehouse file temporarily
        file_handler = FileHandler()
        file_handler.set_bucket(warehouse["bucket"])
        local_path = file_handler.create_empty_temp_file(".duckdb")
        
        try:
            file_handler.download_file(warehouse["storage_path"], local_path)
            
            # Execute query to validate it works
            from services.duckdb_handler import DuckDBHandler
            handler = DuckDBHandler()
            results = handler.execute_query(local_path, kwargs["query"])

            # Validate that the required columns exist in the results
            if not results:
                raise ValueError("Query returned no results")
            
            first_row = results[0]
            if kwargs["x"] not in first_row:
                raise ValueError(f"Column '{kwargs['x']}' not found in query results")
            if kwargs["y"] not in first_row:
                raise ValueError(f"Column '{kwargs['y']}' not found in query results")
            if kwargs.get("categories") and kwargs["categories"] not in first_row:
                raise ValueError(f"Categories column '{kwargs['categories']}' not found in query results")

            # Return the validated parameters
            return {
                "kind": kwargs["kind"],
                "x": kwargs["x"],
                "y": kwargs["y"],
                "categories": kwargs.get("categories"),
                "query": kwargs["query"],
                "warehouse_id": kwargs["warehouse_id"],
                "title": kwargs["title"]
            }
            
        finally:
            # Clean up temporary file
            file_handler.cleanup(local_path)

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this tool."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        } 