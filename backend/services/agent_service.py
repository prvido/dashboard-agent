"""
Agent service module.
This module handles the business logic for agents operations, including:
- Executing a given agent
- Interacting with Supabase database to get the agent's instructions
"""

from typing import Dict, Optional, Any, Generator
from supabase import Client
from tools.tool_registry import ToolRegistry
from .utils.validation import validate_user_id, validate_agent_id
from .agent_runner import AgentRunner
import logging

logger = logging.getLogger(__name__)

class AgentService:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        

    def get_agent(self, user_id: str, agent_id: str) -> Optional[Dict]:
        validate_user_id(user_id)
        validate_agent_id(agent_id)

        response = self.supabase.table("user_agents") \
            .select("*") \
            .eq("id", agent_id) \
            .eq("is_deleted", False) \
            .maybe_single() \
            .execute()

        if not response or not response.data:
            return None
        elif response.data.get('is_private') and response.data.get('user_id') != user_id:
            return None

        return response.data
    
    def run_agent(self, user_id: str, instructions: str, tools: list[dict], input: list[dict], model: str) -> Generator[str, None, None]:
        
        with open('prompts/instructions.txt', 'r') as file:
            _instructions = file.read()
        
        _tools = ['create_chart', 'get_data', 'get_schema', 'export_data']
        
        _model = 'gpt-4o-mini'

        runner = AgentRunner(user_id, _instructions, _tools, input, _model)
        return runner.run_agent_loop()

        # with open('mock/agent_response.json', 'r') as file:
        #     mock_response = json.load(file)
        # for chunk in mock_response:
        #     if chunk['event'] != 'internal.process.completed':
        #         yield chunk['event'], chunk['data']
        #         time.sleep(0.05)
        # responses = [it['data']['response'] for it in mock_response if it['event'] == 'response.completed']
        # yield 'internal.process.completed', {'responses': responses, 'type': 'internal.process.completed'}

        
        

