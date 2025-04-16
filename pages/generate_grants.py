import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import date
from models import Grant, User
from db_utils import get_db_session
from flask_login import current_user
from dateutil.relativedelta import relativedelta
from dash import MATCH, ALL, ctx
from dash.exceptions import PreventUpdate

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

# materisl options
material_options = [
    {"label": "Equipment >5K", "value": "Equipment >5K"},
    {"label": "Materials and Supplies", "value": "Materials and Supplies"},
    {"label": "Equipment <5K", "value": "Equipment <5K"},
    {"label": "Publication Costs", "value": "Publication Costs"},
    {"label": "Computer Services", "value": "Computer Services"},
    {"label": "Software", "value": "Software"},
    {"label": "Facility Usage Fees", "value": "Facility Usage Fees"},
    {"label": "Conference Registration", "value": "Conference Registration"},
    {"label": "Other", "value": "Other"},
    {"label": "Grad Student Tuition & Health Insurance", "value": "Grad Student Tuition & Health Insurance"},
]


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
                            id="add-person-btn",
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
                        ),
                        dbc.Button(
                            "Remove Person",
                            id="remove-person-btn",
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
            html.Div(html.P("Personeel Expense Information", className="fw-bold")),
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
            html.Br(),

            # travel expenses
            html.Div(html.P("Travel Expenses Information", className="fw-bold")),
            html.Hr(),
            dbc.Row(children=[
                html.Div(html.P("Domestic Travel", className="")),
                html.Div(id='domestic-travel-section'),
                html.Div(
                    children=[
                        dbc.Button(
                            "Add Domestic Travel",
                            id="add-domestic-travel-btn",
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
                        ),
                        dbc.Button(
                            "Remove Domestic Travel",
                            id="remove-domestic-travel-btn",
                            color="danger",
                            className="mb-3 w-40",
                            style={"text-align": "center" , "display" : "none"},
                        ),
                    ], 
                    className="d-flex justify-content-center gap-3",
                ),

                html.Br(),

                html.Div(html.P("International Travel", className="")),
                html.Div(id='international-travel-section'),
                html.Div(
                    children=[
                        dbc.Button(
                            "Add International Travel",
                            id="add-international-travel-btn",
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
                        ),
                        dbc.Button(
                            "Remove International Travel",
                            id="remove-international-travel-btn",
                            color="danger",
                            className="mb-3 w-40",
                            style={"text-align": "center" , "display" : "none"},
                        ),
                    ], 
                    className="d-flex justify-content-center gap-3",
                ),
               
            ]), 
            html.Br(),
            # Materials and Supplies
            html.Div(html.P("Materials and Supplies", className="fw-bold")),
            html.Hr(),
            dbc.Row(children=[
                html.Div(id='materials-supplies-section'),
                html.Div(
                    children=[
                        dbc.Button(
                            "Add Material/Supply",
                            id="add-material-btn",
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
                        ),
                        dbc.Button(
                            "Remove Material/Supply",
                            id="remove-material-btn",
                            color="danger",
                            className="mb-3 w-40",
                            style={"text-align": "center", "display": "none"},
                        ),
                    ],
                    className="d-flex justify-content-center gap-3",
                ),
            ]),

            

        
            # action buttons
            html.Br(),
            html.Br(),
            html.Hr(),
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
                                # style={"display" : "flex", "text-align": "center", "margin-top": "20px", "gap" : "20px"},
                                style={
                                        "display": "flex",
                                        "justifyContent": "center",
                                        "gap": "20px",
                                        "paddingTop": "5px",
                                        "paddingBottom": "50px",
                                        "marginTop": "30px",
                                        "marginBottom": "30px",
                                    },
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
        # dcc stores
        dcc.Store(id='personnel-store', data=[0]),
        dcc.Store(id='personnel-values-store', data=None),
        dcc.Store(id='domestic-travel-store', data=[0]),
        dcc.Store(id='international-travel-store', data=[0]),
        dcc.Store(id='hours-store', data={}),
        dcc.Store(id='domestic-travel-values-store', data={}),
        dcc.Store(id='international-travel-values-store', data={}),
        dcc.Store(id='materials-store', data=[0]),
        dcc.Store(id='materials-values-store', data={}),




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






############################################
# Personeel Expenses Callbacks
############################################
# Callback to modify list of personnel row indices
@callback(
    Output('personnel-store', 'data'),
    Output('personnel-values-store', 'data'),
    Input('add-person-btn', 'n_clicks'),
    Input('remove-person-btn', 'n_clicks'),
    State('personnel-store', 'data'),
    State({'type': 'grant-input', 'name': 'person-name', 'index': ALL}, 'value'),
    State({'type': 'grant-input', 'name': 'person-position', 'index': ALL}, 'value'),
    State({'type': 'same-each-year', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def update_person_list(add_clicks, remove_clicks, current_data, names, positions, checkboxes):
    triggered = ctx.triggered_id
    new_data = current_data.copy()

    if triggered == 'add-person-btn':
        new_index = max(current_data) + 1 if current_data else 0
        new_data.append(new_index)
    elif triggered == 'remove-person-btn' and len(current_data) > 1:
        new_data = current_data[:-1]  # Always remove last index

    # Only store values for rows that still exist after the update
    filtered_personnel = []
    for i, n, p, c in zip(current_data, names, positions, checkboxes):
        if i in new_data:
            filtered_personnel.append({
                'index': i,
                'name': n,
                'position': p,
                'checkbox': c
            })

    return new_data, filtered_personnel




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
    Output("remove-person-btn", "style"),
    Input("add-person-btn", "n_clicks"),
    Input('personnel-store', 'data'),
)
def show_remove_button(add_clicks, current_data):
    if add_clicks and len(current_data) > 1:
        return {"text-align": "center" , "display" : "block"}
    else:
        return {"text-align": "center" , "display" : "none"}
    


############################################
# Estimated Working hours Callbacks
############################################

# estimated hours section
# Dynamically create inputs for years based on selected duration
@callback(
    Output('estimated-hours-section', 'children'),
    Input({'type': 'grant-input', 'name': 'person-name', 'index': ALL}, 'value'),
    Input({'type': 'grant-input', 'name': 'person-position', 'index': ALL}, 'value'),
    Input({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
    State('personnel-store', 'data'),
    State('personnel-values-store', 'data'),
    State('hours-store', 'data'),
    State({'type': 'grant-input', 'name': 'start-date'}, 'date'),  # <-- Add this
)
def render_estimated_hours_rows(names, positions, duration, indexes, personnel_data, hours_store, start_date):
    duration = int(duration) if duration else 1
    index_to_data = {
        i: {'name': n, 'position': p}
        for i, n, p in zip(indexes, names, positions)
        if n and p
    }

    # Prepare year labels using start date
    year_labels = []
    try:
        start_year = date.fromisoformat(start_date).year
        year_labels = [str(start_year + y) for y in range(duration)]
    except:
        year_labels = [f"Year {y+1}" for y in range(duration)]

    hours_store = hours_store or {}
    rows = []

    for i in indexes:
        person = index_to_data.get(i)
        if not person:
            continue

        year_inputs = [
            dbc.Col(
                dbc.Input(
                    id={"type": "hours-input", "year": y + 1, "index": i},
                    type='number',
                    placeholder=year_labels[y],
                    value=hours_store.get(f"{i}-{y+1}", ""),
                    className="mb-2"
                ),
                width=12 // duration
            )
            for y in range(duration)
        ]

        checkbox_checked = False
        for item in personnel_data or []:
            if item['index'] == i:
                checkbox_checked = item.get('checkbox', False)

        rows.append(
            dbc.Row([
                dbc.Col(html.P(person['name'], className="mb-0"), width=3),
                dbc.Col(html.P(person['position'], className="mb-0"), width=2),
                dbc.Col(dbc.Row(year_inputs, className="g-1"), width=5),
                dbc.Col(
                    dbc.Checkbox(
                        id={"type": "same-each-year", "index": i},
                        value=checkbox_checked,
                    ),
                    width=2
                ),
            ], className="align-items-center mb-2")
        )

    return rows


@callback(
    Output('personnel-values-store', 'data', allow_duplicate=True),
    Input({'type': 'same-each-year', 'index': ALL}, 'value'),
    State({'type': 'grant-input', 'name': 'person-name', 'index': ALL}, 'value'),
    State({'type': 'grant-input', 'name': 'person-position', 'index': ALL}, 'value'),
    State('personnel-store', 'data'),
    prevent_initial_call=True
)
def update_checkbox_state(checkbox_values, names, positions, indexes):
    data = []
    for i, name, position, checkbox in zip(indexes, names, positions, checkbox_values):
        data.append({
            'index': i,
            'name': name,
            'position': position,
            'checkbox': checkbox
        })
    return data



# Create a callback to save values to hours-store:
@callback(
    Output('hours-store', 'data', allow_duplicate=True),
    Input({'type': 'hours-input', 'year': ALL, 'index': ALL}, 'value'),
    State({'type': 'hours-input', 'year': ALL, 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def save_hour_values(values, ids):
    data = {}
    for val, id_obj in zip(values, ids):
        key = f"{id_obj['index']}-{id_obj['year']}"
        data[key] = val
    return data


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










############################################
# Travel Expenses Callbacks
############################################

# callback to dynamically create inputs for travel expenses: both for domestic and international
@callback(
    Output('domestic-travel-store', 'data'),
    Input('add-domestic-travel-btn', 'n_clicks'),
    Input('remove-domestic-travel-btn', 'n_clicks'),
    State('domestic-travel-store', 'data'),
    prevent_initial_call=True
)
def update_domestic_travel(add_clicks, remove_clicks, data):
    triggered = ctx.triggered_id
    data = data or [0]

    if triggered == 'add-domestic-travel-btn':
        new_index = max(data) + 1
        return data + [new_index]
    elif triggered == 'remove-domestic-travel-btn' and len(data) > 1:
        return data[:-1]
    return data

# Show/Hide Remove Button for Domestic
@callback(
    Output('remove-domestic-travel-btn', 'style'),
    Input('domestic-travel-store', 'data')
)
def toggle_remove_domestic_button(data):
    return {"text-align": "center", "display": "block"} if len(data) > 1 else {"text-align": "center", "display": "none"}

#  International Travel Row Manager
@callback(
    Output('international-travel-store', 'data'),
    Input('add-international-travel-btn', 'n_clicks'),
    Input('remove-international-travel-btn', 'n_clicks'),
    State('international-travel-store', 'data'),
    prevent_initial_call=True
)
def update_international_travel(add_clicks, remove_clicks, data):
    triggered = ctx.triggered_id
    data = data or [0]

    if triggered == 'add-international-travel-btn':
        new_index = max(data) + 1
        return data + [new_index]
    elif triggered == 'remove-international-travel-btn' and len(data) > 1:
        return data[:-1]
    return data

# Show/Hide Remove Button for International
@callback(
    Output('remove-international-travel-btn', 'style'),
    Input('international-travel-store', 'data')
)
def toggle_remove_international_button(data):
    return {"text-align": "center", "display": "block"} if len(data) > 1 else {"text-align": "center", "display": "none"}


# Update domestic travel values store
@callback(
    Output('domestic-travel-values-store', 'data', allow_duplicate=True),
    Input({'type': 'travel-name', 'scope': 'domestic', 'index': ALL}, 'value'),
    Input({'type': 'travel-desc', 'scope': 'domestic', 'index': ALL}, 'value'),
    Input({'type': 'travel-year', 'scope': 'domestic', 'index': ALL}, 'value'),
    State({'type': 'travel-name', 'scope': 'domestic', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def update_domestic_travel_values(names, descs, years, ids):
    data = {}
    for name, desc, year, id_obj in zip(names, descs, years, ids):
        index = id_obj['index']
        data[str(index)] = {
            'name': name,
            'desc': desc,
            'year': year
        }
    return data


# Update international travel values store
@callback(
    Output('international-travel-values-store', 'data', allow_duplicate=True),
    Input({'type': 'travel-name', 'scope': 'international', 'index': ALL}, 'value'),
    Input({'type': 'travel-desc', 'scope': 'international', 'index': ALL}, 'value'),
    Input({'type': 'travel-year', 'scope': 'international', 'index': ALL}, 'value'),
    State({'type': 'travel-name', 'scope': 'international', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def update_international_travel_values(names, descs, years, ids):
    data = {}
    for name, desc, year, id_obj in zip(names, descs, years, ids):
        index = id_obj['index']
        data[str(index)] = {
            'name': name,
            'desc': desc,
            'year': year
        }
    return data


# Render domestic travel rows with persisted values
@callback(
    Output('domestic-travel-section', 'children'),
    Input('domestic-travel-store', 'data'),
    State('domestic-travel-values-store', 'data'),
    Input({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
    Input({'type': 'grant-input', 'name': 'start-date'}, 'date'),
)
def render_domestic_travels(indexes, stored_data, duration, start_date):
    duration = int(duration) if duration else 1
    stored_data = stored_data or {}
    rows = []

    try:
        start_date_obj = date.fromisoformat(start_date)
    except:
        raise PreventUpdate

    year_options = [
        {"label": f"Year {i + 1} ({(start_date_obj + relativedelta(years=i)).year})",
         "value": (start_date_obj + relativedelta(years=i)).year}
        for i in range(duration)
    ]

    for i in indexes:
        val = stored_data.get(str(i), {})
        rows.append(
            dbc.Row([
                dbc.Col(dbc.Input(
                    id={"type": "travel-name", "scope": "domestic", "index": i},
                    placeholder="Travel Name",
                    value=val.get('name', "")
                ), width=3),
                dbc.Col(dbc.Textarea(
                    id={"type": "travel-desc", "scope": "domestic", "index": i},
                    placeholder="Description",
                    value=val.get('desc', ""),
                    style={"height": "38px"}
                ), width=6),
                dbc.Col(dbc.Select(
                    id={"type": "travel-year", "scope": "domestic", "index": i},
                    options=year_options,
                    value=val.get('year', None),
                    placeholder="Select Year"
                ), width=3),
            ], className="mb-3")
        )
    return rows


# Render international travel rows with persisted values
@callback(
    Output('international-travel-section', 'children'),
    Input('international-travel-store', 'data'),
    State('international-travel-values-store', 'data'),
    Input({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
    Input({'type': 'grant-input', 'name': 'start-date'}, 'date'),
)
def render_international_travels(indexes, stored_data, duration, start_date):
    duration = int(duration) if duration else 1
    stored_data = stored_data or {}
    rows = []

    try:
        start_date_obj = date.fromisoformat(start_date)
    except:
        raise PreventUpdate

    year_options = [
        {"label": f"Year {i + 1} ({(start_date_obj + relativedelta(years=i)).year})",
         "value": (start_date_obj + relativedelta(years=i)).year}
        for i in range(duration)
    ]

    for i in indexes:
        val = stored_data.get(str(i), {})
        rows.append(
            dbc.Row([
                dbc.Col(dbc.Input(
                    id={"type": "travel-name", "scope": "international", "index": i},
                    placeholder="Travel Name",
                    value=val.get('name', "")
                ), width=3),
                dbc.Col(dbc.Textarea(
                    id={"type": "travel-desc", "scope": "international", "index": i},
                    placeholder="Description",
                    value=val.get('desc', ""),
                    style={"height": "38px"}
                ), width=6),
                dbc.Col(dbc.Select(
                    id={"type": "travel-year", "scope": "international", "index": i},
                    options=year_options,
                    value=val.get('year', None),
                    placeholder="Select Year"
                ), width=3),
            ], className="mb-3")
        )
    return rows





############################################
# Material and Supplies Callbacks
############################################
@callback(
    Output('materials-store', 'data'),
    Input('add-material-btn', 'n_clicks'),
    Input('remove-material-btn', 'n_clicks'),
    State('materials-store', 'data'),
    prevent_initial_call=True
)
def update_materials(add, remove, data):
    data = data or [0]
    triggered = ctx.triggered_id
    if triggered == 'add-material-btn':
        new_index = max(data) + 1
        return data + [new_index]
    elif triggered == 'remove-material-btn' and len(data) > 1:
        return data[:-1]
    return data

@callback(
    Output('remove-material-btn', 'style'),
    Input('materials-store', 'data')
)
def toggle_remove_material_button(data):
    return {"text-align": "center", "display": "block"} if len(data) > 1 else {"text-align": "center", "display": "none"}



@callback(
    Output('materials-values-store', 'data', allow_duplicate=True),
    Input({'type': 'material-name', 'index': ALL}, 'value'),
    Input({'type': 'material-cost', 'index': ALL}, 'value'),
    Input({'type': 'material-year', 'index': ALL}, 'value'),
    Input({'type': 'material-desc', 'index': ALL}, 'value'),  
    State({'type': 'material-name', 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def update_material_values(names, costs, years, descs, ids):
    data = {}
    for name, cost, year, desc, id_obj in zip(names, costs, years, descs, ids):
        index = id_obj['index']
        data[str(index)] = {
            'name': name,
            'cost': cost,
            'desc': desc,
            'year': year,
            
        }
    return data


@callback(
    Output('materials-supplies-section', 'children'),
    Input('materials-store', 'data'),
    State('materials-values-store', 'data'),
    Input({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
    Input({'type': 'grant-input', 'name': 'start-date'}, 'date'),
)
def render_materials(indexes, stored_data, duration, start_date):
    duration = int(duration) if duration else 1
    stored_data = stored_data or {}

    try:
        start_date_obj = date.fromisoformat(start_date)
    except:
        raise PreventUpdate

    year_options = [
        {"label": f"Year {i + 1} ({(start_date_obj + relativedelta(years=i)).year})",
         "value": (start_date_obj + relativedelta(years=i)).year}
        for i in range(duration)
    ]

    rows = []
    for i in indexes:
        val = stored_data.get(str(i), {})
        rows.append(
            dbc.Row([
                dbc.Col(dbc.Select(
                    id={"type": "material-name", "index": i},
                    options=material_options,
                    value=val.get('name', ""),
                    placeholder="Select Material or Supply"
                ), width=3),
                dbc.Col(dbc.Input(
                    id={"type": "material-cost", "index": i},
                    type="number",
                    placeholder="Enter Cost",
                    value=val.get('cost', ""),
                    className="", 
                ), width=2),
                dbc.Col(dbc.Textarea(
                    id={"type": "material-desc", "index": i},
                    placeholder="Enter Description",
                    value=val.get('desc', ""),
                    style={"height": "38px"}
                ), width=5),
                dbc.Col(dbc.Select(
                    id={"type": "material-year", "index": i},
                    options=year_options,
                    value=val.get('year', None),
                    placeholder="Select Year"
                ), width=2),
                
            ], className="mb-3")
        )
    return rows


@callback(
    Output({'type': 'material-cost', 'index': MATCH}, 'className'),
    Input({'type': 'material-cost', 'index': MATCH}, 'n_blur'),
    State({'type': 'material-cost', 'index': MATCH}, 'value'),
    State({'type': 'material-name', 'index': MATCH}, 'value'),
    prevent_initial_call=True
)
def validate_material_cost_on_blur(n_blur, cost, material_name):
    if material_name == 'Equipment >5K' and cost is not None and cost < 5000:
        return "invalid-cost"
    return ""
