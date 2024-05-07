import dash_bootstrap_components as dbc
from dash import register_page
from dashboard_macroeconomia.componentes.sliders_pdj import render_sliders_pdj
from dashboard_macroeconomia.componentes.grafico_pdj import render_grafico_pdj

register_page(__name__, name='PDJ', path='/')

layout = dbc.Row([dbc.Col(render_sliders_pdj(), width=5), dbc.Col(render_grafico_pdj())])
