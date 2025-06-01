class ResponsesAPIHandler:
    # Response types that should replace the entire placeholder
    RESPONSE_TYPES = {
        'response.created', 'response.in_progress', 
        'response.completed', 'response.failed', 'response.incomplete'
    }
    
    # Response types that modify output items
    OUTPUT_ITEM_TYPES = {
        'output_item.added', 'response.output_item.done'
    }
    
    # Response types that modify content parts
    CONTENT_PART_TYPES = {
        'response.content_part.added', 'response.content_part.done'
    }

    def __init__(self, stream):
        self.stream = stream
        self.placeholder = {}
    
    def _handle_response(self, chunk):
        self.placeholder = chunk.to_dict()

    def _handle_output_item(self, chunk):
        while len(self.placeholder['response']['output']) <= chunk.output_index:
            self.placeholder['response']['output'].append({'content': []})
        self.placeholder['response']['output'][chunk.output_index] = chunk.item.to_dict()

    def _handle_content_part(self, chunk):
        while len(self.placeholder['response']['output']) <= chunk.output_index:
            self.placeholder['response']['output'].append({'content': []})
        while len(self.placeholder['response']['output'][chunk.output_index]['content']) <= chunk.content_index:
            self.placeholder['response']['output'][chunk.output_index]['content'].append({})
        self.placeholder['response']['output'][chunk.output_index]['content'][chunk.content_index] = chunk.part.to_dict()

    def _handle_text_delta(self, chunk):
        self.placeholder['response']['output'][chunk.output_index]['content'][chunk.content_index]['text'] += chunk.delta

    def _handle_annotation(self, chunk):
        self.placeholder['response']['output'][chunk.output_index]['content'][chunk.content_index]['annotations']['annotation_index'] = chunk.annotation.to_dict()

    def _handle_function_call_delta(self, chunk):
        if chunk.output_index >= len(self.placeholder['response']['output']):
            self.placeholder['response']['output'][chunk.output_index] = {'arguments': '', **(chunk for k, v in chunk.items() if k != 'delta')}
        self.placeholder['response']['output'][chunk.output_index]['arguments'] += chunk.delta

    def process_stream(self):
        handlers = {
            'response.output_text.delta': self._handle_text_delta,
            'response.output_text.annotation.added': self._handle_annotation,
            'response.output_function_call.delta': self._handle_function_call_delta
        }
        for chunk in self.stream:
            if chunk.type in self.RESPONSE_TYPES:
                self._handle_response(chunk)
            elif chunk.type in self.OUTPUT_ITEM_TYPES:
                self._handle_output_item(chunk)
            elif chunk.type in self.CONTENT_PART_TYPES:
                self._handle_content_part(chunk)
            else:
                handler = handlers.get(chunk.type)
                if handler:
                    handler(chunk)
            yield chunk.type, self.placeholder
    
    def sanitize_response(self):
        chunk = self.placeholder
        chunk_type = chunk['type']
        response = chunk['response']

        sanitized_response = {
            "type": chunk_type,
            "status": response['status'],
            "created_at": response['created_at'],
            "output": response['output']
        }

        if chunk_type == 'response.failed':
            sanitized_response["error"] = response.get("error", {})
        elif chunk_type == 'response.incomplete':
            sanitized_response["incomplete"] = response.get("incomplete_details", {})

        return sanitized_response
