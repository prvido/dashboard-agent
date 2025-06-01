from typing import Dict, Type
from .base import BaseTool

class ToolRegistry:
    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """Register a tool class with the registry."""
        # Create an instance to get the tool name
        temp_instance = tool_class(user_id="temp")
        cls._tools[temp_instance.name] = tool_class
        return tool_class

    @classmethod
    def get_tool(cls, tool_name: str) -> Type[BaseTool]:
        """Get a tool class by name."""
        return cls._tools.get(tool_name)

    @classmethod
    def get_all_tools(cls) -> Dict[str, Type[BaseTool]]:
        """Get all registered tools."""
        return cls._tools.copy()

# Import and register tools here
from tools.list_warehouses import ListWarehousesTool
from tools.get_data import GetDataTool
from tools.export_data import ExportDataTool
from tools.get_schema import GetSchemaTool
from tools.create_chart import CreateChartTool

ToolRegistry.register(ListWarehousesTool)
ToolRegistry.register(GetDataTool)
ToolRegistry.register(ExportDataTool) 
ToolRegistry.register(GetSchemaTool)
ToolRegistry.register(CreateChartTool)