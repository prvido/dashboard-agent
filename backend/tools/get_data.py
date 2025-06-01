from typing import Any, Dict
from .base import BaseTool
import tiktoken
import json
from random import sample
from supabase import create_client, Client
from services.file_handler import FileHandler
from services.warehouses_service import WarehouseService

from core.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

class GetDataTool(BaseTool):

    MAX_OUTPUT_TOKENS = 500

    def __init__(self, user_id: str):
        super().__init__(
            name="get_data",
            description="Run a DuckDB SQL query on a warehouse to retrieve data needed to answer questions. Do not use for creating charts.",
            parameters={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string", 
                        "description": "ID of the warehouse to query."
                    },
                    "query": {
                        "type": "string",
                        "description": "DuckDB SQL query to execute."
                    }
                },
                "required": ["warehouse_id", "query"]
            },
            user_id=user_id
        )
    
    def _get_sample(self, results: list, sample_size: int = 10) -> list[int]:
        return sample(range(len(results)), min(len(results), sample_size))

    def _estimate_token_count(self, results: list[dict], sample_size: int = 10) -> int:
        results_sample = self._get_sample(results, sample_size)
        results_sample_json = '\n'.join([json.dumps(result) for result in results_sample])
        sample_tokens = len(tiktoken.encoding_for_model("gpt-4o").encode(results_sample_json))
        avg_record_token = sample_tokens / len(results_sample)
        estimated_tokens = avg_record_token * len(results)
        return {'sample_tokens':sample_tokens,'avg_record_token': avg_record_token,'estimated_tokens':estimated_tokens}
    
    def _truncate_results(self, results: list[dict], avg_record_token: int) -> list[dict]:
        allowed_records = max(1, int(self.MAX_OUTPUT_TOKENS / avg_record_token))
        return results[:allowed_records]

    def run(self, **kwargs) -> Any:
        from services.duckdb_handler import DuckDBHandler
        
        warehouse_id = kwargs.get("warehouse_id")
        query = kwargs.get("query")
        
        if not warehouse_id or not query:
            raise ValueError("Both warehouse_id and query are required")
            
        # Get warehouse details
        warehouse_service = WarehouseService(supabase)
        warehouse = warehouse_service.get_warehouse(user_id=self.user_id, warehouse_id=warehouse_id)
        
        # Initialize file handler and download warehouse file temporarily
        file_handler = FileHandler()
        file_handler.set_bucket(warehouse["bucket"])
        local_path = file_handler.create_empty_temp_file(".duckdb")
        
        try:
            file_handler.download_file(warehouse["storage_path"], local_path)
            
            # Execute query using DuckDBHandler
            handler = DuckDBHandler()
            results = handler.execute_query(local_path, query)

            estimated_token_count = self._estimate_token_count(results)

            trucate_results = estimated_token_count['estimated_tokens'] > self.MAX_OUTPUT_TOKENS
            if trucate_results:
                results = self._truncate_results(results, estimated_token_count['avg_record_token'])

            response = {
                'data': results,
                'truncated': trucate_results,
            }

            if trucate_results:
                response['warning'] = f"The query returned returned truncated results because the output was to big. The first {len(results)} records are returned."

            return response
            
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