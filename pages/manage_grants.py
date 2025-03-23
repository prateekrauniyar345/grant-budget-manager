import dash
from dash import html


dash.register_page(__name__, path='/manage_grants')

def layout():
    layout = html.Div([
        html.H1('This is our manage_grants page'),
        html.Div('This is our manage_grants page content.'),
    ])
    return layout
    