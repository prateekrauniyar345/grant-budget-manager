import dash
from dash import html


dash.register_page(__name__, path='/profile')

def layout():
    layout = html.Div([
        html.H1('This is our profile page'),
        html.Div('This is our profile page content.'),
    ])
    return layout
    