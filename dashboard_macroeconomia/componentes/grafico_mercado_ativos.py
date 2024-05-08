from dash import Output, Input, callback, dcc
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from dashboard_macroeconomia.componentes import ids


def pdj(fig: go.Figure,
        juros_local: float,
        juros_estrangeiro: float,
        cambio_esperado: float,
        diferencial_risco: float):
    x = np.arange(1, 200, 0.1) / 100

    # Retorno Esperado do Exterior
    y = [cambio_esperado / (1 + i - (juros_estrangeiro / 100) - (diferencial_risco / 100)) for i in x]
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines",
        name="Ret. Estrangeiro",
        line=dict(color="#FF8C00")), row=1, col=1)

    # Retorno Esperado Doméstico
    y = np.arange(0, 10, 0.1)
    fig.add_trace(go.Scatter(
        x=[juros_local] * len(y),
        y=y,
        mode="lines",
        name="Ret. Local",
        line=dict(color="grey")), row=1, col=1)

    cambio_eq = cambio_esperado / (1 + juros_local - juros_estrangeiro / 100 - diferencial_risco / 100)
    fig.add_trace(go.Scatter(
        x=[juros_local],
        y=[cambio_eq],
        mode="markers",
        name="Equilíbrio", marker=dict(size=10, color="#FF8C00")), row=1, col=1)


def mercado_monetario(fig: go.Figure, moedas: float, preco: float, pib: float):
    demanda_real_por_liquidez = np.arange(0.1, 10, 0.1) / preco
    sensibilidade = 0.6
    pib = pib / 7500
    beta_pib = 1
    beta_liquidez_real = 4
    juros = beta_liquidez_real * np.power(demanda_real_por_liquidez, -sensibilidade) * \
            beta_pib * np.power(pib, 1 - sensibilidade)
    fig.add_trace(go.Scatter(
        x=juros,
        y=demanda_real_por_liquidez,
        mode="lines",
        name="Liquidez Real",
        line=dict(color="#FF8C00")), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=np.arange(0, 2, 1),
        y=[moedas / preco] * 2,
        mode="lines",
        name="Oferta Monetária Real",
        line=dict(color="grey")), row=2, col=1)

    juros_local = beta_liquidez_real * np.power(moedas / preco, -sensibilidade) \
                  * beta_pib * np.power(pib, 1 - sensibilidade)
    fig.add_trace(go.Scatter(
        x=[juros_local],
        y=[moedas / preco],
        mode="markers",
        name="Juros Local - BACEN", marker=dict(size=10, color="#FF8C00"),
        showlegend=False), row=2, col=1)

    return juros_local


def render_grafico_mercado_de_ativos():
    @callback(
        Output(ids.GRAFICO_MERCADO_ATIVOS, "figure"),
        [Input(ids.SLIDER_MOEDAS, "value"),
         Input(ids.SLIDER_PIB, "value"),
         Input(ids.SLIDER_JUROS_ESTRANGEIRO, "value"),
         Input(ids.SLIDER_CAMBIO_ESPERADO, "value"),
         Input(ids.SLIDER_DIFERENCIAL_RISCO, "value")], )
    def update_grafico_mercado_ativos(moedas: float,
                                      pib: float,
                                      juros_estrangeiro: float,
                                      cambio_esperado: float,
                                      diferencial_risco: float):

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0)
        juros_local = mercado_monetario(fig=fig, moedas=moedas, preco=1, pib=pib)
        pdj(fig, juros_local, juros_estrangeiro, cambio_esperado, diferencial_risco)

        fig.update_yaxes(range=[0, 7], showticklabels=True, row=1, col=1)
        fig.update_yaxes(range=[6, 0], showticklabels=True, row=2, col=1)
        fig.update_layout(title_text=f"Mercado de Ativos | Teórico",
                          title_font_size=15, title_x=0.5,
                          paper_bgcolor='rgba(37,40,43,100)',
                          template='plotly_dark',
                          showlegend=False)
        fig.update_xaxes(range=[0, 1], showticklabels=False, row=1, col=1, showgrid=False,  zeroline=False,
                         showline=True, linecolor='white')
        fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor='white', row=1, col=1,
                         title="Câmbio")
        fig.update_xaxes(range=[0, 1], showticklabels=True, row=2, col=1, showgrid=False, zeroline=False,
                         showline=True, linecolor='white', title='Retorno Local', tickformat='.0%')
        fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor='white', row=2, col=1,
                         title="Liquidez Real")

        return fig

    return dcc.Loading(dcc.Graph(id=ids.GRAFICO_MERCADO_ATIVOS), type='circle', delay_show=50)
