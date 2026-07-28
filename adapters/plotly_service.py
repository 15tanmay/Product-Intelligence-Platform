import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Corporate colour palette consistent across all charts
_PALETTE = px.colors.qualitative.Plotly
_TEMPLATE = "plotly_white"


class PlotlyService:
    """Centralised factory for Plotly figures used across all dashboard pages."""

    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str,
        color: str | None = None,
        text: str | None = None,
    ) -> go.Figure:
        fig = px.bar(
            df, x=x, y=y, title=title, color=color, text=text,
            color_discrete_sequence=_PALETTE, template=_TEMPLATE,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(title_font_size=16, margin=dict(t=60))
        return fig

    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str,
        color: str | None = None,
    ) -> go.Figure:
        fig = px.line(
            df, x=x, y=y, title=title, color=color,
            color_discrete_sequence=_PALETTE, template=_TEMPLATE, markers=True,
        )
        fig.update_layout(title_font_size=16, margin=dict(t=60))
        return fig

    @staticmethod
    def create_pie_chart(
        df: pd.DataFrame,
        names: str,
        values: str,
        title: str,
    ) -> go.Figure:
        fig = px.pie(
            df, names=names, values=values, title=title,
            color_discrete_sequence=_PALETTE, template=_TEMPLATE,
            hole=0.4,
        )
        fig.update_layout(title_font_size=16, margin=dict(t=60))
        return fig

    @staticmethod
    def create_grouped_bar(
        df: pd.DataFrame,
        x: str,
        y: str,
        color: str,
        title: str,
        barmode: str = "group",
    ) -> go.Figure:
        fig = px.bar(
            df, x=x, y=y, color=color, title=title, barmode=barmode,
            color_discrete_sequence=_PALETTE, template=_TEMPLATE,
        )
        fig.update_layout(title_font_size=16, margin=dict(t=60))
        return fig

    @staticmethod
    def create_scatter(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: str,
        color: str | None = None,
        size: str | None = None,
        hover_data: list | None = None,
    ) -> go.Figure:
        fig = px.scatter(
            df, x=x, y=y, title=title, color=color, size=size,
            hover_data=hover_data, color_discrete_sequence=_PALETTE,
            template=_TEMPLATE,
        )
        fig.update_layout(title_font_size=16, margin=dict(t=60))
        return fig

    @staticmethod
    def create_heatmap(
        data: pd.DataFrame,
        title: str,
        x_label: str = "",
        y_label: str = "",
    ) -> go.Figure:
        fig = go.Figure(
            data=go.Heatmap(
                z=data.values,
                x=data.columns.tolist(),
                y=data.index.tolist(),
                colorscale="Blues",
                text=data.values,
                texttemplate="%{text:.0f}",
            )
        )
        fig.update_layout(
            title=title, title_font_size=16,
            xaxis_title=x_label, yaxis_title=y_label,
            template=_TEMPLATE, margin=dict(t=60),
        )
        return fig

    @staticmethod
    def create_funnel(labels: list, values: list, title: str) -> go.Figure:
        fig = go.Figure(go.Funnel(y=labels, x=values))
        fig.update_layout(title=title, title_font_size=16, template=_TEMPLATE)
        return fig
