from dash import html, page_container
import dash_bootstrap_components as dbc
from dashboard_macroeconomia.componentes.barra_de_navegacao import renderizar_barra_de_navegacao


def criar_layout():
    footer = dbc.Container(dbc.Row(dbc.Col(html.A("Felipe Lima | GitHub", href='https://github.com/fevoss/portfolio'),
                                           align='left')), className='footer',
                           fluid=True)
    return html.Div([renderizar_barra_de_navegacao(), page_container, footer])


