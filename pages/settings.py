import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

# Register the settings page
dash.register_page(__name__, path='/settings')

# Page layout
def layout():
    return html.Div([
        dcc.Store(id="user-theme", storage_type="local"),

        html.H3("Settings", className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),

        dbc.Container([
            html.H5("Display Preferences", className="fw-bold mb-3"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Choose Theme"),
                    dbc.RadioItems(
                        id="theme-selector",
                        options=[
                            {"label": "Light", "value": "light"},
                            {"label": "Dark", "value": "dark"},
                        ],
                        value="light",
                        inline=True,
                        className="mb-3"
                    )
                ], width=6),

                dbc.Col([
                    dbc.Label("Font Size"),
                    dbc.Select(
                        id="font-size-selector",
                        options=[
                            {"label": "Small", "value": "sm"},
                            {"label": "Medium", "value": "md"},
                            {"label": "Large", "value": "lg"},
                        ],
                        value="md",
                        className="mb-3"
                    )
                ], width=6),
            ]),

            html.Hr(),

            html.Div("More settings coming soon...", className="text-muted fst-italic mt-2 mb-5"),
        ], fluid=True)
    ])
