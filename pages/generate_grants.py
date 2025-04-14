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
            html.Div(
                html.P("Budget Information", className="fw-bold")
            ),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Grant Title"),
                    dbc.Input( 
                        id={"type": "grant-input", "name": "grant-title"},
                        type='text', 
                        placeholder="Enter Grant Title", 
                        className="mb-3 "
                    ),
                ], width=6,),
                
                dbc.Col([
                    dbc.Label("Funding Agency"),
                    dbc.Select(
                        id={"type": "grant-input", "name": "funding-agency"},
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
                    dbc.Input(
                        id={"type": "grant-input", "name": "total-funding"},
                        type='number', 
                        placeholder="Enter Total Funding Amount", 
                        className="mb-3"
                    ),
                ], width=6),
                dbc.Col([
                    dbc.Label("Grant Status"),
                    dbc.Select(
                        id={"type": "grant-input", "name": "grant-status"},
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
                        id={"type": "grant-input", "name": "start-date"},
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
                        id={"type": "grant-input", "name": "end-date"},
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
                    dbc.Textarea(
                        id={"type": "grant-input", "name": "grant-description"},
                        placeholder="Enter a detailed description of the grant", 
                        style={"height": "100px"}, 
                        className="mb-3"
                    ),
                ], width=12),
            ], className="mb-4"),

            # PI & Co-PI Section(budget personeels)
            html.Div(html.P("Personeel Information", className="fw-bold")),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Name"),
                    dbc.Input(
                        id={"type": "grant-input", "name": "person-name", "index": 0},
                        type='text',
                        placeholder="Enter full name",
                        className="mb-3"
                    ),
                ], width=6),

                dbc.Col([
                    dbc.Label("Position"),
                    dbc.Select(
                        id={"type": "grant-input", "name": "person-position", "index": 0},
                        options=[
                            {"label": "PI", "value": "PI"},
                            {"label": "Co-PI", "value": "Co-PI"},
                            {"label": "Senior Personnel", "value": "Senior Personnel"},
                            {"label": "Collaborator", "value": "Collaborator"},
                            {"label": "Professional Staff", "value": "UI Professional Staff"},
                            {"label": "Postdoc", "value": "Postdoc"},
                            {"label": "GRA", "value": "GRA"},
                            {"label": "Undergrad", "value": "Undergrad"},
                            {"label": "Temp Help", "value": "Temp Help"},
                        ],
                        placeholder="Select role",
                        className="mb-3"
                    ),
                ], width=6),

                html.Div(
                    dbc.Button(
                        "Add Person",
                        id={"type": "grant-input", "name": "add-person-btn"},
                        color="primary",
                        className="mb-3 w-40",
                        style={"text-align": "center"},
                    ),
                    className="d-flex justify-content-center",
                ),
            ]),
            html.Br(),

            # Expense Section
            html.Div(html.P("Expense Information", className="fw-bold")),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Label("UI Professional Staff & Post Docs"),
                    dbc.Input(id='ui-staff-expense', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("GRAs / UGrads"),
                    dbc.Input(id='grads-expense', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Temp Help"),
                    dbc.Input(id='temp-help-expense', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Travel - Domestic"),
                    dbc.Input(id='travel-domestic', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Travel - International"),
                    dbc.Input(id='travel-international', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Materials and Supplies"),
                    dbc.Input(id='materials-supplies', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Publication Costs"),
                    dbc.Input(id='publication-costs', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Grad Student Tuition & Health Insurance"),
                    dbc.Input(id='tuition-health', type='number', placeholder="Enter amount", className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Other Costs"),
                    dbc.Textarea(id='other-costs', placeholder="Describe other costs", className="mb-3", style={"height": "100px"}),
                ]),
            ]),

            # Fringe Section (auto-calculated – just for display)
            html.Div(html.P("Fringe Benefit Rates (Auto Calculated)", className="fw-bold")),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Faculty Fringe (%)"),
                    dbc.Input(id='faculty-fringe', type='number', disabled=True, className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Post Doc Fringe (%)"),
                    dbc.Input(id='postdoc-fringe', type='number', disabled=True, className="mb-3"),
                ]),
            ]),

            # Indirect Cost and Totals
            html.Div(html.P("Indirect Costs & Totals", className="fw-bold")),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Indirect Cost Rate (%)"),
                    dbc.Input(id='indirect-rate', type='number', disabled=True, className="mb-3"),
                ]),
                dbc.Col([
                    dbc.Label("Total Project Cost"),
                    dbc.Input(id='total-project-cost', type='number', disabled=True, className="mb-3"),
                ]),
            ]),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                children=[
                                    dbc.Button(
                                        "Save as Draft",
                                        id="save-draft-btn",
                                        color="secondary",
                                        className="w-40",
                                        style={"text-align": "center"},
                                    ),
                                    dbc.Button(
                                        "Submit",
                                        id="submit-btn",
                                        color="primary",
                                        className="w-40",
                                        style={"text-align": "center"},
                                    ),
                                    dbc.Button(
                                        "Clear",
                                        id="clear-btn",
                                        color="danger",
                                        className="w-40",
                                        style={"text-align": "center"},
                                    ),
                                ],
                                style={"display" : "flex", "text-align": "center", "margin-top": "20px", "gap" : "20px"},
                            )
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
