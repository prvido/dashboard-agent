import streamlit as st

class BackButtonComponent:
    def __init__(self, destination_page: st.Page, key=None):
        self.destination_page = destination_page
        self.key = key
        self.render()

    def render(self):
        if st.button('', type='tertiary', icon=':material/arrow_back:', key=self.key):
            st.switch_page(self.destination_page)

