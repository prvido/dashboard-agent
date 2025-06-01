from abc import ABC, abstractmethod
from src.modules.util import query_warehouse
import streamlit as st
from uuid import uuid4

class BaseChart(ABC):
    fig = None
    def __init__(self, token: str, x: str, y: str, categories: list[str], query: str, warehouse_id: str, title: str):
        self.token = token
        self.x = x
        self.y = y
        self.categories = categories
        self.query = query
        self.warehouse_id = warehouse_id
        self.title = title
        self.set_data()
        self.set_fig()
        self.render()        
    
    def set_data(self) -> None:
        self.data = query_warehouse(self.token, self.warehouse_id, self.query)['data']

    @abstractmethod
    def set_fig(self) -> None:
        pass

    def render(self) -> None:
        if self.token:
            if self.fig is not None:
                self.fig.update_layout(height=400, margin=dict(l=70, r=20, t=45, b=70))
                st.plotly_chart(self.fig, use_container_width=True, border=True, theme='streamlit', key=str(uuid4()))
            else:
                st.dataframe(self.data, use_container_width=True, key=str(uuid4()))