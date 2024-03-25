from dash import Dash
from dashboard import layout


def main():
    app = Dash()
    app.title = "Trednd-Following Evaluator"
    app.layout = layout.create_layout(app)
    app.run()


if __name__ == "__main__":
    main()
