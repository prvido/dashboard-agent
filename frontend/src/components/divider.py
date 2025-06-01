import streamlit as st

class DividerComponent:
    def __init__(self, color="#555555", thickness="1px", margin="0"):
        self.color = color
        self.thickness = thickness
        self.margin = margin
        self.render()

    def render(self):
        st.markdown(
            f"""
            <hr style="
                border: none;
                border-top: {self.thickness} solid {self.color};
                margin: {self.margin};
            "/>
            """,
            unsafe_allow_html=True
        )