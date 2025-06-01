import streamlit as st
from src.pages.base import BasePage


class WaitlistPage(BasePage):
    """Minimalistic wait-list landing page."""

    logo_url: str = (
        "https://pvzksrsakhuvnxahclqa.supabase.co/storage/v1/object/public/assets//logo.png"
    )
    waitlist_url: str = "https://forms.gle/C8CjQXWu4Y2CKqEUA"

    def __init__(self):
        self.render()

    def render(self) -> None:

        # --- Logo (centered) --------------------------------------------------
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="{self.logo_url}" style="max-width:240px; width:100%;" />
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Short message ----------------------------------------------------
        st.markdown(
            """
            <p style="text-align:center; font-size:1.1rem; margin-top:1.5rem;">
                We’re currently rolling out access in batches.<br/>
                Join the wait-list and we’ll notify you as soon as your invite is ready!
            </p>
            """,
            unsafe_allow_html=True,
        )

        # --- “Join the wait-list” button --------------------------------------
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:1.5rem;">
                <a href="{self.waitlist_url}" target="_blank"
                   style="text-decoration:none;">
                    <button style="
                        background-color:#FF4B4B;
                        color:white;
                        border:none;
                        padding:0.75rem 2.25rem;
                        border-radius:6px;
                        font-size:1rem;
                        cursor:pointer;">
                        Join the&nbsp;Wait-list
                    </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Instantiate the page (Streamlit will execute this when imported)
WaitlistPage()
