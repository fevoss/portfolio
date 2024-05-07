from dash import Output, Input, callback, dcc
import numpy as np
import plotly.graph_objects as go
from dashboard_macroeconomia.componentes import ids


def render_grafico_pdj():
    @callback(
        Output(ids.GRAFICO_PDJ, "figure"),
        [Input(ids.SLIDER_JUROS_LOCAL, "value"),
         Input(ids.SLIDER_JUROS_ESTRANGEIRO, "value"),
         Input(ids.SLIDER_CAMBIO_ESPERADO, "value"),
         Input(ids.SLIDER_DIFERENCIAL_RISCO, "value")],)
    def update_pdj(juros_local: float,
                   juros_estrangeiro: float,
                   cambio_esperado: float,
                   diferencial_risco: float):
        fig = go.Figure()
        x = np.arange(1, 200, 0.1) / 100

        # Retorno Esperado do Exterior
        y = [cambio_esperado / (1 + i - (juros_estrangeiro/100) - (diferencial_risco/100)) for i in x]
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="Retorno Externo",
            line=dict(color="black")))

        # Retorno Esperado Doméstico
        y = np.arange(0, 10, 0.1)
        fig.add_trace(go.Scatter(
            x=[juros_local/100] * len(y),
            y=y,
            mode="lines",
            name="Retorno Local",
            line=dict(color="red")))

        fig.add_trace(go.Scatter(
            x=[juros_local/100],
            y=[cambio_esperado / (1 + juros_local/100 - juros_estrangeiro/100 - diferencial_risco/100)],
            mode="markers",
            name="Câmbio", marker=dict(size=10)))

        fig.update_layout(title_text="Paridade Descoberta de Juros", title_font_size=20, title_x=0.5,
                          yaxis_range=[0, 10],
                          xaxis_range=[0, 2],
                          template='seaborn')
        return fig
    return dcc.Graph(id=ids.GRAFICO_PDJ)