import dash_bootstrap_components as dbc


def renderizar_barra_de_navegacao():
    barra = dbc.NavbarSimple(
        children=dbc.NavItem(dbc.NavLink("Mercado de Ativos", href='/')),
        brand='Macroeconomia',
        brand_href='/',
        color='dark',
        dark=True
    )
    return barra
