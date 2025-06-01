from typing import Any, Dict
from .base import BaseTool
from services.warehouses_service import WarehouseService
from services.datasets_service import DatasetService
from supabase import create_client
from core.config import settings

class GetSchemaTool(BaseTool):
    def __init__(self, user_id: str):
        super().__init__(
            name="get_schema",
            description="Retrieve metadata about a warehouse and its tables using the warehouse ID. Use only to inspect structure, not to query data.",
            parameters={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string",
                        "description": "ID of the warehouse to retrieve metadata from."
                    }
                },
                "required": ["warehouse_id"],
                "additionalProperties": False
            },
            user_id=user_id
        )
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)
        self.warehouse_service = WarehouseService(self.supabase)
        self.dataset_service = DatasetService(self.supabase)

    def run(self, **kwargs) -> Any:
        """Get a specific warehouse and its tables by warehouse ID."""
        warehouse_id = kwargs.get("warehouse_id")
        
        # Get the warehouse
        warehouse = self.warehouse_service.get_warehouse(self.user_id, warehouse_id)
        if not warehouse:
            return {"error": f"Warehouse with ID {warehouse_id} not found or access denied"}
        
        # Get all datasets (tables) for this warehouse
        datasets = self.dataset_service.get_user_datasets(self.user_id, warehouse_id=warehouse_id)
        
        # Format tables information
        tables = {}
        for dataset in datasets:
            tables[dataset["name"]] = {
                "description": dataset.get("description", ""),
                "columns": dataset.get("columns", [])
            }
        
        # Format the result
        result = {
            "id": warehouse["id"],
            "name": warehouse["name"],
            "description": warehouse["description"],
            "tables": tables
        }
        
        return result

    def get_schema(self) -> Dict[str, Any]:
        """Get the schema for this tool."""
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        } 