from dash import Dash, html
from . import grafico_preco
from . import dropdown_ativos


def create_layout(app: Dash) -> html.Div:
    return html.Div(className='app-div', children=[html.H1(app.title),
                                                   html.Hr(),
                                                   html.Div(className='dropdown-container',
                                                            children=dropdown_ativos.render(app)),
                                                   grafico_preco.render(app)])
