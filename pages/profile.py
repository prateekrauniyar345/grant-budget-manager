# import dash
# from dash import html


# dash.register_page(__name__, path='/profile')

# def layout():
#     layout = html.Div([
#         html.H1('This is our profile page'),
#         html.Div('This is our profilwwwe page content.'),
#     ])
#     return layout
    

import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from models import User, Grant, GrantPersonnel
from flask_login import current_user
from db_utils import get_db_session
import pandas as pd

# Register the page
dash.register_page(__name__, path='/profile')

def layout():
    return html.Div([
        html.H3('User Profile', className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),
        dbc.Container([
            dbc.Row([
                dbc.Col(html.Div(id='user-profile-card'), width=4),
                dbc.Col(html.Div(id='user-grant-summary'), width=8),
            ], className="mb-5"),

            html.H4("Grant Statistics", className="text-left mb-3"),
            dbc.Row([
                dbc.Col(dcc.Graph(id='grant-count-bar'), width=6),
                dbc.Col(dcc.Graph(id='personnel-pie-chart'), width=6),
            ]),
        ], fluid=True)
    ])


@callback(
    Output('user-profile-card', 'children'),
    Output('user-grant-summary', 'children'),
    Output('grant-count-bar', 'figure'),
    Output('personnel-pie-chart', 'figure'),
    Input('user-profile-card', 'id')
)
def populate_profile(_):
    session = get_db_session()

    if not current_user.is_authenticated:
        return html.Div("User not logged in.", style={"color": "red"}), dash.no_update, dash.no_update, dash.no_update

    user = session.query(User).get(current_user.id)
    grants = session.query(Grant).filter_by(user_id=user.id).all()

    grant_data = []
    personnel_counts = {}

    for grant in grants:
        personnels = session.query(GrantPersonnel).filter_by(grant_id=grant.id).all()
        role_count = {}
        for p in personnels:
            role = p.position or "Unknown"
            role_count[role] = role_count.get(role, 0) + 1
            personnel_counts[role] = personnel_counts.get(role, 0) + 1

        grant_data.append({
            'title': grant.title,
            'agency': grant.funding_agency,
            'duration': grant.duration,
            'start_date': grant.start_date.strftime('%Y-%m-%d'),
            'end_date': grant.end_date.strftime('%Y-%m-%d'),
            'personnel_count': sum(role_count.values())
        })

    # --- User Card ---
    user_card = dbc.Card([
        dbc.CardHeader("User Info", className="fw-bold text-primary"),
        dbc.CardBody([
            html.P(f"Name: {user.first_name} {user.last_name}"),
            html.P(f"Username: {user.username}"),
            html.P(f"Email: {user.email}"),
            html.P(f"Joined On: {user.created_at.strftime('%Y-%m-%d')}")
        ])
    ], className="shadow")

    # --- Grants Table ---
    grants_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Title"),
            html.Th("Agency"),
            html.Th("Duration"),
            html.Th("Personnel"),
            html.Th("Start"),
            html.Th("End")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(grant['title']),
                html.Td(grant['agency']),
                html.Td(f"{grant['duration']} yrs"),
                html.Td(grant['personnel_count']),
                html.Td(grant['start_date']),
                html.Td(grant['end_date'])
            ]) for grant in grant_data
        ])
    ], bordered=True, hover=True, responsive=True, striped=True, className="shadow")

    # --- Bar Chart: Grant Counts by Agency ---
    df_grants = pd.DataFrame(grant_data)
    fig_bar = px.bar(df_grants, x='agency', color='agency', 
                     title='Grants by Funding Agency',
                     labels={'agency': 'Agency', 'count': 'Grants'})

    # --- Pie Chart: Personnel Distribution ---
    df_pie = pd.DataFrame({
        'Role': list(personnel_counts.keys()),
        'Count': list(personnel_counts.values())
    })
    fig_pie = px.pie(df_pie, names='Role', values='Count', title='Personnel Role Distribution')

    return user_card, grants_table, fig_bar, fig_pie
