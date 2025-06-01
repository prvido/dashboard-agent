import streamlit as st
from state_handler import StateHandler

from src.pages.base import BasePage

from src.components.divider import DividerComponent

class ComingSoonPage(BasePage):

    def __init__(self, state_handler:StateHandler):
        super().__init__(state_handler)
        self.page_name = st.session_state.coming_soon_settings['page_name']
        self.render()
    
    def render(self):
        st.markdown(f'<p style="font-size: 3rem;">{self.page_name}</p>', unsafe_allow_html=True)
        DividerComponent()
        st.markdown('This feature is not available yet, but we are happy that you showed interest.')