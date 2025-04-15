import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import date
from models import Grant, User
from db_utils import get_db_session
from flask_login import current_user
from dateutil.relativedelta import relativedelta
from dash import MATCH, ALL, ctx

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
                    dbc.Label("Duration (In Years)"),
                    dbc.Select(
                        id={"type": "grant-input", "name": "total-duration"},
                        options=[
                            {"label": "1 Year", "value": 1},
                            {"label": "2 Years", "value": 2},
                            {"label": "3 Years", "value": 3},
                            {"label": "4 Years", "value": 4},
                            {"label": "5 Years", "value": 5},
                        ],
                        placeholder="Select Total Duration",
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
                        date = None,
                        # date=date.today(),
                        className="mb-3", 
                        disabled=True, 
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
                html.Div(id='personnel-section'),
                # dcc.Store(id='personnel-store', data=[0]),

                html.Div(
                    children=[
                        dbc.Button(
                            "Add Person",
                            id={"type": "grant-input", "name": "add-person-btn"},
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
                        ),
                        dbc.Button(
                            "Remove Person",
                            id={"type": "grant-input", "name": "remove-person-btn"},
                            color="danger",
                            className="mb-3 w-40",
                            style={"text-align": "center" , "display" : "none"},
                        ),
                    ], 
                    className="d-flex justify-content-center gap-3",
                ),
            ]),
            html.Br(),

            # Expense Section
            html.Div(html.P("Expense Information", className="fw-bold")),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Estimated Work Hours", className=""),
                    # Header row
                    dbc.Row([
                        dbc.Col(html.P("Name", className="mb-0 fw-semibold text-left"), width=3),
                        dbc.Col(html.P("Position", className="mb-0 fw-semibold text-left"), width=2),
                        dbc.Col(html.P("Hours for year(s)", className="mb-0 fw-semibold text-left"), width=5),
                        dbc.Col(html.P("Same for Each Year", className="mb-0 fw-semibold text-left"), width=2),
                    ], style={"backgroundColor": "#ced4da", "padding": "10px", "borderRadius": "6px"}, className="mb-2"),
                    
                    # Dynamic content goes here
                    html.Div(id='estimated-hours-section')
                ])
            ]),

            # dbc.Row([
            #     dbc.Col([
            #         dbc.Label("Travel - Domestic"),
            #         dbc.Input(id='travel-domestic', type='number', placeholder="Enter amount", className="mb-3"),
            #     ]),
            #     dbc.Col([
            #         dbc.Label("Travel - International"),
            #         dbc.Input(id='travel-international', type='number', placeholder="Enter amount", className="mb-3"),
            #     ]),
            # ]),
            # dbc.Row([
            #     dbc.Col([
            #         dbc.Label("Materials and Supplies"),
            #         dbc.Input(id='materials-supplies', type='number', placeholder="Enter amount", className="mb-3"),
            #     ]),
            #     dbc.Col([
            #         dbc.Label("Publication Costs"),
            #         dbc.Input(id='publication-costs', type='number', placeholder="Enter amount", className="mb-3"),
            #     ]),
            # ]),
            # dbc.Row([
            #     dbc.Col([
            #         dbc.Label("Grad Student Tuition & Health Insurance"),
            #         dbc.Input(id='tuition-health', type='number', placeholder="Enter amount", className="mb-3"),
            #     ]),
            #     dbc.Col([
            #         dbc.Label("Other Costs"),
            #         dbc.Textarea(id='other-costs', placeholder="Describe other costs", className="mb-3", style={"height": "100px"}),
            #     ]),
            # ]),

            # action buttons
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
        dcc.Store(id='personnel-store', data=[0]),
        dcc.Store(id='personnel-values-store', data=None),
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



@callback(
    Output({"type": "grant-input", "name": "end-date"}, "date"),
    Input({"type": "grant-input", "name": "start-date"}, "date"),
    Input({"type": "grant-input", "name": "total-duration"}, "value"),
    prevent_initial_call=True
)
def update_end_date(start_date, duration):
    if start_date and duration:
        try:
            start_date_obj = date.fromisoformat(start_date)
            duration_years = int(duration) 
            end_date = start_date_obj + relativedelta(years=+duration_years)
            return end_date.isoformat()
        except Exception as e:
            print("Error calculating end date:", e)
    return None


# Callback to modify list of personnel row indices
@callback(
    Output('personnel-store', 'data'),
    Output('personnel-values-store', 'data'),
    Input({'type': 'grant-input', 'name': 'add-person-btn'}, 'n_clicks'),
    Input({'type': 'grant-input', 'name': 'remove-person-btn'}, 'n_clicks'),
    State('personnel-store', 'data'),
    State({'type': 'grant-input', 'name': 'person-name', 'index': ALL}, 'value'),
    State({'type': 'grant-input', 'name': 'person-position', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def update_person_list(add_clicks, remove_clicks, current_data, names, positions):
    # Preserve existing data
    current_personnel = [
        {'index': i, 'name': n, 'position': p}
        for i, n, p in zip(current_data, names, positions)
    ]
    
    triggered = ctx.triggered_id
    if triggered and triggered['name'] == 'add-person-btn':
        new_index = max(current_data) + 1 if current_data else 0
        new_data = current_data + [new_index]
    elif triggered and triggered['name'] == 'remove-person-btn':
        if len(current_data) > 1:
            new_data = current_data[:-1]
            current_personnel = current_personnel[:-1]  # Drop last row's values
        else:
            new_data = current_data
    else:
        new_data = current_data

    return new_data, current_personnel


# Callback to render rows based on indices in personnel-store
@callback(
    Output('personnel-section', 'children'),
    Input('personnel-store', 'data'),
    State('personnel-values-store', 'data')
)
def render_personnel_rows(indexes, stored_data):
    stored_data = stored_data or []
    index_to_data = {item['index']: item for item in stored_data}
    
    rows = []
    for i in indexes:
        person_data = index_to_data.get(i, {})
        rows.append(
            dbc.Row([
                dbc.Col([
                    dbc.Label("Name"),
                    dbc.Input(
                        id={"type": "grant-input", "name": "person-name", "index": i},
                        type='text',
                        placeholder="Enter full name",
                        className="mb-3",
                        value=person_data.get('name', "")
                    ),
                ], width=6),

                dbc.Col([
                    dbc.Label("Position"),
                    dbc.Select(
                        id={"type": "grant-input", "name": "person-position", "index": i},
                        options=[
                            {"label": "PI", "value": "PI"},
                            {"label": "Co-PI", "value": "Co-PI"},
                            {"label": "Professional Staff", "value": "UI Professional Staff"},
                            {"label": "Postdoc", "value": "Postdoc"},
                            {"label": "GRA", "value": "GRA"},
                            {"label": "Undergrad", "value": "Undergrad"},
                            {"label": "Temp Help", "value": "Temp Help"},
                        ],
                        placeholder="Select role",
                        className="mb-3",
                        value=person_data.get('position', "")
                    ),
                ], width=6),
            ], className="mb-2")
        )
    return rows





# callback to show the buttons to remove for when we add a person
@callback(
    Output({"type": "grant-input", "name": "remove-person-btn"}, "style"),
    Input({"type": "grant-input", "name": "add-person-btn"}, "n_clicks"),
    Input('personnel-store', 'data'),
)
def show_remove_button(add_clicks, current_data):
    if add_clicks and len(current_data) > 1:
        return {"text-align": "center" , "display" : "block"}
    else:
        return {"text-align": "center" , "display" : "none"}
    


# Dynamically create inputs for years based on selected duration
@callback(
    Output('estimated-hours-section', 'children'),
    Input({'type': 'grant-input', 'name': 'person-name', 'index': ALL}, 'value'),
    Input({'type': 'grant-input', 'name': 'person-position', 'index': ALL}, 'value'),
    Input({'type': 'grant-input', 'name': 'total-duration'}, 'value'),  
    State('personnel-store', 'data'),
    
)
def render_estimated_hours_rows(names, positions, duration, indexes ):
    duration = int(duration) if duration else 1
    duration = duration or 1
    index_to_data = {
        i: {'name': n, 'position': p}
        for i, n, p in zip(indexes, names, positions)
        if n and p  # show row only if at least one field is entered
    }


    rows = []
    for i in indexes:
        person = index_to_data.get(i)
        if not person:
            continue  # skip rows with empty name or position

        # inner row for year inputs
        year_inputs = [
            dbc.Col(
                dbc.Input(
                    id={"type": "hours-input", "year": y, "index": i},
                    type='number',
                    placeholder=f"Y{y}",
                    className="mb-2"
                ), width=12 // duration  
            )
            for y in range(1, duration + 1)
        ]

        rows.append(
            dbc.Row([
                dbc.Col(html.P(person['name'], className="mb-0"), width=3),
                dbc.Col(html.P(person['position'], className="mb-0"), width=2),
                dbc.Col(dbc.Row(year_inputs, className="g-1"), width=5), 
                dbc.Col(
                    dbc.Checkbox(
                        id={"type": "same-each-year", "index": i},
                        # className="form-check-input",
                    ),
                    width=2
                ),
            ], className="align-items-center mb-2")
        )

    return rows

# callback for syncing values when “Same for Each Year” is checked
@callback(
    Output({'type': 'hours-input', 'year': ALL, 'index': MATCH}, 'value'),
    Input({'type': 'same-each-year', 'index': MATCH}, 'value'),
    State({'type': 'hours-input', 'year': ALL, 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def copy_hours_if_same_for_all(same_for_each, year_values):
    if same_for_each:
        first_year_value = year_values[0]
        return [first_year_value] * len(year_values)
    return year_values
