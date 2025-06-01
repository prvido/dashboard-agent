import streamlit as st
from src.pages.base import BasePage
from src.pages.page_registry import PageRegistry

from src.modules.util import get_warehouse, get_datasets, delete_dataset, convert_size, delete_warehouse

from src.dialogs.dataset_modal import DatasetModal
from src.dialogs.warehouse_modal import WarehouseModal

from src.components.divider import DividerComponent
from src.components.metric import MetricComponent
from src.components.back_button import BackButtonComponent

class WarehouseDetailsPage(BasePage):
    def __init__(self):

        self.warehouse_id = st.session_state.ids.get('warehouse_id') or st.query_params.get('warehouse_id')
        if not self.warehouse_id:
            st.switch_page(PageRegistry.get_page('Warehouses'))
        st.session_state.ids['warehouse_id'] = self.warehouse_id
        st.query_params.update(warehouse_id = self.warehouse_id)

        self.warehouse = get_warehouse(st.session_state.token, self.warehouse_id)
        self.datasets = get_datasets(st.session_state.token, self.warehouse_id)
        self.render()

    def _create_update_warehouse_onclick(self):
        def onclick():
            WarehouseModal(self.warehouse['id'], self.warehouse['name'], self.warehouse['description'], operation='update')
        return onclick

    def render(self):

        title_col, back_col, edit_col, delete_col = st.columns([0.85, 0.05, 0.05, 0.05])

        with back_col:
            BackButtonComponent(destination_page=PageRegistry.get_page('Warehouses'))
        
        with title_col:
            st.markdown(f'<p style="font-size: 3rem; margin: 0;">{self.warehouse["name"]}</p>', unsafe_allow_html=True)

        edit_col.button('', use_container_width=True, icon=":material/edit:", key='edit_warehouse', type='tertiary', on_click=self._create_update_warehouse_onclick())

        if delete_col.button('', use_container_width=True, icon=":material/delete:", key='delete_warehouse', type='tertiary'):
            delete_warehouse(st.session_state['token'], self.warehouse['id'])
            st.session_state.ids['warehouse_id'] = None
            page = PageRegistry.get_page('Warehouses')
            st.switch_page(page)

        title_col, _ = st.columns([0.85, 0.1])
        title_col.caption(self.warehouse['description'])

        st.markdown('### Metrics')
        DividerComponent()
        with st.container(key='metrics-container'):
            col1, col2, col3 = st.columns(3)
            with col1:
                MetricComponent(label='Datasets', value=len(self.datasets), decimal_places=0)
            with col2:
                MetricComponent(label='Size', value=convert_size(sum([int(it['size']) for it in self.datasets])))
            with col3:
                MetricComponent(label='Context Tokens', value='-')

        st.markdown('')
        st.markdown('### Datasets')
        DividerComponent()
        search_col, new_wh_col = st.columns([0.75, 0.25])
        table_name_filter = search_col.text_input('x', placeholder='Search', key='search', label_visibility='collapsed')
        new_table_button = new_wh_col.button('Dataset', use_container_width=True, icon=":material/add:", type='primary')
         
        if new_table_button:
            DatasetModal(self.warehouse_id)
        
        widths = [0.15, 0.15, 0.075, 0.075, 0.15]  
        col1, col2, col3, col4, col5 = st.columns(widths)
        col1.markdown('**Name**')
        col2.markdown('**Updated At**')
        col3.markdown('**Type**')
        col4.markdown('**Size**')
        cola, colb, colc = col5.columns(3)
        cola.markdown('Query')
        colb.markdown('Chart')
        colc.markdown('View')

        for dataset in [it for it in self.datasets if table_name_filter in it['name'].lower()]:
            col1, col2, col3, col4, col5 = st.columns(widths)
            col1.markdown(dataset['name'])
            col2.markdown(dataset['updated_at'][0:19])
            col3.markdown(dataset['type'])
            col4.markdown(convert_size(int(dataset['size'])))

            cola, colb, colc = col5.columns(3)
            if cola.button('', use_container_width=True, icon=":material/code:", key=f"view_{dataset['id']}", type='tertiary'):
                st.toast('🕒 Coming Soon')
            if colb.button('', use_container_width=True, icon=":material/bar_chart:", key=f"edit_{dataset['id']}", type='tertiary'):
                st.toast('🕒 Coming Soon')
            
            if colc.button('', use_container_width=True, icon=":material/visibility:", key=f"delete_{dataset['id']}", type='tertiary'):
                st.session_state.ids['dataset_id'] = dataset.get('id')
                page = PageRegistry.get_page('Dataset Details')
                st.switch_page(page)

        st.markdown('')
        st.markdown('### Documents')
        DividerComponent()
        st.markdown('🕒 Coming Soon')

WarehouseDetailsPage()