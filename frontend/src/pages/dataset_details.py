import streamlit as st
from src.modules.util import get_dataset, convert_size, delete_dataset, get_warehouse

from src.pages.base import BasePage
from src.pages.page_registry import PageRegistry

from src.dialogs.dataset_modal import DatasetModal

from src.components.divider import DividerComponent
from src.components.back_button import BackButtonComponent

class DatasetDetailsPage(BasePage):
    def __init__(self):

        self.warehouse_id = st.session_state.ids.get('warehouse_id') or st.query_params.get('warehouse_id')
        if not self.warehouse_id:
            st.switch_page(PageRegistry.get_page('Warehouses'))
        st.session_state.ids['warehouse_id'] = self.warehouse_id
        st.query_params.update(warehouse_id = self.warehouse_id)

        self.dataset_id = st.session_state.ids.get('dataset_id') or st.query_params.get('dataset_id')
        if not self.dataset_id:
            st.switch_page(PageRegistry.get_page('Warehouse Details'))
        st.session_state.ids['dataset_id'] = self.dataset_id
        st.query_params.update(dataset_id = self.dataset_id)

        self.warehouse = get_warehouse(st.session_state.token, self.warehouse_id)
        self.dataset = get_dataset(st.session_state.token, self.dataset_id)
        self.render()

        
    def render(self):
        
        title_col, back_col, edit_col, delete_col = st.columns([0.85, 0.05, 0.05, 0.05])

        with back_col:
            BackButtonComponent(PageRegistry.get_page('Warehouse Details'))

        title_col.markdown(f'<p style="font-size: 3rem; margin: 0;">{self.dataset["name"]}</p>', unsafe_allow_html=True)
        
        if edit_col.button('', use_container_width=True, icon=":material/edit:", key='edit_dataset', type='tertiary'):
            st.toast('🕒 Coming Soon')
        
        if delete_col.button('', use_container_width=True, icon=":material/delete:", key='delete_dataset', type='tertiary'):
            delete_dataset(st.session_state.token, st.session_state.ids['dataset_id'])
            st.switch_page(PageRegistry.get_page('Warehouse Details'))

        title_col, _ = st.columns([0.9, 0.1])
        title_col.caption(self.dataset['description'])

        
        st.markdown('#### Info')
        DividerComponent()
        col1, col2 = st.columns([0.3, 0.7])
        col1.markdown('**Created At**')
        col2.markdown(self.dataset['created_at'])
        col1.markdown('**Updated At**')
        col2.markdown(self.dataset['updated_at'])
        col1.markdown('**Size**')
        col2.markdown(convert_size(int(self.dataset['size'])))
        col1.markdown('**Type**')
        col2.markdown(self.dataset['type'])


        st.markdown('#### Schema')
        DividerComponent()
        col1, col2 = st.columns([0.3, 0.7])
        col1.markdown('**Name**')
        col2.markdown('**Type**')
        for column in self.dataset['columns']:
            col1, col2 = st.columns([0.3, 0.7])
            col1.markdown(f"{column['name']}:")
            col2.markdown(f"{column['type']}")
        
        st.markdown('#### Preview')
        DividerComponent()
        st.dataframe(self.dataset['preview_data'], use_container_width=True)

DatasetDetailsPage()