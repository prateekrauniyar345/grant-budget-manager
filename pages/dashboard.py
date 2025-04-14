import dash
from dash import html, dcc, Input, Output, State, callback, ALL, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
from models import Grant, User
from db_utils import get_db_session
from flask_login import current_user
import io
import base64
from datetime import datetime

# Register the page
dash.register_page(__name__, path='/dashboard')

# Define the layout
def layout():
    return html.Div([
        html.H3('Available Budgets', className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),

        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div(id='table-container'),
                ], width=12),
            ], className="mb-4"),


            # Hidden div for storing download data
            html.Div(id='download-data', style={'display': 'none'}),
            dcc.Download(id="download-excel")
        ], fluid=True)
    ])

# Callback to fetch and display grants
@callback(
    Output('table-container', 'children'),
    Input('table-container', 'id'),  # Trigger on button click
    prevent_initial_call=False
)
def display_grants(id):
    # Get the database session
    session = get_db_session()

    try:
        # Ensure the current user is logged in
        if not current_user.is_authenticated:
            return html.Div("You must be logged in to view your grants.", style={"color": "red"})

        # Fetch the grants created by the current user
        grants = session.query(Grant).filter(Grant.user_id == current_user.id).all()

        # If no grants found, return a message with an image
        if not grants:
            return html.Div([
                html.Img(src='assets/images/nogrants1.png', style={"width": "500px", "height":"100%", "display": "block", "margin": "auto"}),
                html.Div("No grants found.", style={"color": "gray", "text-align": "center", "margin-top": "10px"})
            ])

        # Prepare data for displaying in rows and columns
        rows = []
        for idx, grant in enumerate(grants, 1):
            # Determine if the row index is even
            row_style = {'backgroundColor': '#f8f9fa'} if idx % 2 == 0 else {}
            rows.append(
                dbc.Row([
                    # dbc.Col(html.Div(str(idx)), width=1),
                    dbc.Col(html.Div(grant.title), width=2),
                    dbc.Col(html.Div(grant.created_at.strftime('%Y-%m-%d')), width=2),
                    dbc.Col(html.Div(grant.funding_agency), width=1),
                    dbc.Col(html.Div(grant.start_date.strftime('%Y-%m-%d')), width=2),
                    dbc.Col(html.Div(grant.end_date.strftime('%Y-%m-%d')), width=2),
                    dbc.Col(html.Div([
                        dbc.Button("Edit", n_clicks=0,  id={'type': 'edit-btn', 'index': grant.id}, className="btn btn-warning btn-sm me-2"),
                        dbc.Button("Delete", n_clicks=0,  id={'type': 'delete-btn', 'index': grant.id}, className="btn btn-danger btn-sm me-2"),
                        dbc.Button("Manage", n_clicks=0,  id={'type': 'manage-btn', 'index': grant.id}, className="btn btn-info btn-sm me-2"),
                        dbc.Button("Download Excel", n_clicks=0,  id={'type': 'download-excel-btn', 'index': grant.id}, className="btn btn-success btn-sm me-2", ), 
                    ], style={"display": "flex", "gap": "0px", }), width=3)
                ], className="mb-2 p-2 rounded", style=row_style)
            )

        # Display the table
            table = html.Div([
                dbc.Row([
                    # dbc.Col(html.Div("SN", className="text-center p-2"), width=1),
                    dbc.Col(html.Div("Grant Name", className="text-left p-2"), width=2),
                    dbc.Col(html.Div("Date Created", className="text-left p-2"), width=2),
                    dbc.Col(html.Div("Funding Agency", className="text-left p-2"), width=1),
                    dbc.Col(html.Div("Start Date", className="text-left p-2"), width=2),
                    dbc.Col(html.Div("End Date", className="text-left p-2"), width=2),
                    dbc.Col(html.Div("Actions", className="text-left p-2"), width=3)
                ], className="fw-bold mb-2 bg-light border rounded ", style={"font-size": "1rem", }),  # Styled header row
                *rows  # Adding all the rows dynamically
            ])


        return table

    except Exception as err:
        return html.Div(f"Error: {str(err)}", style={"color": "red"})

    finally:
        session.close()  # Close the session


@callback(
    Output('table-container', 'children', allow_duplicate=True),
    Input({'type': 'delete-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def delete_grant(n_clicks_list):
    # Check if the delete button was clicked (ensure n_clicks_list is not empty)
    if not any(n_clicks_list):
        return dash.no_update  # No update if no button was clicked

    # Extract the button ID from the triggered property
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    # Extract the grant ID
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    grant_id = eval(button_id)['index']  # Extract the index (grant ID)

    # Get the database session
    session = get_db_session()

    try:
        # Ensure the current user is logged in
        if not current_user.is_authenticated:
            return html.Div("You must be logged in to delete a grant.", style={"color": "red"})

        # Fetch the grant by ID
        grant_to_delete = session.query(Grant).get(grant_id)

        # Ensure the current user is the owner of the grant
        if grant_to_delete.user_id != current_user.id:
            return html.Div("You do not have permission to delete this grant.", style={"color": "red"})

        # Delete the grant from the database
        session.delete(grant_to_delete)
        session.commit()

        # Refresh the table after deletion
        return display_grants(0)

    except Exception as err:
        return html.Div(f"Error: {str(err)}", style={"color": "red"})

    finally:
        session.close()


# Callback to handle Excel download
@callback(
    Output("download-excel", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_excel(n_clicks):
    # Get the database session
    session = get_db_session()

    try:
        # Ensure the current user is logged in
        if not current_user.is_authenticated:
            return None

        # Fetch the grants created by the current user
        grants = session.query(Grant).filter(Grant.user_id == current_user.id).all()

        # Prepare data for the Excel file
        grants_data = []
        for grant in grants:
            grants_data.append({
                'Grant Name': grant.title,
                'Date Created': grant.created_at.strftime('%Y-%m-%d'),
                'Funding Agency': grant.funding_agency,
                'Start Date': grant.start_date.strftime('%Y-%m-%d'),
                'End Date': grant.end_date.strftime('%Y-%m-%d'),
            })

        # Convert to DataFrame
        df = pd.DataFrame(grants_data)

        # Save to Excel in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Grants')
        buffer.seek(0)

        # Return the Excel file for download
        return dcc.send_bytes(buffer.getvalue(), filename="grants.xlsx")

    except Exception as err:
        return html.Div(f"Error: {str(err)}", style={"color": "red"})

    finally:
        session.close()
