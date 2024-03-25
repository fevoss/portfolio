from dash import html, Dash, dcc
from . import ids
from dashboard.lista_ativos import ativos


def render(app: Dash) -> html.Div:

    return html.Div(children=[
        html.H3('Preço'),
        dcc.Dropdown(multi=False,
                     options=[{'label': ' '.join([i.upper() for i in cliente.split("_")]), 'value': cliente}
                              for cliente in ativos],
                     value=ativos,
                     id=ids.ATIVOS_DROPDOWN)
    ])
