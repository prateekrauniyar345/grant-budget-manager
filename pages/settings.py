import dash
from dash import html


dash.register_page(__name__, path='/settings')

def layout():
    layout = html.Div([
        html.H1('This is our settings page'),
        html.Div('This is our settings page content.'),
    ])
    return layout
    