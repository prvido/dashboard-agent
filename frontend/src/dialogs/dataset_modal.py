import streamlit as st
import time

from src.modules.util import upload_dataset, update_dataset
from src.pages.page_registry import PageRegistry


class DatasetModal:
    def __init__(self, warehouse_id, dataset_id=None, dataset_name=None, dataset_description=None, operation='create', destination='Warehouse Details'):
        self.warehouse_id = warehouse_id
        self.dataset_id = dataset_id
        self.dataset_name = dataset_name
        self.dataset_description = dataset_description
        self.operation = operation
        self.destination = destination
        self.render()

    @st.dialog("Create/Update Dataset")
    def render(self):
        file = st.file_uploader("Upload Dataset File", key="dataset_file")
        name = st.text_input("Dataset Name", key="dataset_name", value=self.dataset_name)
        description = st.text_area("Dataset Description", key="dataset_description", value=self.dataset_description)
        
        if st.button("Upload"):
            if not file:
                st.error("Please upload a file")
                return
            
            dataset = upload_dataset(st.session_state['token'], file, self.warehouse_id, name, description )
            st.success("Dataset created successfully!")
            time.sleep(2)
            page = PageRegistry.get_page(self.destination)
            st.switch_page(page)
            