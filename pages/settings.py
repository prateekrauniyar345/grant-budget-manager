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




@callback(
    Output("theme-link",     "href"),
    Output("page-container",  "className"),
    Input("user-theme",       "data"),
    prevent_initial_call=True,
)
def apply_user_preferences(pref):
    # 1) Safe‐guard defaults
    if not isinstance(pref, dict):
        pref = {"theme":"light","font_size":"md"}

    theme     = pref.get("theme",    "light")
    font_size = pref.get("font_size","md")

    # 2) Theme URL (light vs. your dark choice)
    theme_url = (
        dbc.themes.BOOTSTRAP
        if theme == "light"
        else dbc.themes.SUPERHERO
    )

    # 3) Font‐size utility
    fs_map    = {"sm":"fs-6","md":"fs-5","lg":"fs-4"}
    fs_class  = fs_map.get(font_size, "fs-5")

    # 4) Text color: white for any dark theme
    text_class = "" if theme == "light" else "text-white"

    # 5) Build wrapper class preserving main_body
    classes = ["main_body", fs_class, text_class]
    wrapper_class = " ".join(filter(None, classes))

    return theme_url, wrapper_class



@callback(
    Output("user-theme", "data", allow_duplicate=True),
    Input("theme-selector", "value"),
    Input("font-size-selector", "value"),
    State("user-theme", "data"),
    prevent_initial_call=True
)
def save_user_preferences(theme, font_size, current_data):
    if not isinstance(current_data, dict):
        current_data = {}

    # Only update fields that changed
    updated = current_data.copy()
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "theme-selector":
        updated["theme"] = theme
    elif trigger_id == "font-size-selector":
        updated["font_size"] = font_size

    return updated
@callback(
    Output("theme-selector", "value"),
    Output("font-size-selector", "value"),
    Input("user-theme", "data")
)
def load_preferences(pref):
    if not isinstance(pref, dict):
        pref = {"theme": "light", "font_size": "md"}
    return pref.get("theme"), pref.get("font_size")