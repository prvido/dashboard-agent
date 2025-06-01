from typing import Any, Dict
from .base import BaseTool
from services.warehouses_service import WarehouseService
from services.datasets_service import DatasetService
from supabase import create_client
from core.config import settings

class ListWarehousesTool(BaseTool):
    def __init__(self, user_id: str):
        super().__init__(
            name="list_warehouses",
            description="Use this tool to see the warehouses and tables the user have access to",
            parameters={
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Optional search query to filter warehouses by name or description"
                    }
                },
                "required": [],
                "additionalProperties": False
            },
            user_id=user_id
        )
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)
        self.warehouse_service = WarehouseService(self.supabase)
        self.dataset_service = DatasetService(self.supabase)

    def run(self, **kwargs) -> Any:
        """Get all warehouses and their tables for the current user, optionally filtered by search query."""
        warehouses = self.warehouse_service.get_all_warehouses(self.user_id, q=kwargs.get("q"))
        
        result = {}
        for wh in warehouses:
            # Get all datasets (tables) for this warehouse
            datasets = self.dataset_service.get_user_datasets(self.user_id, warehouse_id=wh["id"])
            
            # Format tables information
            tables = {}
            for dataset in datasets:
                tables[dataset["name"]] = {
                    "description": dataset.get("description", ""),
                    "columns": dataset.get("columns", [])
                }
            
            # Add warehouse to result
            result[wh["id"]] = {
                "name": wh["name"],
                "description": wh["description"],
                "tables": tables
            }
        
        return {"warehouses": result}

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this tool."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

