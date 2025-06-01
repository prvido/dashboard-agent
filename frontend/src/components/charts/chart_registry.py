import streamlit as st
from src.components.charts.base import BaseChart

class ChartRegistry:
    _charts: dict[str, BaseChart] = {}

    @classmethod
    def register(cls, chart_type: str, chart_class: BaseChart) -> BaseChart:
        """Register a chart class with the registry."""
        cls._charts[chart_type] = chart_class
        return chart_class

    @classmethod
    def get_chart(cls, chart_type: str) -> BaseChart:
        """Get a chart class by type."""
        return cls._charts[chart_type]

from src.components.charts.bar import BarChart
from src.components.charts.line import LineChart
from src.components.charts.table import Table
from src.components.charts.donut import DonutChart
from src.components.charts.scatter import ScatterChart

ChartRegistry.register("bar", BarChart)
ChartRegistry.register("line", LineChart)
ChartRegistry.register("table", Table)
ChartRegistry.register("donut", DonutChart)
ChartRegistry.register("scatter", ScatterChart)
