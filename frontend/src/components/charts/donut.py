from src.components.charts.base import BaseChart
import plotly.express as px

class DonutChart(BaseChart):

    def __init__(self, token: str, x: str, y: str, categories: list[str], query: str, warehouse_id: str, title: str):
        super().__init__(token, x, y, categories, query, warehouse_id, title)

    def set_fig(self) -> None:
        self.fig = px.pie(self.data, values=self.y, names=self.x, title=self.title, hole=0.4) 