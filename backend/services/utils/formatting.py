from typing import Any
import json

def format_chunk(event: str, data: Any) -> str:
    return f'event: {event}\ndata: {json.dumps(data)}\n\n'