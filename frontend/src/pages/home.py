import streamlit as st
from src.pages.base import BasePage
from src.pages.page_registry import PageRegistry

class HomePage(BasePage):
    logo_url: str = "https://pvzksrsakhuvnxahclqa.supabase.co/storage/v1/object/public/assets//logo.png"

    def __init__(self):
        self.render()

    def render(self) -> None:

        # ─────────────────── HEADER ────────────────────
        logo_col, _, login_col, start_col = st.columns([0.50, 0.25, 0.10, 0.15])
        with logo_col:
            st.image(self.logo_url, width=125)

        with login_col:
            if st.button("Sign In", use_container_width=True, type="tertiary"):
                st.switch_page(PageRegistry.get_page("Login"))

        with start_col:
            if st.button("Start", use_container_width=True, type="primary"):
                st.switch_page(PageRegistry.get_page("Waitlist"))

        # ─────────────────── HERO ──────────────────────
       
        with st.container(key='homepage-hero'):
            st.html(
                """
                <h1 style='text-align:center;font-size:4rem;font-weight:600;margin:0px auto;'>
                    Analyse it with Intuitus
                </h1>
                """
            )
            st.html(
                """
                <p style='text-align:center;max-width:100%;font-size:1.25rem;line-height:1.5;font-weight:200;margin: 0px auto;'>
                    Intuitus is an analysis-driven AI agent that links data and decisions — it not only interprets,
                    but also delivers answers. Intuitus excels at workplace and research analytics,
                    doing everything while you relax.
                </p>
                """
            )

        
        with st.container(key='homepage-intro'):
            # Intro video -----------------------------------------------------------
            st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

            # Call‑to‑actions --------------------------------------------------------
            cta, _ = st.columns([0.25, 0.75])
            with cta:
                if st.button("Try Intutius", use_container_width=True, type="primary"):
                    st.switch_page(PageRegistry.get_page("Waitlist"))
            


        # ─────────────────── FOOTER ─────────────────────


        st.image(self.logo_url, width=110)
        st.caption(
            'Intuitus, from the Latin for "vision", is an AI agent for data analysis that converts ideas into insight.'
        )
        st.caption("© 2025 Intuitus AI")

HomePage()