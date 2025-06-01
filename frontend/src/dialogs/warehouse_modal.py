import streamlit as st
import time

from src.modules.util import create_warehouse, update_warehouse

from src.pages.page_registry import PageRegistry

class WarehouseModal:

    def __init__(self, warehouse_id=None, warehouse_name=None, warehouse_description=None, operation='create', destination='Warehouse Details'):
        self.warehouse_id = warehouse_id
        self.warehouse_name = warehouse_name
        self.warehouse_description = warehouse_description
        self.operation = operation
        self.destination = destination
        self.render()

    @st.dialog(f"Create/Update Warehouse")
    def render(self):

        name = st.text_input("Warehouse Name", key="warehouse_name", value=self.warehouse_name)
        description = st.text_area("Warehouse Description", key="warehouse_description", value=self.warehouse_description)
        
        if self.operation == 'create':
            if st.button("Create"):
                warehouse = create_warehouse(st.session_state['token'], name, description)
                st.success("Warehouse created successfully!")
                time.sleep(1)
                st.session_state.ids['warehouse_id'] = warehouse.get('id')
                page = PageRegistry.get_page(self.destination)
                st.switch_page(page)

        elif self.operation == 'update':
            if st.button("Update"):
                update_warehouse(st.session_state['token'], self.warehouse_id, name, description)
                st.success("Warehouse updated successfully!")
                time.sleep(1)
                st.rerun()

