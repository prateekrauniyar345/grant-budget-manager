import dash
from dash import html


dash.register_page(__name__, path='/logout')

def layout():
    layout = html.Div([
        html.H1('This is our logout page'),
        html.Div('This is our logout page content.'),
    ])
    return layout
    