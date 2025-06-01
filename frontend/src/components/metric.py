import streamlit as st

class MetricComponent:
    def __init__(self, label: str, value: str, background_color: str = 'rgba(38, 39, 48, 0)', decimal_places: int = 1):
        self.label = label
        self.value = value
        self.background_color = background_color
        self.decimal_places = decimal_places
        self.render()

    def format_number(self, value: str) -> str:
        try:
            num = float(value)
            format_str = f".{self.decimal_places}f"
            if num >= 1_000_000_000:
                return f"{num/1_000_000_000:{format_str}}B"
            elif num >= 1_000_000:
                return f"{num/1_000_000:{format_str}}M"
            elif num >= 1_000:
                return f"{num/1_000:{format_str}}k"
            else:
                return f"{num:{format_str}}"
        except (ValueError, TypeError):
            return value

    def render(self):
        formatted_value = self.format_number(self.value)
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; background-color: {self.background_color}; padding: 0px;">
                <span style="font-size: 14px; padding: 0px; margin: 0px;">{self.label}</span>
                <span style="font-size: 36px; padding: 0px; margin: 0px;">{formatted_value}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
