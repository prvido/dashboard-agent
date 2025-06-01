import os
from typing import Any
import streamlit as st

class PageRegistry:
    _pages: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, page: st.Page, metadata: dict[str, Any] = {}):
        cls._pages[page.title] = {'page': page, 'metadata': metadata}

    @classmethod
    def get_page(cls, page_title: str):
        return cls._pages.get(page_title)['page']

    @classmethod
    def get_all_pages(cls):
        return list(cls._pages.values())

# BASE_DIR = /app/src/pages
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def page(file: str, **kwargs):
    abs_path = os.path.join(BASE_DIR, file)
    return st.Page(abs_path, **kwargs)

PageRegistry.register(page('chat.py', title='Chat', icon=':material/message:'))
PageRegistry.register(page('warehouses.py', title='Warehouses', icon=':material/warehouse:', url_path='warehouses'))
PageRegistry.register(page('warehouse_details.py', title='Warehouse Details', icon=':material/message:', url_path='warehouse-details'), {'show_in_nav': False})
PageRegistry.register(page('dataset_details.py', title='Dataset Details', icon=':material/message:', url_path='dataset-details'), {'show_in_nav': False})
PageRegistry.register(page('login.py', title='Login', icon=':material/thumb_up:', url_path='login'), {'show_in_nav': False, 'unauth': True})
PageRegistry.register(page('home.py', title='Home', icon=':material/home:', url_path='home', default=True), {'show_in_nav': False, 'unauth': True})
PageRegistry.register(page('waitlist.py', title='Waitlist', icon=':material/home:', url_path='waitlist'), {'show_in_nav': False, 'unauth': True})
