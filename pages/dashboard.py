import dash
from dash import html


dash.register_page(__name__, path='/dashboard')

def layout():
    layout = html.Div([
        html.H1('This is our dashbaord page'),
        html.Div('This is our dashbaord page content.'),
    ])
    return layout
    