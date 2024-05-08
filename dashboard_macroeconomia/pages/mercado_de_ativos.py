import dash_bootstrap_components as dbc
from dash import register_page, html
from dashboard_macroeconomia.componentes.sliders_mercado_ativos import render_sliders_mercado_ativos
from dashboard_macroeconomia.componentes.grafico_mercado_ativos import render_grafico_mercado_de_ativos
from dashboard_macroeconomia.componentes.graficos_complementares_mercado_ativo import\
    render_grafico_complementares_mercado_ativos
from dashboard_macroeconomia.componentes.ids import BOTAO_ATUALIZAR

register_page(__name__, name='Mercado de Ativos', path='/')

layout = html.Div(children=[dbc.Container(dbc.Row([dbc.Col(render_sliders_mercado_ativos(), width=4),
                                                   dbc.Col([render_grafico_mercado_de_ativos()])])),
                            dbc.Container(dbc.Row([dbc.Col(dbc.Button('Atualizar', id=BOTAO_ATUALIZAR)),
                                                   render_grafico_complementares_mercado_ativos()]))])