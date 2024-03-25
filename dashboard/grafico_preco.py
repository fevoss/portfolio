import pandas as pd
from dash import Dash, html, dcc
from dashboard import ids
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import itertools as it

df = pd.read_excel('ativos.xlsx', index_col=0)


def render(app: Dash = None) -> html.Div:
    @app.callback(
        Output(ids.LINE_CHART, 'children'), Input(ids.ATIVOS_DROPDOWN, 'value'))
    def update_chart(ativo: str) -> html.Div:
        serie_temporal = df[ativo]

        mme_21: pd.Series = serie_temporal.ewm(span=21).mean()
        mme_100: pd.Series = serie_temporal.ewm(span=100).mean()

        fig = go.Figure()

        colors = (mme_21 > mme_100).astype(int).dropna()

        verde = colors == 1
        vermelho = colors == 0

        colors.loc[verde] = 'blue'
        colors.loc[vermelho] = 'red'
        locs = colors.index
        colors = colors.tolist()

        x_pairs = it.pairwise(locs)
        y_pairs = it.pairwise(serie_temporal.loc[locs].tolist())

        for x, y, color in zip(x_pairs, y_pairs, colors):
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode='lines',
                    line={'color': color},
                    showlegend=False
                )
            )
        fig.update_layout(title=ativo)
        return html.Div(dcc.Graph(figure=fig), id=ids.LINE_CHART)
    return html.Div(id=ids.LINE_CHART)

