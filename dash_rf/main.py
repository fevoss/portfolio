from dash import Dash
from dash_bootstrap_components.themes import SLATE
from dash_rf.componentes.layout import criar_layout


def main(debug=True) -> None:
    app = Dash(external_stylesheets=[SLATE])
    app.title = "Renda Fixa"
    app.layout = criar_layout(app)
    app.run(debug=debug)


if __name__ == "__main__":
    main(True)
