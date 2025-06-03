import streamlit as st

from src.pages.page_registry import PageRegistry

from src.components.sidebar import SidebarComponent

st.set_page_config(page_icon='https://pvzksrsakhuvnxahclqa.supabase.co/storage/v1/object/public/assets//icon.png')

# Initialize session_state  first
if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = {}

if "ids" not in st.session_state:
    st.session_state.ids = {
        "warehouse_id": None,
        "dataset_id": None,
        "chat_id": None,
        "agent_id": "33e8ffcc-d3da-4979-98a5-a339bec744ab",
        "model_id": "gpt-4o"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

# Load Styles
st.html('src/styles/globals.css')

if not st.session_state.token:
    pages = [it['page'] for it in PageRegistry.get_all_pages() if it['metadata'].get('unauth')]
else:
    SidebarComponent()
    pages = [it.get('page') for it in PageRegistry.get_all_pages()]
nav = st.navigation(pages, position='hidden')

nav.run()

