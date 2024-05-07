import dash_bootstrap_components as dbc
from dash import dcc
from dashboard_macroeconomia.componentes import ids


def render_sliders_mercado_ativos():
    slider_qntde_moedas = dcc.Slider(id=ids.SLIDER_MOEDAS, min=0.5, max=5, value=2.5, step=0.5)
    slider_pib = dcc.Slider(id=ids.SLIDER_PIB, min=1, max=10, value=5, step=1)
    slider_juros_estrangeiro = dcc.Slider(id=ids.SLIDER_JUROS_ESTRANGEIRO, min=1, max=15, value=5, step=1)
    slider_cambio_esperado = dcc.Slider(id=ids.SLIDER_CAMBIO_ESPERADO, min=1, max=10, value=5, step=1)
    slider_diferencial_de_risco = dcc.Slider(id=ids.SLIDER_DIFERENCIAL_RISCO, min=1, max=10, value=2, step=1)
    return [dbc.Row(dbc.Col([dbc.Label("Quantidade Moedas", width=5), slider_qntde_moedas])),
            dbc.Row(dbc.Col([dbc.Label("PIB", width=5), slider_pib])),
            dbc.Row(dbc.Col([dbc.Label("Juros Externo (%)", width=5), slider_juros_estrangeiro])),
            dbc.Row(dbc.Col([dbc.Label("Câmbio Esperado", width=5), slider_cambio_esperado])),
            dbc.Row(dbc.Col([dbc.Label("Diferencial de Risco (%)", width=5), slider_diferencial_de_risco]))]

