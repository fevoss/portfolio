from dash import Output, Input, callback, dcc
from dashboard_macroeconomia.api.brasil import obter_ultima_curva_pre_disponivel, obter_historico_embi, obter_dolar_esperado
from dashboard_macroeconomia.api.eua import UsaMacro
import plotly.graph_objects as go
from dashboard_macroeconomia.componentes import ids
from plotly.subplots import make_subplots


def render_grafico_complementares_mercado_ativos():
    @callback(
        Output(ids.GRAFICO_COMPLEMENTARES_MERCADO_ATIVOS, "figure"),
        [Input(ids.BOTAO_ATUALIZAR, "n_clicks")])
    def update_grafico_curva_juros_brasil(_: float):

        cor_das_linhas = "#FF8C00"

        fig = make_subplots(rows=1, cols=4, subplot_titles=("Plot 1", "Plot 2", "Plot 3", "Plot 4"))
        curva_juros = obter_ultima_curva_pre_disponivel()
        fig.add_trace(go.Scatter(
            x=curva_juros.index.tolist(),
            y=curva_juros.tolist(),
            mode="lines",
            line=dict(color=cor_das_linhas)), row=1, col=1)

        embi_mais = obter_historico_embi() / 10000
        fig.add_trace(go.Scatter(
            x=embi_mais.index.tolist(),
            y=embi_mais.tolist(),
            mode="lines",
            line=dict(color=cor_das_linhas)), row=1, col=2)

        dolar_esperado = obter_dolar_esperado()
        fig.add_trace(go.Scatter(
            x=dolar_esperado.index.tolist(),
            y=dolar_esperado.tolist(),
            mode="lines",
            line=dict(color=cor_das_linhas)), row=1, col=3)

        curva_eua = UsaMacro().obter_ultima_curva_pre_disponivel()
        fig.add_trace(go.Scatter(
            x=curva_eua.index.tolist(),
            y=curva_eua.tolist(),
            mode="lines",
            line=dict(color=cor_das_linhas)), row=1, col=4)

        fig.update_layout(showlegend=False,
                          paper_bgcolor='rgba(37,40,43,100)',
                          template='plotly_dark')
        fig.update_xaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')
        fig.update_yaxes(showgrid=False, zeroline=False, showline=True, linecolor='white')

        fig.update_yaxes(tickformat='.2%', row=1, col=1)  # Gráfico Curva de Juros
        fig.update_yaxes(tickformat='.2%',  row=1, col=2)  # Gráfico Embi +
        fig.update_yaxes(tickprefix='R$', tickformat='.2f', row=1, col=3)  # Gráfico Embi +
        fig.update_yaxes(tickformat='.2%', row=1, col=4)  # Gráfico Curva de Juros

        names = {'Plot 1': f'Curva de Juros | {curva_juros.name}',
                 'Plot 2': f"EMBI (+) | {embi_mais.index[-1].strftime('%d/%m/%y')}",
                 'Plot 3': f"Expectativa Câmbio | {dolar_esperado.name.strftime('%d/%m/%y')}",
                 'Plot 4': f'Curva de Juros EUA | {curva_juros.name}'}
        fig.for_each_annotation(lambda a: a.update(text=names[a.text]))

        return fig

    return dcc.Loading(dcc.Graph(id=ids.GRAFICO_COMPLEMENTARES_MERCADO_ATIVOS), type='circle', delay_show=50)

