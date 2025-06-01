from src.components.charts.base import BaseChart

class Table(BaseChart):
    def __init__(self, token: str, x: str, y: str, categories: list[str], query: str, warehouse_id: str, title: str):
        super().__init__(token, x, y, categories, query, warehouse_id, title)

    def set_fig(self) -> None:
        pass
        

