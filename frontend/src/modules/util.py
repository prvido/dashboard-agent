import requests
import json

BASE_URL = 'http://backend:5000'

def login(user_email, user_password):
    response = requests.post(f"{BASE_URL}/api/auth/login", json={"email": user_email, "password": user_password})
    try:
        return response.json()
    except:
        return response.text

def register(user_email, user_password, full_name):
    url = f'{BASE_URL}/api/auth/register'
    json = {"email": user_email, "password": user_password, "full_name": full_name}
    response = requests.post(url, json=json)
    return response.json()


def get_warehouses(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/warehouses", headers=headers)
    return response.json()

def get_warehouse(token, warehouse_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/warehouses/{warehouse_id}", headers=headers)
    return response.json()

def create_warehouse(token, name, description):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "description": description}
    response = requests.post(f"{BASE_URL}/api/warehouses", headers=headers, json=data)
    return response.json()

def create_chat(token, title="New Chat", metadata={}):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title, "metadata": metadata}
    response = requests.post(f"{BASE_URL}/api/chats", headers=headers, json=data)
    return response.json()

def update_chat(token, chat_id, title="New Chat", metadata={}):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title, "metadata": metadata}
    response = requests.put(f"{BASE_URL}/api/chats/{chat_id}", headers=headers, json=data)
    return response.json()

def delete_chat(token, chat_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/chats/{chat_id}", headers=headers)
    return response.json()

def get_chats(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/chats", headers=headers)
    return response.json()

def send_message(token, chat_id, agent_id, payload, metadata={}):
    import json
    import requests

    url = f"{BASE_URL}/api/chats/{chat_id}/messages"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"agent_id": agent_id, "payload": payload, "metadata": metadata}

    with requests.post(url, headers=headers, json=data, stream=True) as response_stream:
        event_lines = []

        for raw_chunk in response_stream.iter_lines(decode_unicode=True):
            if raw_chunk == "":
                # End of one event
                event_type = None
                data_lines = []

                for line in event_lines:
                    if line.startswith("event: "):
                        event_type = line[len("event: "):]
                    elif line.startswith("data: "):
                        data_lines.append(line[len("data: "):])

                if event_type and data_lines:
                    try:
                        parsed_data = json.loads("\n".join(data_lines))
                    except json.JSONDecodeError:
                        parsed_data = "\n".join(data_lines)  # Fallback to raw text
                    yield {"event": event_type, "data": parsed_data}

                event_lines = []  # Reset for next event

            else:
                event_lines.append(raw_chunk)

            

def upload_dataset(token, uploaded_file, warehouse_id, name, description=None):
    url = f"{BASE_URL}/api/datasets"
    headers = {"Authorization": f"Bearer {token}"}
    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    data = {'warehouse_id': warehouse_id, 'name': name, 'description': description}
    response = requests.post(url, headers=headers, files=files, data=data)
    return response.json()

def get_datasets(token, warehouse_id):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"warehouse_id": warehouse_id}
    response = requests.get(f"{BASE_URL}/api/datasets", headers=headers, params=params)
    return response.json()

def get_dataset(token, dataset_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/datasets/{dataset_id}", headers=headers)
    return response.json()

def get_chat_messages(token, chat_id, limit=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if limit is not None:
        params["limit"] = limit
    response = requests.get(f"{BASE_URL}/api/chats/{chat_id}/messages", headers=headers, params=params)
    return response.json()

def query_warehouse(token, warehouse_id, query):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"query": query}
    response = requests.post(f"{BASE_URL}/api/warehouses/{warehouse_id}/query", headers=headers, json=data)
    return response.json()

def get_tools(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/tools", headers=headers)
    return response.json()

def run_tool(token, tool_name, tool_payload={}):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "tool_name": tool_name,
        "tool_payload": tool_payload
    }
    response = requests.post(f"{BASE_URL}/api/tools/run", headers=headers, json=data)
    return response.json()

def delete_warehouse(token, warehouse_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/warehouses/{warehouse_id}", headers=headers)
    return response.status_code == 204  # Returns True if successful (204 No Content)

def delete_dataset(token, dataset_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/api/datasets/{dataset_id}", headers=headers)
    return response.status_code == 200  # Returns True if successful (200 OK)

def update_dataset(token, dataset_id, uploaded_file=None):
    url = f"{BASE_URL}/api/datasets/{dataset_id}"
    headers = {"Authorization": f"Bearer {token}"}
    if uploaded_file:
        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.put(url, headers=headers, files=files)
    else:
        response = requests.put(url, headers=headers)
        
    return response.json()

def get_schema(token, warehouse_id):
    url = f"{BASE_URL}/api/tools/run"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "tool_name": "get_schema",
        "tool_payload": {"warehouse_id": warehouse_id}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def convert_size(size):
    if size == 0:
        return '0 KB'
    elif size < 1024:
        return f"1 KB"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

def update_warehouse(token, warehouse_id, name=None, description=None):
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    
    if not data:
        raise ValueError("At least one of name or description must be provided")
        
    response = requests.put(f"{BASE_URL}/api/warehouses/{warehouse_id}", headers=headers, json=data)
    return response.json()