import dash_bootstrap_components as dbc
import pandas as pd
from dash_rf.value_objects.mock import ativos
from dash_rf.value_objects.titulos import Titulo
from dash import dcc, Dash, Output, Input
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash_rf.componentes import ids
import plotly.express as px


def render_lista_ativos():
    df = pd.DataFrame([i.to_dict() for i in ativos])
    df['Montante'] = df['pu'] * df['qntde']
    novo_dict = {col: df[col].astype(str).tolist() for col in df.columns}
    df = pd.DataFrame(novo_dict)
    df.columns = ['PU',
                  'Indexador',
                  'Instrumento',
                  'Quantidade',
                  'Taxa',
                  'Emissor',
                  'Dt Compra',
                  'Vencimento',
                  'Montante']
    colunas = [ 'Dt Compra', 'Montante', 'Indexador', 'Instrumento', 'Taxa', 'Emissor', 'Vencimento']
    return dbc.Table.from_dataframe(df[colunas], striped=True, bordered=True, hover=True, size='sm')


class Graficos:

    @staticmethod
    def _pizza_por_isencao(ativos: list[Titulo]):
        df = pd.DataFrame([i.to_dict() for i in ativos])
        df['Montante'] = df['pu'] * df['qntde']
        df['IR'] = [ativo.aliquota_ir() for ativo in ativos]
        df = df.groupby('IR').agg({'Montante': 'sum'})
        df['colors'] = [px.colors.sequential.RdPu[color + 4] for color in range(len(df))]
        return go.Pie(labels=[f'IR: {str(round(i*100, 1))}%' for i in df.index],
                      values=df['Montante'].tolist(),
                      domain=dict(x=[0, 0.5]),
                      textinfo='label+percent',
                      hole=0.4,
                      textfont=dict(color='#FFFFFF'),
                      marker_colors=df['colors'])

    @staticmethod
    def _pizza_por_indexador(ativos: list[Titulo]):
        df = pd.DataFrame([i.to_dict() for i in ativos])
        df['Montante'] = df['pu'] * df['qntde']
        df['indexador'] = df['indexador'].astype(str)
        df = df.groupby('indexador').agg({'Montante': 'sum'})
        df['colors'] = [px.colors.sequential.RdPu[color + 5] for color in range(len(df))]
        return go.Pie(labels=df.index.tolist(),
                      values=df['Montante'].tolist(),
                      domain=dict(x=[0.50, 1]),
                      textinfo='label+percent',
                      hole=0.4,
                      textfont=dict(color='#FFFFFF'),
                      marker_colors=df['colors'])

    @staticmethod
    def _montante_por_emissor(ativos: list[Titulo]):
        df = pd.DataFrame([i.to_dict() for i in ativos])
        df['Montante'] = df['pu'] * df['qntde']
        df = df.groupby('emissor').agg({'Montante': 'sum'})
        df['colors'] = [px.colors.sequential.RdPu[color + 2] for color in range(len(df))]
        return go.Bar(x=df['Montante'].tolist(), y=df.index.tolist(), orientation='h', marker=dict(color=df['colors']))

    @staticmethod
    def _prazo_por_emissor(ativos: list[Titulo]):
        df = pd.DataFrame([i.to_dict() for i in ativos])
        df['Montante'] = df['pu'] * df['qntde']
        df['emissor'] = df['emissor'].astype(str)
        df['p'] = [i.prazo for i in ativos]
        montante_por_emissor = df.groupby('emissor').agg({'Montante': 'sum'})
        df['p'] = df['p'] * df['Montante']
        duration_por_emissor = df.groupby('emissor').agg({'p': 'mean'}) / montante_por_emissor.values
        df['colors'] = [px.colors.sequential.RdPu[color + 5] for color in range(len(df))]
        return go.Bar(x=duration_por_emissor.index.tolist(), y=duration_por_emissor['p'].tolist(),
                      marker=dict(color=df['colors']))

    @classmethod
    def render_graficos_pizza(cls, app: Dash, ativos: list[Titulo]):

        @app.callback(
            Output(ids.GRAFICOS_PIZZA, "figure"),
            Input(ids.BOTAO, 'n_clicks'))
        def update(_):
            fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],
                                subplot_titles=("Alíquotas", "Indexador"))

            fig.add_trace(cls._pizza_por_isencao(ativos), row=1, col=1)

            fig.add_trace(cls._pizza_por_indexador(ativos), row=1, col=2)

            fig.update_layout(showlegend=False,
                              paper_bgcolor='rgba(37,40,43,100)',
                              template='plotly_dark')
            fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')
            fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')

            return fig
        return dcc.Loading(dcc.Graph(id=ids.GRAFICOS_PIZZA), type='circle', delay_show=50)

    @classmethod
    def render_graficos_barra(cls, app: Dash, ativos: list[Titulo]):
        @app.callback(
            Output(ids.GRAFICOS_BAR, "figure"),
            Input(ids.BOTAO, 'n_clicks'))
        def update(_):
            fig = make_subplots(rows=1, cols=2, subplot_titles=("R$/Emissor", "Prazo/Emissor"))

            fig.add_trace(cls._montante_por_emissor(ativos), row=1, col=1)

            fig.add_trace(cls._prazo_por_emissor(ativos), row=1, col=2)

            fig.update_layout(showlegend=False,
                              paper_bgcolor='rgba(37,40,43,100)',
                              template='plotly_dark')
            fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')
            fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')

            return fig

        return dcc.Loading(dcc.Graph(id=ids.GRAFICOS_BAR), type='circle', delay_show=50)


def criar_layout(app: Dash):
    div = [dbc.Container(dbc.Button('Atualizar', id=ids.BOTAO)),
          dbc.Row(
            [
                dbc.Col(render_lista_ativos()),
                dbc.Col(
                    [dbc.Container(dbc.Row(Graficos.render_graficos_pizza(app, ativos))),
                    dbc.Container(dbc.Row(Graficos.render_graficos_barra(app, ativos)))]
                )
            ])]
    return div

