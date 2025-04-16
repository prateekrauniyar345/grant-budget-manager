import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from flask_login import logout_user

dash.register_page(__name__, path='/logout')

def layout():
    return html.Div([
        html.H3("Logout", className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),

        dbc.Container([
            html.P("Click the button below to log out.", className="mb-4"),
            dbc.Button("Log Out", id="open-logout-modal", color="danger"),

            # Logout confirmation modal
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Confirm Logout")),
                dbc.ModalBody("Are you sure you want to log out?"),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-logout", className="ms-auto", color="secondary"),
                    dcc.Location(id="logout-redirect", refresh=True),  # For redirect
                    dbc.Button("Yes, Log Out", id="confirm-logout", color="danger"),
                ])
            ],
            id="logout-modal",
            is_open=False,
            centered=True
            ),
        ], className="text-center", fluid=True),
    ])

# Toggle modal open/close
@callback(
    Output("logout-modal", "is_open"),
    Input("open-logout-modal", "n_clicks"),
    Input("cancel-logout", "n_clicks"),
    State("logout-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_modal(open_click, cancel_click, is_open):
    triggered = dash.ctx.triggered_id
    if triggered in ["open-logout-modal", "cancel-logout"]:
        return not is_open
    return is_open

# Perform redirect on confirmation
@callback(
    Output("logout-redirect", "pathname"),
    Input("confirm-logout", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n):
    logout_user()  # Clear session
    return "/login"  # Redirect after logout
