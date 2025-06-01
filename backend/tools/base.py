from typing import Any, Dict, List
from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self, name: str, description: str, parameters: dict[str, Any], user_id: str):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.user_id = user_id
  
    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        pass 