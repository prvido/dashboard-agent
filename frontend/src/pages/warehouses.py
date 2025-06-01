import streamlit as st

from src.pages.base import BasePage
from src.pages.page_registry import PageRegistry



from src.modules.util import get_warehouses
from src.dialogs.warehouse_modal import WarehouseModal
from src.components.back_button import BackButtonComponent


class WarehouseComponent():
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.render()

    def render(self):
        with st.container(border=True):
            col1, col2 = st.columns([0.95,  0.05])
            col1.markdown(f"#### {self.warehouse['name']}" )
            if col2.button('', use_container_width=True, icon=":material/chevron_right:", key=f'view_{self.warehouse["id"]}', type='tertiary'):
                st.session_state.ids['warehouse_id'] = self.warehouse['id']
                st.switch_page(PageRegistry.get_page('Warehouse Details'))
                
            st.markdown(self.warehouse['description'])



class WarehouseListPage(BasePage):
    def __init__(self):
        self.warehouses = get_warehouses(token=st.session_state.token)
        self.render()

    def render(self):

        st.markdown(f'<p style="font-size: 3rem;">Your warehouses</p>', unsafe_allow_html=True)

        search_col, new_wh_col = st.columns([0.75, 0.25])
        wh_name_filter = search_col.text_input('x', placeholder='Search', key='search', label_visibility='collapsed')
        new_warehouse_button = new_wh_col.button('Warehouse', use_container_width=True, icon=":material/add:", type='primary')

        if new_warehouse_button:
            WarehouseModal()

        for warehouse in [it for it in self.warehouses if wh_name_filter in it['name'].lower()]:
            WarehouseComponent(warehouse)

WarehouseListPage()