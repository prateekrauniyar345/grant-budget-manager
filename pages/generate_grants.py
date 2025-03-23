import dash
from dash import html


dash.register_page(__name__, path='/generate_grants')

def layout():
    layout = html.Div([
        html.H1('This is our generate_grants page'),
        html.Div('This is our generate_grants page content.'),
    ])
    return layout
    