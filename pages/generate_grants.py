import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import date
from models import Grant, User
from db_utils import get_db_session
from flask_login import current_user

# Register the page
dash.register_page(__name__, path='/generate-grants')

# Success and Failure Toasts
success_toast = dbc.Toast(
    "Grant successfully submitted!",
    id="success-toast",
    is_open=False,
    duration=4000,
    header="Success",
    icon="success",
    className="mb-3",
    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
)

failure_toast = dbc.Toast(
    "Error: Grant submission failed.",
    id="failure-toast",
    is_open=False,
    duration=4000,
    header="Failure",
    icon="danger",
    className="mb-3",
    style={"position": "fixed", "top": 66, "right": 10, "width": 350},
)

# Define Container
container = html.Div(
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Grant Title"),
                    dbc.Input(id='grant-title', type='text', placeholder="Enter Grant Title", className="mb-3"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Funding Agency"),
                    dbc.Select(
                        id='funding-agency',
                        options=[
                            {'label': 'NSF', 'value': 'NSF'},
                            {'label': 'NIH', 'value': 'NIH'},
                            {'label': 'Other', 'value': 'Other'}
                        ],
                        placeholder="Select Funding Agency",
                        className="mb-3"
                    ),
                ], width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Total Funding Amount ($)"),
                    dbc.Input(id='total-funding', type='number', placeholder="Enter Total Funding Amount", className="mb-3"),
                ], width=6),
                dbc.Col([
                    dbc.Label("Grant Status"),
                    dbc.Select(
                        id='grant-status',
                        options=[
                            {'label': 'Draft', 'value': 'Draft'},
                            {'label': 'Submitted', 'value': 'Submitted'},
                            {'label': 'Approved', 'value': 'Approved'},
                            {'label': 'Rejected', 'value': 'Rejected'},
                            {'label': 'Completed', 'value': 'Completed'}
                        ],
                        value="Draft",
                        className="mb-3"
                    ),
                ], width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Start Date"),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id='start-date',
                        min_date_allowed=date.today(),
                        initial_visible_month=date.today(),
                        date=date.today(),
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("End Date"),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id='end-date',
                        min_date_allowed=date.today(),
                        initial_visible_month=date.today(),
                        date=date.today(),
                        className="mb-3"
                    ),
                ], width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Label("Grant Description"),
                    dbc.Textarea(id='grant-description', placeholder="Enter a detailed description of the grant", style={"height": "100px"}, className="mb-3"),
                ], width=12),
            ], className="mb-4"),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Button(
                                "Submit",
                                id="submit-btn",
                                color="primary",
                                className="w-40",
                                style={"text-align": "center"},
                            ),
                        ],
                        className="d-flex justify-content-center",
                    ),
                ],
                className="mb-4",
                justify="center",
            ), 
        ], fluid=True, id="grant-generator-sub-container"), 
    ], 
    id="grant-generator-container"
)

# Define the layout
def layout():
    return html.Div([
        html.H3('Generate Grants', className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),
        dcc.Loading(
            type='circle',
            children=[
                container,
                success_toast,  # Add success toast
                failure_toast   # Add failure toast
            ],
        ),
    ])

# Callback to handle form submission
@callback(
    [Output('success-toast', 'is_open'), Output('failure-toast', 'is_open')],
    Input('submit-btn', 'n_clicks'),
    [
        State('grant-title', 'value'),
        State('funding-agency', 'value'),
        State('total-funding', 'value'),
        State('grant-status', 'value'),
        State('start-date', 'date'),
        State('end-date', 'date'),
        State('grant-description', 'value')
    ],
    prevent_initial_call=True
)
def submit_grant(n_clicks, title, funding_agency, total_funding, status, start_date, end_date, description):
    if not all([title, funding_agency, total_funding, status, start_date, end_date]):
        return False, True  # Show failure toast

    # Get the database session
    session = get_db_session()

    try:
        if not current_user.is_authenticated:
            return False, True  # Show failure toast

        new_grant = Grant(
            user_id=current_user.id,
            title=title,
            description=description,
            funding_agency=funding_agency,
            total_funding=total_funding,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        session.add(new_grant)
        session.commit()

        return True, False  # Show success toast

    except Exception as err:
        session.rollback()
        print(f"Error occurred while submitting grant: {err}")
        return False, True  # Show failure toast

    finally:
        session.close()
