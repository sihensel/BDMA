from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)
#app = Dash(__name__, use_pages=True)
app.config.suppress_callback_exceptions = True

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#13173C",
    "background": "#13173C",
    "color": "white",
}


CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Dashboard", className="display-7"),
        html.Hr(),
        html.P(
            "Ukraine War Tweet history", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Bots", href="/botDash", active="exact"),
                dbc.NavLink("rawData News", href="/rawNewsData", active="exact"),
                dbc.NavLink("rawData Tweets", href="/rawTweetsData", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(dash.page_container, style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=False)