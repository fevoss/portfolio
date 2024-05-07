from dash import Dash
from dash_bootstrap_components.themes import SLATE
from dashboard_macroeconomia.componentes.layout import criar_layout


# Olhar isso aqui para criar uma animação melhor
# https://dash-example-index.herokuapp.com/animations

def main(debug=True) -> None:
    app = Dash(external_stylesheets=[SLATE], use_pages=True)
    app.title = "Macroeconomia"
    app.layout = criar_layout()
    app.run(debug=debug)


if __name__ == "__main__":
    main(True)
