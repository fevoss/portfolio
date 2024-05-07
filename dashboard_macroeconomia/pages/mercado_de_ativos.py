import dash_bootstrap_components as dbc
from dash import register_page
from dashboard_macroeconomia.componentes.sliders_mercado_ativos import render_sliders_mercado_ativos
from dashboard_macroeconomia.componentes.grafico_mercado_ativos import render_grafico_mercado_de_ativos

register_page(__name__, name='Mercado de Ativos', path='/')

layout = dbc.Row([dbc.Col(render_sliders_mercado_ativos(), width=5), dbc.Col(render_grafico_mercado_de_ativos())])
