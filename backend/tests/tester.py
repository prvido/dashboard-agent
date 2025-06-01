import requests
import io

class Tester:
    def __init__(self):
        self.BASE_URL = "http://127.0.0.1:5000/api"

    def get_access_token(self, email: str, password: str) -> str:
        url = f"{self.BASE_URL}/auth/login"
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)
        return response.json()["access_token"]

    def create_warehouse(self, name: str, description: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/warehouses"
        payload = {"name": name, "description": description}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def get_warehouse(self, warehouse_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/warehouses/{warehouse_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def create_dataset(self, warehouse_id: str, name: str, description: str, access_token: str, data: bytes) -> dict:
        url = f"{self.BASE_URL}/datasets"
        headers = {"Authorization": f"Bearer {access_token}"}
        file_data = io.BytesIO(data)
        file_data.name = "test.csv"
        files = {'file': ('test.csv', file_data, 'text/csv')}
        data = {'warehouse_id': warehouse_id, 'name': name, 'description': description}
        response = requests.post(url, files=files, data=data, headers=headers)
        return response.json()
    
    def get_dataset(self, dataset_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/datasets/{dataset_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_datasets(self, warehouse_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/datasets"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def update_dataset(self, dataset_id: str, access_token: str, data: bytes) -> dict:
        url = f"{self.BASE_URL}/datasets/{dataset_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        file_data = io.BytesIO(data)
        file_data.name = "test.csv"
        files = {'file': ('test.csv', file_data, 'text/csv')}
        response = requests.put(url, files=files, headers=headers)
        return response.json()

    def delete_dataset(self, dataset_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/datasets/{dataset_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.delete(url, headers=headers)
        return response.json()

    def query_warehouse(self, warehouse_id, access_token: str, query="SELECT table_name FROM information_schema.tables;") -> dict:
        url = f"{self.BASE_URL}/warehouses/{warehouse_id}/query"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers, json={"query": query})
        return response.json()
    
    def create_chat(self, title: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/chats"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers, json={"title": title})
        return response.json()

    def get_chats(self, access_token: str) -> dict:
        url = f"{self.BASE_URL}/chats"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def get_chat(self, chat_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/chats/{chat_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

    def update_chat(self, chat_id: str, access_token: str, title: str = None, metadata: dict = None) -> dict:
        url = f"{self.BASE_URL}/chats/{chat_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {}
        if title is not None:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        response = requests.put(url, headers=headers, json=payload)
        return response.json()

    def delete_chat(self, chat_id: str, access_token: str) -> dict:
        url = f"{self.BASE_URL}/chats/{chat_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.delete(url, headers=headers)
        return response.json()
    
    
