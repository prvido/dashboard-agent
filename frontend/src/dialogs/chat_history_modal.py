import streamlit as st
from datetime import datetime
from src.modules.util import get_chats, update_chat, delete_chat

from src.components.divider import DividerComponent

class ChatHistoryModal:
    def __init__(self):
        self.render()

    @st.dialog("Chat History")
    def render(self):
        chats = get_chats(st.session_state.token)

        st.markdown("""
           <style>
                .stHorizontalBlock  {
                    justify-content: center;
                    align-items: center;
                }
            </style>         
        """, unsafe_allow_html=True)
        
        widths = [0.6, 0.2, 0.20]
        title_col, date_col, actions_col = st.columns(widths)

        title_col.markdown('**Title**')
        date_col.markdown('**Crated**')
        DividerComponent()
        
        for chat in chats:
            title_col, date_col, actions_col = st.columns(widths)
            title = title_col.text_input('Title', chat.get('title'), label_visibility='collapsed', key=f'title-{chat.get("id")}')

            date = datetime.fromisoformat(chat['created_at']).strftime('%d/%m/%Y')
            date_col.write(date)
            open_col, edit_col, delete_col = actions_col.columns(3)
            
            if open_col.button('', key=f"open-{chat['id']}", type='tertiary', icon=':material/open_in_new:'):
                st.session_state.ids['chat_id'] =  chat.get('id')
                st.rerun()

            if edit_col.button('', key=f"edit-{chat['id']}", type='tertiary', icon=':material/save:'):
                update_chat(st.session_state.token, chat.get('id'), title)

            if delete_col.button('', key=f"delete-{chat['id']}", type='tertiary', icon=':material/delete:'):
                delete_chat(st.session_state.token, chat.get('id'))