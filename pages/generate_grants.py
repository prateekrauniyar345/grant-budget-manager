import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import date
from models import User
from db_utils import get_db_session
from flask_login import current_user
from dateutil.relativedelta import relativedelta
from dash import MATCH, ALL, ctx
from dash.exceptions import PreventUpdate
from models import Grant, GrantPersonnel, GrantTravel,TravelItinerary, GrantMaterial, ExpenseSubcategory, PI, CoPI, ProfessionalStaff, Postdoc, GRA, Undergrad, TempHelp
from db_utils import get_db_session
from datetime import date
import urllib.parse
from dash import callback_context  # already using ctx probably
# Callback to handle form submission
from sqlalchemy.exc import SQLAlchemyError
from collections import OrderedDict


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


# list of personeels options
PI_PERSONEELS_OPTIONS = []
COPI_PERSONEELS_OPTIONS = []
PROFESSIONAL_STAFF_OPTIONS = []
POSTDOC_OPTIONS = []
GRA_OPTIONS = []
UNDERGRAD_OPTIONS = []
TEMP_HELP_OPTIONS = []

def load_personnel_options():
    session = get_db_session()

    try:
        return {
            "PI": [{"label": pi.full_name, "value": pi.full_name} for pi in session.query(PI).all()],
            "Co-PI": [{"label": copi.full_name, "value": copi.full_name} for copi in session.query(CoPI).all()],
            "UI Professional Staff": [{"label": staff.full_name, "value": staff.full_name} for staff in session.query(ProfessionalStaff).all()],
            "Postdoc": [{"label": postdoc.full_name, "value": postdoc.full_name} for postdoc in session.query(Postdoc).all()],
            "GRA": [{"label": gra.full_name, "value": gra.full_name} for gra in session.query(GRA).all()],
            "Undergrad": [{"label": ug.full_name, "value": ug.full_name} for ug in session.query(Undergrad).all()],
            "Temp Help": [{"label": temp.full_name, "value": temp.full_name} for temp in session.query(TempHelp).all()]
        }
    finally:
        session.close()

# Load once and store in memory (could be in a Flask global or during app init)
personnel_cache = load_personnel_options()



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
                html.Div(
                    children=[
                        dbc.Button(
                            "Add Person",
                            id="add-person-btn",
                            color="primary",
                            className="mb-3 w-40",
                            style={"text-align": "center"},
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
                                        n_clicks=0,
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


def layout(**query_params):
    edit_id = query_params.get("edit_id", None)

    print("Edit ID:", edit_id)
    print("query params:", query_params)

    return html.Div([
        dcc.Store(
            id='personnel-store',
            data=[{'index': 1, 'position': '', 'name': '', 'checkbox': False}]
        ),
        dcc.Store(id='domestic-travel-store', data=[0]),
        dcc.Store(id='international-travel-store', data=[0]),
        dcc.Store(id='hours-store', data={}),
        dcc.Store(id='domestic-travel-values-store', data={}),
        dcc.Store(id='international-travel-values-store', data={}),
        dcc.Store(id='materials-store', data=[0]),
        dcc.Store(id='materials-values-store', data={}),

        dcc.Location(id='clear-url', refresh=True),
        dcc.Location(id='url', refresh=False),

       
        # to remove
        html.Div(id="debug-edit-id", style={"display": "none"}),
        # html.Div(id="debug-fields", style={"color": "red"}),
        html.Div(id="form-mounted-flag", style={}),

        html.Div(id='dummy-output', style={}),



        html.H3('Generate Grants', className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),

        dcc.Loading(
            type='circle',
            children=[
                container,
                success_toast,
                failure_toast
            ],
        ),

         # ✅ Pre-fill the Store directly here
        dcc.Store(id='edit-grant-id', data=edit_id),

    ])




@callback(
    Output('success-toast', 'is_open'),
    Output('failure-toast', 'is_open'),
    Input('submit-btn', 'n_clicks'),
    [
        State({'type': 'grant-input', 'name': 'grant-title'},      'value'),
        State({'type': 'grant-input', 'name': 'funding-agency'},   'value'),
        State({'type': 'grant-input', 'name': 'total-duration'},   'value'),
        State({'type': 'grant-input', 'name': 'grant-status'},     'value'),
        State({'type': 'grant-input', 'name': 'start-date'},       'date'),
        State({'type': 'grant-input', 'name': 'end-date'},         'date'),
        State({'type': 'grant-input', 'name': 'grant-description'},'value'),
        # ← now read from the single personnel-store:
        State('personnel-store', 'data'),
        State('hours-store', 'data'),
        State('domestic-travel-values-store',      'data'),
        State('international-travel-values-store', 'data'),
        State('materials-values-store',            'data'),
        State('edit-grant-id',                     'data'),
    ],
    prevent_initial_call=True
)
def submit_grant(n_clicks,
                 title, agency, duration, status,
                 start_date, end_date, description,
                 personnel_rows, hours_data,
                 dom_tr, int_tr, mat_data,
                 edit_grant_id):
    # basic validation
    if not all([title, agency, duration, status, start_date, end_date]):
        return False, True

    session = get_db_session()
    def normalize_empty(v): return v if v not in ("", None) else None

    try:
        if not current_user.is_authenticated:
            return False, True

        with session.begin():
            if edit_grant_id:
                # ── UPDATE EXISTING ──
                g = session.query(Grant)\
                           .filter_by(id=int(edit_grant_id),
                                      user_id=current_user.id)\
                           .first()
                if not g:
                    return False, True

                # update fields...
                # ── UPDATE THE GRANT FIELDS ──
                g.title           = title
                g.funding_agency  = agency
                g.duration        = duration
                g.start_date      = start_date
                g.end_date        = end_date
                g.status          = status
                g.description     = normalize_empty(description)

                grant_id = g.id

                # clear old related rows
                session.query(GrantPersonnel).filter_by(grant_id=grant_id).delete()
                session.query(GrantTravel).   filter_by(grant_id=grant_id).delete()
                session.query(GrantMaterial). filter_by(grant_id=grant_id).delete()

            else:
                # ── INSERT NEW ──
                new = Grant(
                    user_id=current_user.id,
                    title=title,
                    description=normalize_empty(description),
                    funding_agency=agency,
                    duration=duration,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                session.add(new)
                session.flush()
                grant_id = new.id

            # ── PERSONNEL ──
            if personnel_rows and hours_data:
                sy = date.fromisoformat(start_date).year
                for row in personnel_rows:
                    # skip any completely blank row
                    if not row.get('name') or not row.get('position'):
                        continue
                    idx = row['index']
                    for off in range(int(duration)):
                        key = f"{idx}-{off+1}"
                        hrs = normalize_empty(hours_data.get(key))
                        if hrs is not None:
                            session.add(GrantPersonnel(
                                grant_id=grant_id,
                                name=row['name'],
                                position=row['position'],
                                year=sy + off,
                                estimated_hours=hrs
                            ))

            # ── DOMESTIC TRAVEL + ITINERARY ──
            for key, item in (dom_tr or {}).items():
                # only add if user filled name or year
                if item.get('name') or item.get('year'):
                    # 1) create the GrantTravel
                    travel = GrantTravel(
                        grant_id=grant_id,
                        travel_type='Domestic',
                        name=item.get('name'),
                        description=normalize_empty(item.get('desc')),
                        year=normalize_empty(item.get('year'))
                    )
                    session.add(travel)
                    session.flush()  # so travel.id is set
                    print("depature date is : ", item.get('departure_date'))
                    print("arrival date is : ", item.get('arrival_date'))
                    # 2) then create the matching TravelItinerary
                    itin = TravelItinerary(
                        travel_id=travel.id,
                        departure_date        = normalize_empty(item.get('departure_date')),
                        arrival_date          = normalize_empty(item.get('arrival_date')),
                        flight_cost           = normalize_empty(item.get('flight_cost')),
                        days_stay             = normalize_empty(item.get('days_stay')),
                        per_day_food_lodging  = normalize_empty(item.get('food_lodging_cost')),
                        per_day_transportation= normalize_empty(item.get('transportation_cost'))
                    )
                    session.add(itin)

            # ── INTERNATIONAL TRAVEL + ITINERARY ──
            for key, item in (int_tr or {}).items():
                if item.get('name') or item.get('year'):
                    travel = GrantTravel(
                        grant_id=grant_id,
                        travel_type='International',
                        name=item.get('name'),
                        description=normalize_empty(item.get('desc')),
                        year=normalize_empty(item.get('year'))
                    )
                    session.add(travel)
                    session.flush()

                    itin = TravelItinerary(
                        travel_id=travel.id,
                        departure_date        = normalize_empty(item.get('departure_date')),
                        arrival_date          = normalize_empty(item.get('arrival_date')),
                        flight_cost           = normalize_empty(item.get('flight_cost')),
                        days_stay             = normalize_empty(item.get('days_stay')),
                        per_day_food_lodging  = normalize_empty(item.get('food_lodging_cost')),
                        per_day_transportation= normalize_empty(item.get('transportation_cost'))
                    )
                    session.add(itin)

            # ── MATERIALS & SUPPLIES ──
            for item in (mat_data or {}).values():
                cost = normalize_empty(item.get('cost'))
                yr   = normalize_empty(item.get('year'))
                if cost is not None or yr is not None:
                    sub = session.query(ExpenseSubcategory)\
                                 .filter_by(name=item.get('name'))\
                                 .first()
                    session.add(GrantMaterial(
                        grant_id=grant_id,
                        category_id = sub.category_id if sub else None,
                        subcategory_id= sub.id if sub else None,
                        cost=cost,
                        description=normalize_empty(item.get('desc')),
                        year=yr
                    ))

        return True, False

    except SQLAlchemyError as e:
        print("Submission Error:", e)
        return False, True

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
# Personeel Section Callbacks
############################################

############################################
# 1️  Single “manager” for Add/Del/Edits
############################################
@callback(
     Output('personnel-store', 'data'),
     Input('add-person-btn', 'n_clicks'),
     Input({'type':'grant-input','name':'delete-row-option','index':ALL}, 'n_clicks'),
     Input({'type':'grant-input','name':'person-position','index':ALL}, 'value'),
     Input({'type':'grant-input','name':'person-name','index':ALL}, 'value'),
     State('personnel-store', 'data'),
     prevent_initial_call=True
)
def manage_personnel(add_clicks, delete_clicks, positions, names, rows):
     rows = rows or []
     trig = ctx.triggered_id

     # ➕ Add a blank row
     if trig == 'add-person-btn':
         new_idx = max(r['index'] for r in rows) + 1 if rows else 1
         return rows + [{'index': new_idx, 'position': '', 'name': ''}]

     # ❌ Remove a row
     if isinstance(trig, dict) and trig.get('name') == 'delete-row-option' and any(click and click > 0 for click in delete_clicks):
         idx = trig['index']
         return [r for r in rows if r['index'] != idx]

     # ✏️ Field edits
     updated = []
     for r, pos, nm in zip(rows, positions, names):
         r2 = r.copy()
         r2['position'] = pos or r2['position']
         r2['name']     = nm  or r2['name']
         updated.append(r2)
     return updated



############################################
# 2️Render the personnel rows
############################################
@callback(
    Output('personnel-section', 'children'),
    Input('personnel-store', 'data'),
)
def render_personnel_rows(rows):
    rows = rows or []
    children = []
    for r in rows:
        idx = r['index']
        children.append(
            dbc.Row([
                # Position
                dbc.Col([
                    dbc.Label("Position"),
                    dbc.Select(
                        id={"type":"grant-input","name":"person-position","index":idx},
                        options=[
                            {"label":"PI",                   "value":"PI"},
                            {"label":"Co-PI",                "value":"Co-PI"},
                            {"label":"UI Professional Staff","value":"UI Professional Staff"},
                            {"label":"Postdoc",              "value":"Postdoc"},
                            {"label":"GRA",                  "value":"GRA"},
                            {"label":"Undergrad",            "value":"Undergrad"},
                            {"label":"Temp Help",            "value":"Temp Help"},
                        ],
                        value=r['position'],
                        placeholder="Select role",
                    ),
                ], width=5),

                # Name
                dbc.Col([
                    dbc.Label("Name"),
                    dcc.Dropdown(
                        id={"type":"grant-input","name":"person-name","index":idx},
                        # options=personnel_cache.get(r['position'], []),  #load_personnel_options()   using this function
                        options=load_personnel_options().get(r['position'], []),
                        value=r['name'],
                        placeholder="Select full name",
                    ),
                ], width=6),

                # Remove
                # id={"type":"grant-input","name":"delete-row-option","index":idx},
                dbc.Col(
                        children=[
                            dbc.Label("Remove", className="mb-1 text-white"),
                            dbc.Button(
                                "❌",
                                id={"type":"grant-input","name":"delete-row-option","index":idx},
                                color="danger",
                                size="sm",
                                className="bg-light mt-1",  # adds space between label and button
                                disabled=False
                            ),
                        ],
                        width=1,
                        className="d-flex flex-column align-items-center"
                    ),
            ], className="mb-2")
        )
    return children


############################################
# 3️ Keep Name dropdown in sync with Position
############################################
@callback(
    Output({'type':'grant-input','name':'person-name','index':MATCH}, 'options'),
    Input({'type':'grant-input','name':'person-position','index':MATCH}, 'value')
)
def update_person_name_dropdown(position):
    return personnel_cache.get(position, [])


############################################
# 4️  Render Estimated‐Hours (per row)
############################################
@callback(
    Output('estimated-hours-section', 'children'),
    Input('personnel-store',                       'data'),
    Input({'type':'grant-input','name':'total-duration'}, 'value'),
    Input({'type':'grant-input','name':'start-date'},     'date'),
    State('hours-store', 'data'),
    prevent_initial_call=True
)
def render_estimated_hours(rows, duration, start_date, hours_store):
    if not rows:
        return []
    hours_store = hours_store or {}
    duration = int(duration or 1)

    # year labels
    try:
        base = date.fromisoformat(start_date).year
        labels = [str(base + i) for i in range(duration)]
    except:
        labels = [f"Year {i+1}" for i in range(duration)]

    output = []
    for r in rows:
        idx = r['index']
        inputs = [
            dbc.Col(
                dbc.Input(
                    id={"type":"hours-input","index":idx,"year":y},
                    type="number",
                    placeholder=labels[y-1],
                    value=hours_store.get(f"{idx}-{y}", ""),
                ),
                width=12//duration
            )
            for y in range(1, duration+1)
        ]
        output.append(
            dbc.Row([
                dbc.Col(html.P(r['name'], className="mb-0"),     width=3),
                dbc.Col(html.P(r['position'], className="mb-0"), width=2),
                dbc.Col(dbc.Row(inputs, className="g-1"),       width=5),
                dbc.Col(
                    dbc.Checkbox(
                        id={"type":"same-each-year","index":idx},
                        value=r.get('checkbox', False)
                    ),
                    width=2
                ),
            ], className="align-items-center mb-2")
        )
    return output





############################################
# 5️ Save hours-store on input
############################################
@callback(
    Output('hours-store', 'data', allow_duplicate=True),
    Input({'type':'hours-input','index':ALL,'year':ALL}, 'value'),
    State({'type':'hours-input','index':ALL,'year':ALL}, 'id'),
    prevent_initial_call=True
)
def save_hour_values(vals, ids):
    data = {}
    for v, id_obj in zip(vals, ids):
        data[f"{id_obj['index']}-{id_obj['year']}"] = v
    return data


############################################
# 6️ “Same Each Year” copier
############################################
@callback(
    Output({'type':'hours-input','index':MATCH,'year':ALL}, 'value'),
    Input({'type':'same-each-year','index':MATCH}, 'value'),
    State({'type':'hours-input','index':MATCH,'year':ALL}, 'value'),
    prevent_initial_call=True
)
def copy_hours_if_same(checked, year_vals):
    return [year_vals[0]] * len(year_vals) if checked else year_vals


# ========================================================================================================================================

############################################
# Travel Expenses Callbacks
############################################
@callback(
    Output({'type':'travel-itn','scope':MATCH,'field':'days_stay','index':MATCH}, 'value'),
    Input({'type':'travel-itn','scope':MATCH,'field':'departure_date','index':MATCH}, 'date'),
    Input({'type':'travel-itn','scope':MATCH,'field':'arrival_date'  ,'index':MATCH}, 'date'),
    prevent_initial_call=True
)
def compute_days_of_stay(dep_date, arr_date):
    # both dates come in as ISO strings or None
    if not dep_date or not arr_date:
        # if either is missing, clear out
        return None
    try:
        d0 = date.fromisoformat(dep_date)
        d1 = date.fromisoformat(arr_date)
        # ensure arrival ≥ departure
        delta = (d1 - d0).days
        return max(delta, 0)
    except Exception:
        raise PreventUpdate

@callback(
    Output('domestic-travel-store', 'data'),
    Input('add-domestic-travel-btn', 'n_clicks'),
    Input({'type': 'travel-year', 'name': 'remove-row-option-domestic', 'index': ALL}, 'n_clicks'),
    State('domestic-travel-store', 'data'),
    prevent_initial_call=True
)
def update_domestic_travel(add_clicks, delete_clicks, current_data):
    # print("initial value of domestic travel store: ", current_data)
    triggered = ctx.triggered_id
    # print("triggered is: ", triggered)    
    data = current_data or [0]
    # print("current data is: ", data)

    if triggered == 'add-domestic-travel-btn' and add_clicks>0:
        new_idx = (max(data) if data else 0) + 1
        # print("new index is: ", new_idx)
        # print("data that will be returned is : ", (data + [new_idx]) )
        return (data + [new_idx])

    elif isinstance(triggered, dict) and triggered.get('name') == 'remove-row-option-domestic' and any(click and click > 0 for click in delete_clicks):
        index_to_remove = triggered.get('index')
        if len(data) > 1:
            return [i for i in data if i != index_to_remove]
    # print("domestic travel store data in return is: ", data)
    return dash.no_update
# Update domestic travel + itinerary values
@callback(
    Output('domestic-travel-values-store', 'data', allow_duplicate=True),
    Input({'type': 'travel-name', 'scope': 'domestic', 'index': ALL}, 'value'),
    Input({'type': 'travel-desc', 'scope': 'domestic', 'index': ALL}, 'value'),
    Input({'type': 'travel-year', 'scope': 'domestic', 'index': ALL}, 'value'),
    Input({'type': 'travel-itn', 'scope': 'domestic', 'field': ALL, 'index': ALL}, 'value'),
    Input({'type': 'travel-itn', 'scope': 'domestic', 'field': ALL, 'index': ALL}, 'date'),
    State({'type': 'travel-name', 'scope': 'domestic', 'index': ALL}, 'id'),
    State({'type': 'travel-itn', 'scope': 'domestic', 'field': ALL, 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def update_domestic_travel_values(names, descs, years, itn_vals, dates, name_ids, itn_ids):
    data = {}
    # print("domestic travel names are: ", names)
    # print("domestic travel descs are: ", descs)
    # print("domestic travel years are: ", years)
    # print("domestic travel itn vals are: ", itn_vals)
    # print("domestic travel dates are: ", dates)
    # print("domestic travel name ids are: ", name_ids)
    # print("domestic travel itn ids are: ", itn_ids)


    # stash name/desc/year
    for name, desc, year, id_obj in zip(names, descs, years, name_ids):
        idx = str(id_obj['index'])
        if not data.get(idx):
            data[idx] = {}
        if name:
            data[idx]['name'] = name
        if desc:
            data[idx]['desc'] = desc
        if year:
            data[idx]['year'] = year

    # stash itinerary fields
    for val, date_val, id_obj in zip(itn_vals, dates, itn_ids):
        idx = str(id_obj['index'])
        field = id_obj['field']

        if not data.get(idx):
            data[idx] = {}

        if field in ('departure_date', 'arrival_date'):
            if date_val:
                data[idx][field] = date_val
        else:
            if val is not None and val != '':
                data[idx][field] = val

    # print("domestic travel values are: ", data)
    return data




@callback(
    Output('international-travel-store', 'data'),
    Input('add-international-travel-btn', 'n_clicks'),
    Input({'type': 'travel-year', 'name': 'remove-row-option-international', 'index': ALL}, 'n_clicks'),
    State('international-travel-store', 'data'),
    prevent_initial_call=True
)
def update_international_travel(add_clicks, delete_clicks, data):
    # print("initial value of international travel store: ", data)
    triggered = ctx.triggered_id
    data = data or [0]
    # print("current data for international is: ", data)

    if triggered == 'add-international-travel-btn':
        # new_index = max(data) + 1 if data else 1
        new_index = max(data) + 1
        return data + [new_index]

    elif isinstance(triggered, dict) and triggered.get('name') == 'remove-row-option-international' and any(click and click > 0 for click in delete_clicks):
        index_to_remove = triggered.get('index')
        if len(data) > 1:
            return [i for i in data if i != index_to_remove]

    return data







# Update international travel values store
@callback(
    Output('international-travel-values-store', 'data', allow_duplicate=True),
    Input({'type': 'travel-name', 'scope': 'international', 'index': ALL}, 'value'),
    Input({'type': 'travel-desc', 'scope': 'international', 'index': ALL}, 'value'),
    Input({'type': 'travel-year', 'scope': 'international', 'index': ALL}, 'value'),
    Input({'type': 'travel-itn', 'scope': 'international', 'field': ALL, 'index': ALL}, 'value'),
    Input({'type': 'travel-itn', 'scope': 'international', 'field': ALL, 'index': ALL}, 'date'),  # ADDED to match domestic structure
    State({'type': 'travel-name', 'scope': 'international', 'index': ALL}, 'id'),
    State({'type': 'travel-itn', 'scope': 'international', 'field': ALL, 'index': ALL}, 'id'),
    prevent_initial_call=True
)
def update_international_travel_values(names, descs, years, itn_vals, dates, name_ids, itn_ids):
    data = {}

    # stash name/desc/year
    for name, desc, year, id_obj in zip(names, descs, years, name_ids):
        idx = str(id_obj['index'])
        if not data.get(idx):
            data[idx] = {}
        if name:
            data[idx]['name'] = name
        if desc:
            data[idx]['desc'] = desc
        if year:
            data[idx]['year'] = year

    # stash itinerary fields
    for val, date_val, id_obj in zip(itn_vals, dates, itn_ids):
        idx = str(id_obj['index'])
        field = id_obj['field']

        if not data.get(idx):
            data[idx] = {}

        if field in ('departure_date', 'arrival_date'):
            if date_val:
                data[idx][field] = date_val
        else:
            if val is not None and val != '':
                data[idx][field] = val

    # print("International travel values are: ", data)
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
        {
            "label": f"Year {i+1} ({(start_date_obj + relativedelta(years=i)).year})",
            "value": (start_date_obj + relativedelta(years=i)).year
        }
        for i in range(duration)
    ]
    for i in indexes:
        val = stored_data.get(str(i), {})
        rows.append(
            html.Div(children=[
                # — first line: name / desc / year / depart / arrive / ❌
                dbc.Row([
                    dbc.Col(
                        dbc.Input(
                            id={"type": "travel-name", "scope": "domestic", "index": i},
                            placeholder="Travel Name",
                            value=val.get('name', "")
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Textarea(
                            id={"type": "travel-desc", "scope": "domestic", "index": i},
                            placeholder="Description",
                            value=val.get('desc', ""),
                            style={"height": "38px"}
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Select(
                            id={"type": "travel-year", "scope": "domestic", "index": i},
                            options=year_options,
                            value=val.get('year', None),
                            placeholder="Select Year"
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id={'type':'travel-itn','scope':'domestic','field':'departure_date','index':i},
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + relativedelta(years=+duration),
                            placeholder='Depart', 
                            date=val.get('departure_date')
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id={'type':'travel-itn','scope':'domestic','field':'arrival_date','index':i},
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + relativedelta(years=+duration),
                            placeholder='Arrive', 
                            date=val.get('arrival_date')
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Button(
                            "❌",
                            id={"type": "travel-year", "name": "remove-row-option-domestic", "index": i},
                            color="danger", size="sm", className="bg-light mt-1",
                        ),
                        width=1,
                        className="d-flex align-items-center justify-content-center"
                    ),
                ], className="mb-2 px-0 align-items-center"),

                # — section heading —
                html.Div(
                    html.U("Transportation, Food & Lodging Details"),
                    className="text-muted text-center mb-1"
                ),

                # — second line: flight / taxi / food_lodging / days —
                dbc.Row([
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'domestic','field':'flight_cost','index':i},
                            type='number', placeholder='Flight $', 
                            value=val.get('flight_cost')
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'domestic','field':'transportation_cost','index':i},
                            type='number', placeholder='Taxi/Uber $/day', 
                            value=val.get('transportation_cost')
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'domestic','field':'food_lodging_cost','index':i},
                            type='number', placeholder='Food & Lodge $/day', 
                            value=val.get('food_lodging_cost')
                        ),
                        width=4
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'domestic','field':'days_stay','index':i},
                            value=val.get('days_stay'),
                            type='number', placeholder='Days',
                            disabled=True,

                        ),
                        width=2
                    ),
                ], className="mb-3 px-0 align-items-center"),
                html.Br(),
            ])
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
        {
            "label": f"Year {i+1} ({(start_date_obj + relativedelta(years=i)).year})",
            "value": (start_date_obj + relativedelta(years=i)).year
        }
        for i in range(duration)
    ]

    for i in indexes:
        val = stored_data.get(str(i), {})

        rows.append(
            html.Div(children=[
                # — first line: name / desc / year / depart / arrive / ❌
                dbc.Row([
                    dbc.Col(
                        dbc.Input(
                            id={"type": "travel-name", "scope": "international", "index": i},
                            placeholder="Travel Name",
                            value=val.get('name', "")
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Textarea(
                            id={"type": "travel-desc", "scope": "international", "index": i},
                            placeholder="Description",
                            value=val.get('desc', ""),
                            style={"height": "38px"}
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Select(
                            id={"type": "travel-year", "scope": "international", "index": i},
                            options=year_options,
                            value=val.get('year', None),
                            placeholder="Select Year"
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id={'type':'travel-itn','scope':'international','field':'departure_date','index':i},
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + relativedelta(years=+duration),
                            placeholder='Depart', 
                            date=val.get('departure_date')
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id={'type':'travel-itn','scope':'international','field':'arrival_date','index':i},
                            min_date_allowed=date.today(),
                            max_date_allowed=date.today() + relativedelta(years=+duration),
                            placeholder='Arrive', 
                            date=val.get('arrival_date')
                        ),
                        width=2
                    ),
                    dbc.Col(
                        dbc.Button(
                            "❌",
                            id={"type": "travel-year", "name": "remove-row-option-international", "index": i},
                            color="danger", size="sm",className="bg-light mt-1",
                        ),
                        width=1,
                        className="d-flex align-items-center justify-content-center"
                    ),
                ], className="mb-2 px-0 align-items-center"),

                # — section heading —
                html.Div(
                    html.U("Transportation, Food & Lodging Details"),
                    className="text-muted text-center mb-1"
                ),

                # — second line: flight / taxi / food_lodging / days —
                dbc.Row([
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'international','field':'flight_cost','index':i},
                            type='number', placeholder='Flight $', 
                            value=val.get('flight_cost')
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'international','field':'transportation_cost','index':i},
                            type='number', placeholder='Taxi/Uber $/day', 
                            value=val.get('transportation_cost')
                        ),
                        width=3
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'international','field':'food_lodging_cost','index':i},
                            type='number', placeholder='Food & Lodge $/day', 
                            value=val.get('food_lodging_cost')
                        ),
                        width=4
                    ),
                    dbc.Col(
                        dbc.Input(
                            id={'type':'travel-itn','scope':'international','field':'days_stay','index':i},
                            value=val.get('days_stay'),
                            type='number', placeholder='Days',
                            disabled=True,
                        ),
                        width=2
                    ),
                ], 
                className="mb-3 px-0 align-items-center") 
                ,
                html.Br(),
            ],)
        )

    return rows






############################################
# Material and Supplies Callbacks
############################################

@callback(
    Output('materials-store', 'data'),
    Input('add-material-btn', 'n_clicks'),
    Input({'type': 'material', 'name': 'remove-row-option', 'index': ALL}, 'n_clicks'),
    State('materials-store', 'data'),
    prevent_initial_call=True
)
def update_materials(add_clicks, delete_clicks, data):
    triggered = ctx.triggered_id
    data = data or [0]

    if triggered == 'add-material-btn':
        new_index = max(data) + 1 if data else 1
        return data + [new_index]

    elif isinstance(triggered, dict) and triggered.get('name') == 'remove-row-option' and any(click and click > 0 for click in delete_clicks):
        index_to_remove = triggered['index']
        if len(data) > 1:
            return [i for i in data if i != index_to_remove]

    return data

# @callback(
#     Output('remove-material-btn', 'style'),
#     Input('materials-store', 'data')
# )
# def toggle_remove_material_button(data):
#     return {"text-align": "center", "display": "block"} if len(data) > 1 else {"text-align": "center", "display": "none"}



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
                ), width=4),
                dbc.Col(dbc.Select(
                    id={"type": "material-year", "index": i},
                    options=year_options,
                    value=val.get('year', None),
                    placeholder="Select Year"
                ), width=2),
                dbc.Col(
                        children=[
                            # dbc.Label("Remove", className="mb-1"),
                            dbc.Button(
                                "❌",
                                id={"type": "material", "name": "remove-row-option", "index": i},
                                color="danger",
                                size="sm",
                                className="bg-light mt-1",  # adds space between label and button
                                disabled=False
                            ),
                        ],
                        width=1,
                        className="d-flex flex-column align-items-center"
                    ),
                
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




# reset all the fields when I press the clear button. 
@callback(
    Output('clear-url', 'href'),
    Input('clear-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reload_page(n_clicks):
    return "/home/generate-grants"







# callback for edit options
############################################
# Edit Grant Callbacks
############################################

@callback(
    # 1) PERSONNEL
    Output('personnel-store', 'data', allow_duplicate=True),
    # 2) HOURS
    Output('hours-store', 'data'),
    # 3) DOMESTIC TRAVEL
    Output('domestic-travel-store',       'data', allow_duplicate=True),
    Output('domestic-travel-values-store','data'),
    # 4) INTERNATIONAL TRAVEL
    Output('international-travel-store',       'data', allow_duplicate=True),
    Output('international-travel-values-store','data'),
    # 5) MATERIALS
    Output('materials-store',        'data', allow_duplicate=True),
    Output('materials-values-store','data'),
    # 6) METADATA
    Output({'type':'grant-input','name':'grant-title'},       'value'),
    Output({'type':'grant-input','name':'funding-agency'},    'value'),
    Output({'type':'grant-input','name':'total-duration'},    'value'),
    Output({'type':'grant-input','name':'grant-status'},      'value'),
    Output({'type':'grant-input','name':'start-date'},        'date'),
    Output({'type':'grant-input','name':'end-date'},          'date', allow_duplicate=True),
    Output({'type':'grant-input','name':'grant-description'}, 'value'),

    Input("debug-edit-id", "children"),
    Input("edit-grant-id", "data"),
    prevent_initial_call=True
)
def load_all_grant_fields(_, grant_id):
    print("Loading grant ID:", grant_id)
    if not grant_id:
        raise PreventUpdate

    session = get_db_session()
    try:
        grant = session.query(Grant).filter_by(id=int(grant_id),
                                                user_id=current_user.id).first()
        if not grant:
            raise PreventUpdate

        def normalize_empty(v):
            return v if v not in ("", None) else None

        # ─── PERSONNEL + HOURS ───
        start_year = grant.start_date.year
        grouped = OrderedDict()
        for p in session.query(GrantPersonnel)\
                        .filter_by(grant_id=grant_id):
            key = (p.name, p.position)
            grouped.setdefault(key, {})[p.year - start_year + 1] = p.estimated_hours

        personnel_rows = []
        hours_data     = {}
        for idx, ((name, position), year_map) in enumerate(grouped.items(), start=1):
            personnel_rows.append({
                "index":    idx,
                "name":     name,
                "position": position,
                "checkbox": False
            })
            for offset, hrs in year_map.items():
                hours_data[f"{idx}-{offset}"] = hrs

        # ─── DOMESTIC TRAVEL ───
        dom_rows = session.query(GrantTravel)\
                            .filter_by(grant_id=grant_id,
                                        travel_type='Domestic')\
                            .all()
        dom_indices = [i+1 for i in range(len(dom_rows))]
        dom_data = {}
        for idx, t in enumerate(dom_rows, start=1):
            entry = {
                "name": t.name,
                "desc": t.description,
                "year": t.year,
            }
            # if there’s an itinerary record, unpack its fields
            if getattr(t, "itinerary", None):
                it = t.itinerary
                entry.update({
                    "departure_date": it.departure_date.isoformat() if it.departure_date else None,
                    "arrival_date":   it.arrival_date.isoformat()   if it.arrival_date   else None,
                    "flight_cost":    float(it.flight_cost)         if it.flight_cost    is not None else None,
                    "transportation_cost": float(it.per_day_transportation) if it.per_day_transportation is not None else None,
                    "food_lodging_cost":   float(it.per_day_food_lodging)   if it.per_day_food_lodging   is not None else None,
                    "days_stay":      it.days_stay,
                })
            dom_data[str(idx)] = entry

        # ─── INTERNATIONAL TRAVEL ───
        intl_rows = session.query(GrantTravel)\
                            .filter_by(grant_id=grant_id,
                                        travel_type='International')\
                            .all()
        int_indices = [i+1 for i in range(len(intl_rows))]
        int_data = {}
        for idx, t in enumerate(intl_rows, start=1):
            entry = {
                "name": t.name,
                "desc": t.description,
                "year": t.year,
            }
            if getattr(t, "itinerary", None):
                it = t.itinerary
                entry.update({
                    "departure_date": it.departure_date.isoformat() if it.departure_date else None,
                    "arrival_date":   it.arrival_date.isoformat()   if it.arrival_date   else None,
                    "flight_cost":    float(it.flight_cost)         if it.flight_cost    is not None else None,
                    "transportation_cost": float(it.per_day_transportation) if it.per_day_transportation is not None else None,
                    "food_lodging_cost":   float(it.per_day_food_lodging)   if it.per_day_food_lodging   is not None else None,
                    "days_stay":      it.days_stay,
                })
            int_data[str(idx)] = entry

        # ─── MATERIALS & SUPPLIES ───
        mat_rows = session.query(GrantMaterial)\
                          .filter_by(grant_id=grant_id)\
                          .all()
        mat_indices = [i+1 for i in range(len(mat_rows))]
        mat_data = {}
        for i, m in enumerate(mat_rows, start=1):
            sub = session.query(ExpenseSubcategory).get(m.subcategory_id)
            mat_data[str(i)] = {
                "name": sub.name     if sub else None,
                "desc": m.description,
                "cost": m.cost,
                "year": m.year
            }

        # ─── METADATA ───
        title   = grant.title
        agency  = grant.funding_agency
        dur     = grant.duration
        status  = grant.status
        sd      = grant.start_date.isoformat()
        ed      = (grant.start_date + relativedelta(years=+dur))\
                     .isoformat() if grant.end_date is None else grant.end_date.isoformat()
        desc    = normalize_empty(grant.description)

        print("personnel rows are: ", personnel_rows)
        print("hours data is: ", hours_data)
        return (
            # personnel + hours
            personnel_rows, hours_data,
            # domestic travel
            dom_indices, dom_data,
            # international travel
            int_indices, int_data,
            # materials
            mat_indices, mat_data,
            # metadata
            title, agency, dur, status, sd, ed, desc
        )

    finally:
        session.close()




@callback(
    Output("debug-edit-id", "children"),
    Input("edit-grant-id", "data"), 
    prevent_initial_call=False
)
def show_debug_data(data):
    if data is not None:
        session = get_db_session()
        try:
            grant = session.query(Grant).filter_by(id=int(data)).first()
            print("Grant Is:", grant)
            print("name : ", grant.title)
            print("id :", grant.id)
            print("status :", grant.status)
        finally:
            session.close()
        return f"Edit grant ID: {data, grant.id , grant.title , grant.status}"
    return f"Edit grant ID: {data}"



@dash.callback(
    Output('dummy-output', 'children'),
    Input('domestic-travel-store', 'data'),
    Input('international-travel-store', 'data'),
    Input("personnel-store", "data"),
    Input("hours-store", "data"),
    prevent_initial_call=True
)
def log_store_changes(domestic_travel, international_travel, personnel_data, hours_data):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'domestic-travel-store':
        print("🚨 Domestic travel store updated:", domestic_travel)
    elif trigger_id == 'international-travel-store':
        print("🌐 International travel store updated:", international_travel)
    elif trigger_id == 'personnel-store':
        print("👤 Personnel store updated:", personnel_data)
    elif trigger_id == 'hours-store':
        print("⏰ Hours store updated:", hours_data)

    return dash.no_update