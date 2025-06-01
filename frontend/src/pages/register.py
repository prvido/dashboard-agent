import streamlit as st
from src.modules.util import register

from src.pages.base import BasePage
from src.pages.page_registry import PageRegistry

class RegisterPage(BasePage):

    logo_url = 'https://pvzksrsakhuvnxahclqa.supabase.co/storage/v1/object/public/assets//logo.png'

    def __init__(self):
        pass
        self.render()

    def render(self):
        

        _, col, _ = st.columns([0.20, 0.6, 0.20])


        with col:

            st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 40px;">
                    <div style="text-align: center;">
                        <p style="font-size: 2rem; margin: 0; margin-bottom: 0px; padding: 0px;">Get started today</p>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
            full_name = st.text_input('Full Name', placeholder='John Doe')
            email = st.text_input('Email', placeholder='name@example.com')
            password = st.text_input('Password', type='password', placeholder='Password')
            confirm_password = st.text_input('Confirm Password', type='password', placeholder='Password')

            st.markdown('<div style="margin-bottom: 40px;"><div>', unsafe_allow_html=True)

            message_placeholder = st.empty()

            if st.button('Sign Up', use_container_width=True):
                
                if not full_name or not email or not password:
                    message_placeholder.warning("Please enter full_name, email and password.")

                elif password != confirm_password:
                    message_placeholder.warning("Passwords don't match.")

                else:
                    response = register(email, password, full_name)

                    st.session_state.token = response.get('access_token')
                    st.session_state.user['name'] = response['user'].get('user_metadata').get('full_name').split(' ')[0]
                    
                    page = PageRegistry.get_page('Chat')
                    st.switch_page(page)

            st.markdown(
                """
                <div style="text-align: center; margin-top: 20px;">
                    Already have an account?
                    <a href="/login" target="_self" style="color: #FF4B4B; text-decoration: none;">Sign In</a>
                </div>
                """,
                unsafe_allow_html=True
            )
        


RegisterPage()