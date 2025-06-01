import streamlit as st
from src.pages.page_registry import PageRegistry
from src.components.divider import DividerComponent

class SidebarComponent:

    logo_url = 'https://pvzksrsakhuvnxahclqa.supabase.co/storage/v1/object/public/assets//logo.png'

    def __init__(self):
        self.render()

    def render(self):
        
        sidebar = st.sidebar

        sidebar.markdown(f'<div style="text-align: center; margin-bottom:20px;"><img src="{self.logo_url}" width="150"></div>', unsafe_allow_html=True)

        with sidebar:
            DividerComponent()
        
        sidebar.markdown('**Resources**')
        pages = [it.get('page') for it in PageRegistry.get_all_pages() if it['metadata'].get('show_in_nav') != False]

        for page in pages:
            sidebar.page_link(page, icon=page.icon)

        sidebar.markdown('**Contact Us**')
        sidebar.page_link('https://forms.gle/J6XdLZA2n16xXCvc7', label='Feedback', icon=':material/feedback:')

        
        if sidebar.button('Log Out', use_container_width=False, key='logout-button', icon=':material/logout:', type='tertiary'):
            st.session_state.user = {}
            st.session_state.token = None
            page = PageRegistry.get_page('Home')
            st.switch_page(page)