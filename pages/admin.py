import dash
from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
from sqlalchemy.orm import sessionmaker
from db_utils import get_db_session
from models import User, Grant, NSFPersonnelCompensation, NIHPersonnelCompensation, NSFFringeRate, NIHFringeRate, ExpenseCategory, ExpenseSubcategory, GraduateStudentCost, PI, CoPI, ProfessionalStaff, Postdoc, GRA, TempHelp, Undergrad
import os
from dotenv import load_dotenv
load_dotenv()


ADMIN_SECRET = os.getenv("ADMIN_SECRET")


# Register as a Dash page
dash.register_page(__name__, path="/home/admin")


# User 
# Grant
# GrantPersonnel
# GrantTravel
# TravelItinerary 
# GrantMaterial 
# ExpenseSubcategory 
# PI, CoPI 
# ProfessionalStaff
# Postdoc 
# GRA
# Undergrad
# TempHelp
# NSFPersonnelCompensation
# NIHPersonnelCompensation
# NSFFringeRate
# NIHFringeRate
# GraduateStudentCost
# ExpenseCategory



# SQLAlchemy session
# Session = sessionmaker(bind=engine)

def fetch_table_data():
    session = get_db_session()
    data = {
        "users": pd.read_sql(session.query(User).statement, session.bind),
        "grants": pd.read_sql(session.query(Grant).statement, session.bind),
        "nsf_comp": pd.read_sql(session.query(NSFPersonnelCompensation).statement, session.bind),
        "nih_comp": pd.read_sql(session.query(NIHPersonnelCompensation).statement, session.bind),
        "nsf_fringe": pd.read_sql(session.query(NSFFringeRate).statement, session.bind),
        "nih_fringe": pd.read_sql(session.query(NIHFringeRate).statement, session.bind),
        "categories": pd.read_sql(session.query(ExpenseCategory).statement, session.bind),
        "subcategories": pd.read_sql(session.query(ExpenseSubcategory).statement, session.bind),
        "grad_cost": pd.read_sql(session.query(GraduateStudentCost).statement, session.bind), 
        "pi": pd.read_sql(session.query(PI).statement, session.bind),
        "copi": pd.read_sql(session.query(CoPI).statement, session.bind),
        "staff": pd.read_sql(session.query(ProfessionalStaff).statement, session.bind),
        "postdoc": pd.read_sql(session.query(Postdoc).statement, session.bind),
        "gra": pd.read_sql(session.query(GRA).statement, session.bind),
        "temp": pd.read_sql(session.query(TempHelp).statement, session.bind),
        "undergrad": pd.read_sql(session.query(Undergrad).statement, session.bind)
    }
    session.close()
    return data

def layout():
    return dbc.Container([
        dcc.Store(id="admin-authenticated", data=False),

        dbc.Modal([
            dbc.ModalHeader("Admin Access"),
            dbc.ModalBody([
                dbc.Input(id="admin-key-input", type="password", placeholder="Enter Admin Secret", debounce=True),
                html.Div(id="admin-auth-error", style={"color": "red", "marginTop": "0.5rem"})
            ]),
            dbc.ModalFooter(
                dbc.Button("Submit", id="submit-admin-key", color="primary")
            ),
        ], id="admin-auth-modal", is_open=True, backdrop="static", centered=True),

        html.H1("Admin Dashboard", className="text-center my-4"),

        html.Div(id="admin-content", style={"display": "none"}, children=[
            dcc.Tabs(id="admin-tabs", value="users-tab", children=[
                dcc.Tab(label="Users", value="users-tab"),
                dcc.Tab(label="Grants", value="grants-tab"),
                dcc.Tab(label="NSF/NIH Compensation", value="comp-tab"),
                dcc.Tab(label="Fringe Rates", value="fringe-tab"),
                dcc.Tab(label="Expense Categories", value="categories-tab"),
                dcc.Tab(label="Grad Cost", value="grad-tab"),
                dcc.Tab(label="PI", value="pi-tab"),
                dcc.Tab(label="Co-PI", value="copi-tab"),
                dcc.Tab(label="Professional Staff", value="staff-tab"),
                dcc.Tab(label="Postdoc", value="postdoc-tab"),
                dcc.Tab(label="GRA", value="gra-tab"),
                dcc.Tab(label="Temp Help", value="temp-tab"),
                dcc.Tab(label="Undergrad", value="undergrad-tab")
            ]),
            html.Div(id="tab-content")
        ])
    ], fluid=True)


@callback(
    Output("tab-content", "children"),
    Input("admin-tabs", "value")
)
def render_tab(tab):
    data = fetch_table_data()

    if tab == "users-tab":
        return html.Div([
            html.H5("Manage Users"),
            dash_table.DataTable(
                data=data['users'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": False} for i in data['users'].columns],
                row_deletable=True,
                style_table={'overflowX': 'auto'},
                id="user-table"
            ), 
            html.Button("Save User Changes", id="save-user-btn", className="btn btn-success mt-2")
        ])

    elif tab == "grants-tab":
        df = data['grants'].merge(data['users'][['id', 'username']], left_on='user_id', right_on='id', suffixes=('', '_user'))
        return html.Div([
            html.H5("Grants and Owners"),
            dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i, "editable": False} for i in df.columns],
                row_deletable=True,
                style_table={'overflowX': 'auto'},
                id="grant-table"
            ), 
            html.Button("Save Grant Changes", id="save-grant-btn", className="btn btn-success mt-2")
        ])

    elif tab == "comp-tab":
        return html.Div([
            html.H5("NSF Compensation Table"),
            dash_table.DataTable(
                data=data['nsf_comp'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": True} for i in data['nsf_comp'].columns],
                editable=True,
                id="nsf-comp-table"
            ),
            html.Button("Save NSF Compensation", id="save-nsf-comp-btn", className="btn btn-success mt-2"),
            html.Hr(),
            html.H5("NIH Compensation Table"),
            dash_table.DataTable(
                data=data['nih_comp'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": True} for i in data['nih_comp'].columns],
                editable=True,
                id="nih-comp-table"
            ),
            html.Button("Save NIH Compensation", id="save-nih-comp-btn", className="btn btn-success mt-2")
        ])

    elif tab == "fringe-tab":
        return html.Div([
            html.H5("NSF Fringe Rates"),
            dash_table.DataTable(
                data=data['nsf_fringe'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": True} for i in data['nsf_fringe'].columns],
                editable=True,
                id="nsf-fringe-table"
            ),
            html.Button("Save NSF Fringe", id="save-nsf-fringe-btn", className="btn btn-success mt-2"),
            html.Hr(),
            html.H5("NIH Fringe Rates"),
            dash_table.DataTable(
                data=data['nih_fringe'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": True} for i in data['nih_fringe'].columns],
                editable=True,
                id="nih-fringe-table"
            ),
            html.Button("Save NIH Fringe", id="save-nih-fringe-btn", className="btn btn-success mt-2")
        ])

    elif tab == "categories-tab":
        return html.Div([
            html.H5("Expense Categories"),
            dash_table.DataTable(
                data=data['categories'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": i != 'id'} for i in data['categories'].columns],
                editable=True,
                row_deletable=True,
                id="category-table"
            ),
            html.Hr(),
            html.H5("Expense Subcategories"),
            dash_table.DataTable(
                data=data['subcategories'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": i != 'id'} for i in data['subcategories'].columns],
                editable=True,
                row_deletable=True,
                id="subcategory-table"
            ),
            html.Button("Save Expense Categories", id="save-category-btn", className="btn btn-success mt-2")
        ])

    elif tab == "grad-tab":
        return html.Div([
            html.H5("Graduate Student Costs"),
            dash_table.DataTable(
                data=data['grad_cost'].to_dict("records"),
                columns=[{"name": i, "id": i, "editable": True} for i in data['grad_cost'].columns],
                editable=True,
                id="grad-cost-table"
            ),
            html.Button("Save Grad Cost", id="save-grad-cost-btn", className="btn btn-success mt-2")
        ])
    elif tab == "pi-tab":
        return html.Div([
            html.H5("Principal Investigators"),
            dash_table.DataTable(
                data=data['pi'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="pi-table"
            ),
            html.Button("Save PI Changes", id="save-pi-btn", className="btn btn-success mt-2"),
            html.Button("Add PI Row", id="add-pi-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "copi-tab":
        return html.Div([
            html.H5("Co-Principal Investigators"),
            dash_table.DataTable(
                data=data['copi'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="copi-table"
            ),
            html.Button("Save Co-PI Changes", id="save-copi-btn", className="btn btn-success mt-2"),
            html.Button("Add Co-PI Row", id="add-copi-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "staff-tab":
        return html.Div([
            html.H5("Professional Staff"),
            dash_table.DataTable(
                data=data['staff'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="staff-table"
            ),
            html.Button("Save Staff Changes", id="save-staff-btn", className="btn btn-success mt-2"),
            html.Button("Add Staff Row", id="add-staff-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "postdoc-tab":
        return html.Div([
            html.H5("Postdoctoral Researchers"),
            dash_table.DataTable(
                data=data['postdoc'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="postdoc-table"
            ),
            html.Button("Save Postdoc Changes", id="save-postdoc-btn", className="btn btn-success mt-2"),
            html.Button("Add Postdoc Row", id="add-postdoc-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "gra-tab":
        return html.Div([
            html.H5("Graduate Research Assistants"),
            dash_table.DataTable(
                data=data['gra'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="gra-table"
            ),
            html.Button("Save GRA Changes", id="save-gra-btn", className="btn btn-success mt-2"),
            html.Button("Add GRA Row", id="add-gra-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "temp-tab":
        return html.Div([
            html.H5("Temporary Help"),
            dash_table.DataTable(
                data=data['temp'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="temp-table"
            ),
            html.Button("Save Temp Help Changes", id="save-temp-btn", className="btn btn-success mt-2"),
            html.Button("Add Temp Help Row", id="add-temp-row", className="btn btn-secondary mt-2"),
        ])
    elif tab == "undergrad-tab":
        return html.Div([
            html.H5("Undergraduate Assistants"),
            dash_table.DataTable(
                data=data['undergrad'].to_dict("records"),
                columns=[
                    {"name": "id", "id": "id", "editable": False},
                    {"name": "full_name", "id": "full_name", "editable": True},
                    {"name": "email", "id": "email", "editable": True},
                    {"name": "position", "id": "position", "editable": False},
                    {"name": "expected_hourly_salary", "id": "expected_hourly_salary", "editable": True}
                ],
                editable=True,
                row_deletable=True,
                id="undergrad-table"
            ),
            html.Button("Save Undergrad Changes", id="save-undergrad-btn", className="btn btn-success mt-2"),
            html.Button("Add Undergrad Row", id="add-undergrad-row", className="btn btn-secondary mt-2"),
        ])






@callback(
    Output("save-user-btn", "children"),
    Input("save-user-btn", "n_clicks"),
    State("user-table", "data"),
    prevent_initial_call=True
)
def save_user_changes(n_clicks, updated_data):
    session = get_db_session()
    try:
        existing_ids = {u.id for u in session.query(User.id).all()}
        current_ids = {row['id'] for row in updated_data}
        deleted_ids = existing_ids - current_ids

        for uid in deleted_ids:
            session.query(User).filter_by(id=uid).delete()

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()



@callback(
    Output("save-grant-btn", "children"),
    Input("save-grant-btn", "n_clicks"),
    State("grant-table", "data"),
    prevent_initial_call=True
)
def save_grant_changes(n_clicks, updated_data):
    session = get_db_session()
    try:
        existing_ids = {g.id for g in session.query(Grant.id).all()}
        current_ids = {row['id'] for row in updated_data}
        deleted_ids = existing_ids - current_ids

        for gid in deleted_ids:
            session.query(Grant).filter_by(id=gid).delete()

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()




@callback(
    Output("save-nsf-comp-btn", "children"),
    Input("save-nsf-comp-btn", "n_clicks"),
    State("nsf-comp-table", "data"),
    prevent_initial_call=True
)
def save_nsf_comp(n_clicks, data):
    session = get_db_session()
    try:
        for row in data:
            item = session.query(NSFPersonnelCompensation).get(row["id"])
            if item:
                item.role = row["role"]
                item.y2_rate_increase = float(row["y2_rate_increase"])
                item.y3_rate_increase = float(row["y3_rate_increase"])
                item.y4_rate_increase = float(row["y4_rate_increase"])
                item.y5_rate_increase = float(row["y5_rate_increase"])
        session.commit()
        return "✅ Saved!"
    except Exception as e:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("save-nih-comp-btn", "children"),
    Input("save-nih-comp-btn", "n_clicks"),
    State("nih-comp-table", "data"),
    prevent_initial_call=True
)
def save_nih_comp(n_clicks, data):
    session = get_db_session()
    try:
        for row in data:
            item = session.query(NIHPersonnelCompensation).get(row["id"])
            if item:
                item.role = row["role"]
                item.y2_rate_increase = float(row["y2_rate_increase"])
                item.y3_rate_increase = float(row["y3_rate_increase"])
                item.y4_rate_increase = float(row["y4_rate_increase"])
                item.y5_rate_increase = float(row["y5_rate_increase"])
        session.commit()
        return "✅ Saved!"
    except Exception as e:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("save-nsf-fringe-btn", "children"),
    Input("save-nsf-fringe-btn", "n_clicks"),
    State("nsf-fringe-table", "data"),
    prevent_initial_call=True
)
def save_nsf_fringe(n_clicks, data):
    session = get_db_session()
    try:
        for row in data:
            item = session.query(NSFFringeRate).get(row["id"])
            if item:
                item.role = row["role"]
                item.year = row["year"]
                item.fringe_rate = float(row["fringe_rate"])
        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("save-nih-fringe-btn", "children"),
    Input("save-nih-fringe-btn", "n_clicks"),
    State("nih-fringe-table", "data"),
    prevent_initial_call=True
)
def save_nih_fringe(n_clicks, data):
    session = get_db_session()
    try:
        for row in data:
            item = session.query(NIHFringeRate).get(row["id"])
            if item:
                item.role = row["role"]
                item.year = row["year"]
                item.fringe_rate = float(row["fringe_rate"])
        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("save-category-btn", "children"),
    Input("save-category-btn", "n_clicks"),
    State("category-table", "data"),
    State("subcategory-table", "data"),
    prevent_initial_call=True
)
def save_categories(n_clicks, cat_data, subcat_data):
    session = get_db_session()
    try:
        for row in cat_data:
            item = session.query(ExpenseCategory).get(row["id"])
            if item:
                item.name = row["name"]
                item.description = row["description"]
        for row in subcat_data:
            item = session.query(ExpenseSubcategory).get(row["id"])
            if item:
                item.category_id = row["category_id"]
                item.name = row["name"]
                item.description = row["description"]
        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("save-grad-cost-btn", "children"),
    Input("save-grad-cost-btn", "n_clicks"),
    State("grad-cost-table", "data"),
    prevent_initial_call=True
)
def save_grad_cost(n_clicks, data):
    session = get_db_session()
    try:
        for row in data:
            item = session.query(GraduateStudentCost).get(row["id"])
            if item:
                item.student_type = row["student_type"]
                item.base_tuition_per_semester = float(row["base_tuition_per_semester"])
                item.summer_credit_cost = float(row["summer_credit_cost"])
                item.health_insurance_cost = float(row["health_insurance_cost"])
                item.num_semesters_per_year = int(row["num_semesters_per_year"])
                item.annual_increase_percent = float(row["annual_increase_percent"])
                item.total_years = int(row["total_years"])
        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()






@callback(
    Output("admin-authenticated", "data"),
    Output("admin-auth-modal", "is_open"),
    Output("admin-auth-error", "children"),
    Input("submit-admin-key", "n_clicks"),
    State("admin-key-input", "value"),
    prevent_initial_call=True
)
def check_admin_key(n_clicks, key_input):
    if key_input == ADMIN_SECRET:
        return True, False, ""
    return False, True, "❌ Invalid key. Try again."


@callback(
    Output("admin-content", "style"),
    Input("admin-authenticated", "data")
)
def toggle_admin_content(is_authenticated):
    if is_authenticated:
        return {"display": "block"}
    return {"display": "none"}






# ====================
# adding personnels
# Add-row callbacks for each personnel type
@callback(
    Output("pi-table", "data"),
    Input("add-pi-row", "n_clicks"),
    State("pi-table", "data"),
    State("pi-table", "columns"),
    prevent_initial_call=True
)
def add_pi_row(n, rows, cols):
    new_row = {c['id']: "" for c in cols}
    new_row["position"] = "PI"  # autofill position
    return rows + [new_row]

@callback(
    Output("save-pi-btn", "children"),
    Input("save-pi-btn", "n_clicks"),
    State("pi-table", "data"),
    prevent_initial_call=True
)
def save_pi_changes(n_clicks, data):
    from models import PI
    session = get_db_session()
    try:
        # 1. Fetch all existing IDs
        existing_ids = {p.id for p in session.query(PI.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        # 2. Delete removed rows
        for did in deleted_ids:
            session.query(PI).filter_by(id=did).delete()

        # 3. Update existing and insert new rows
        for row in data:
            if "id" in row and row["id"]:
                item = session.query(PI).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(PI(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="PI",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()



# === Co-PI Add Row Callback ===
@callback(
    Output("copi-table", "data"),
    Input("add-copi-row", "n_clicks"),
    State("copi-table", "data"),
    State("copi-table", "columns"),
    prevent_initial_call=True
)
def add_copi_row(n, rows, cols):
    new_row = {c['id']: "" for c in cols}
    new_row["position"] = "Co-PI"
    return rows + [new_row]


# === Co-PI Save Callback ===
@callback(
    Output("save-copi-btn", "children"),
    Input("save-copi-btn", "n_clicks"),
    State("copi-table", "data"),
    prevent_initial_call=True
)
def save_copi_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(CoPI.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(CoPI).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(CoPI).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(CoPI(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="Co-PI",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()


@callback(
    Output("staff-table", "data"),
    Input("add-staff-row", "n_clicks"),
    State("staff-table", "data"),
    State("staff-table", "columns"),
    prevent_initial_call=True
)
def add_staff_row(n_clicks, rows, cols):
    new_row = {c["id"]: "" for c in cols}
    new_row["position"] = "Professional Staff"
    return rows + [new_row]

@callback(
    Output("save-staff-btn", "children"),
    Input("save-staff-btn", "n_clicks"),
    State("staff-table", "data"),
    prevent_initial_call=True
)
def save_staff_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(ProfessionalStaff.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(ProfessionalStaff).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(ProfessionalStaff).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(ProfessionalStaff(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="Professional Staff",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()



@callback(
    Output("postdoc-table", "data"),
    Input("add-postdoc-row", "n_clicks"),
    State("postdoc-table", "data"),
    State("postdoc-table", "columns"),
    prevent_initial_call=True
)
def add_postdoc_row(n_clicks, rows, cols):
    new_row = {c["id"]: "" for c in cols}
    new_row["position"] = "Postdoc"
    return rows + [new_row]

@callback(
    Output("save-postdoc-btn", "children"),
    Input("save-postdoc-btn", "n_clicks"),
    State("postdoc-table", "data"),
    prevent_initial_call=True
)
def save_postdoc_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(Postdoc.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(Postdoc).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(Postdoc).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(Postdoc(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="Postdoc",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()



@callback(
    Output("gra-table", "data"),
    Input("add-gra-row", "n_clicks"),
    State("gra-table", "data"),
    State("gra-table", "columns"),
    prevent_initial_call=True
)
def add_gra_row(n_clicks, rows, cols):
    new_row = {c["id"]: "" for c in cols}
    new_row["position"] = "GRA"
    return rows + [new_row]

@callback(
    Output("save-gra-btn", "children"),
    Input("save-gra-btn", "n_clicks"),
    State("gra-table", "data"),
    prevent_initial_call=True
)
def save_gra_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(GRA.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(GRA).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(GRA).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(GRA(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="GRA",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()




@callback(
    Output("temp-table", "data"),
    Input("add-temp-row", "n_clicks"),
    State("temp-table", "data"),
    State("temp-table", "columns"),
    prevent_initial_call=True
)
def add_temp_row(n_clicks, rows, cols):
    new_row = {c["id"]: "" for c in cols}
    new_row["position"] = "Temp Help"
    return rows + [new_row]

@callback(
    Output("save-temp-btn", "children"),
    Input("save-temp-btn", "n_clicks"),
    State("temp-table", "data"),
    prevent_initial_call=True
)
def save_temp_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(TempHelp.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(TempHelp).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(TempHelp).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(TempHelp(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="Temp Help",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()



@callback(
    Output("undergrad-table", "data"),
    Input("add-undergrad-row", "n_clicks"),
    State("undergrad-table", "data"),
    State("undergrad-table", "columns"),
    prevent_initial_call=True
)
def add_undergrad_row(n_clicks, rows, cols):
    new_row = {c["id"]: "" for c in cols}
    new_row["position"] = "Undergrad"
    return rows + [new_row]

@callback(
    Output("save-undergrad-btn", "children"),
    Input("save-undergrad-btn", "n_clicks"),
    State("undergrad-table", "data"),
    prevent_initial_call=True
)
def save_undergrad_changes(n_clicks, data):
    session = get_db_session()
    try:
        existing_ids = {p.id for p in session.query(Undergrad.id).all()}
        current_ids = {row.get("id") for row in data if row.get("id")}
        deleted_ids = existing_ids - current_ids

        for did in deleted_ids:
            session.query(Undergrad).filter_by(id=did).delete()

        for row in data:
            if row.get("id"):
                item = session.query(Undergrad).get(row["id"])
                if item:
                    item.full_name = row["full_name"]
                    item.email = row["email"]
                    item.expected_hourly_salary = float(row["expected_hourly_salary"])
            else:
                session.add(Undergrad(
                    full_name=row["full_name"],
                    email=row["email"],
                    position="Undergrad",
                    expected_hourly_salary=float(row["expected_hourly_salary"])
                ))

        session.commit()
        return "✅ Saved!"
    except:
        session.rollback()
        return "❌ Error"
    finally:
        session.close()
