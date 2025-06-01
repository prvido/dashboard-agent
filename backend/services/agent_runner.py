from typing import Any, Generator
from openai import OpenAI
from core.config import settings
import json
from .utils.responses_api_handler import ResponsesAPIHandler
from tools.tool_registry import ToolRegistry


class AgentRunner:
    def __init__(self, user_id: str, instructions: str, tools_list: list[str], input: list[dict], model: str, stream: bool = True):
        self.user_id = user_id
        self.instructions = instructions
        self.input = input
        self.model = model
        self.stream = stream
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.responses = []
        self.keep_running = True
        self._set_tools(tools_list, user_id)

    def _set_tools(self, tools_list: list[str], user_id: str):
        tools = []
        for tool_name in tools_list:
            tool = ToolRegistry.get_tool(tool_name)(user_id=user_id)
            tools.append(tool.get_schema())
        self.tools = tools

    def _execute_tool(self, tool_name: str, tool_args: dict) -> dict:
        try:
            tool_class = ToolRegistry.get_tool(tool_name)
            if not tool_class:
                return {"status": "error", "error": f"Tool {tool_name} not found"}
            tool = tool_class(user_id=self.user_id)
            result = tool.run(**tool_args)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_agent(self, instructions: str, tools: list[dict], input: list[dict], model: str, stream: bool = True) -> Any:
        response = self.client.responses.create(
            model=model,
            input=input,
            instructions=instructions,
            tool_choice='auto',
            parallel_tool_calls=False,
            tools=tools,
            stream=stream
        )
        return response
    
    def _run_tool_calls(self, tool_calls: list[dict]) -> Generator[str, None, None]:
        for tool_call in tool_calls:
            self.input.append(tool_call)
            args = json.loads(tool_call['arguments'])
            yield 'internal.process.tool_execution_started', {"tool_name": tool_call["name"], "result": {}, "type": "internal.process.tool_execution_started"}
            result = self._execute_tool(tool_call['name'], args)            
            yield 'internal.process.tool_execution_completed', {"tool_name": tool_call["name"], "arguments": args, "result": result, "type": "internal.process.tool_execution_completed"}
            self.input.append({
                "type": "function_call_output",
                "call_id": tool_call['call_id'],
                "output": str(result)
            })
            self.responses.append({
                "tool_name": tool_call['name'],
                "arguments": args,
                "type": "function_call_output",
                "call_id": tool_call['call_id'],
                "output": result
            })
            print(f'\n\n{tool_call}:\n{result} \n\n')
    
    def _run_iteration(self) -> Generator[str, None, None]:
        response_stream = self._execute_agent(self.instructions, self.tools, self.input, self.model, stream=self.stream)
        handler = ResponsesAPIHandler(response_stream)
        for chunk_type, chunk in handler.process_stream():
            yield chunk_type, chunk
            response = chunk['response']
            if chunk_type == 'response.completed':
                self.responses.append(chunk)
                tool_calls = [it for it in response['output'] if it['type'] == 'function_call']
                if len(tool_calls) > 0:
                    yield from self._run_tool_calls(tool_calls)
                else:
                    self.keep_running = False

    def run_agent_loop(self) -> Generator[str, None, None]:
        max_iterations = 10
        iteration = 0
        while iteration < max_iterations and self.keep_running:
            yield from self._run_iteration()
            iteration += 1
        yield 'internal.process.completed', {'responses': self.responses, 'type': 'internal.process.completed'}