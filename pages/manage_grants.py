import dash
from dash import html


dash.register_page(__name__, path='/view-grants')

def layout():
    layout = html.Div([
        html.H1('This is our manage_grants page'),
        html.Div('This is our manage_grants page content.'),
    ])
    return layout
    

# import dash
# from dash import html, dcc, Input, Output, State, callback, ctx
# import dash_bootstrap_components as dbc
# from flask_login import current_user
# from sqlalchemy.exc import SQLAlchemyError
# from models import Grant, GrantPersonnel, GrantTravel, GrantMaterial, ExpenseSubcategory
# from db_utils import get_db_session
# from datetime import date
# from dateutil.relativedelta import relativedelta

# # Register this page
# dash.register_page(__name__, path='/manage-grants')

# # Toasts
# success_toast = dbc.Toast(
#     "Grant successfully updated!",
#     id="success-toast",
#     is_open=False,
#     duration=4000,
#     header="Success",
#     icon="success",
#     className="mb-3",
#     style={"position": "fixed", "top": 66, "right": 10, "width": 350},
# )

# failure_toast = dbc.Toast(
#     "Error: Grant update failed.",
#     id="failure-toast",
#     is_open=False,
#     duration=4000,
#     header="Failure",
#     icon="danger",
#     className="mb-3",
#     style={"position": "fixed", "top": 66, "right": 10, "width": 350},
# )

# # Layout
# layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     dcc.Store(id='edit-grant-id'),
#     dcc.Store(id='personnel-store'),
#     dcc.Store(id='personnel-values-store'),
#     dcc.Store(id='domestic-travel-values-store'),
#     dcc.Store(id='international-travel-values-store'),
#     dcc.Store(id='materials-values-store'),
#     dcc.Store(id='hours-store'),
#     html.H3('Edit Grant', className="text-center mt-4 mb-4", style={"color": "#2c3e50"}),
#     html.Div(id='edit-grant-container'),
#     success_toast,
#     failure_toast
# ])

# # Extract grant ID from URL and store
# @callback(
#     Output('edit-grant-id', 'data'),
#     Input('url', 'search'),
#     prevent_initial_call=True
# )
# def extract_grant_id(search):
#     import urllib.parse
#     params = urllib.parse.parse_qs(search.lstrip('?'))
#     grant_id = params.get('edit_id', [None])[0]
#     return grant_id

# # Prefill grant form fields
# @callback(
#     Output({'type': 'grant-input', 'name': 'grant-title'}, 'value'),
#     Output({'type': 'grant-input', 'name': 'funding-agency'}, 'value'),
#     Output({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
#     Output({'type': 'grant-input', 'name': 'grant-status'}, 'value'),
#     Output({'type': 'grant-input', 'name': 'start-date'}, 'date'),
#     Output({'type': 'grant-input', 'name': 'end-date'}, 'date'),
#     Output({'type': 'grant-input', 'name': 'grant-description'}, 'value'),
#     Input('edit-grant-id', 'data'),
#     prevent_initial_call=True
# )
# def prefill_grant_fields(grant_id):
#     if not grant_id:
#         raise PreventUpdate

#     session = get_db_session()
#     try:
#         grant = session.query(Grant).filter_by(id=int(grant_id), user_id=current_user.id).first()
#         if not grant:
#             raise PreventUpdate

#         return (
#             grant.title,
#             grant.funding_agency,
#             grant.duration,
#             grant.status,
#             grant.start_date.isoformat(),
#             grant.end_date.isoformat(),
#             grant.description
#         )
#     finally:
#         session.close()

# # Submit update (instead of create)
# @callback(
#     [Output('success-toast', 'is_open'), Output('failure-toast', 'is_open')],
#     Input('submit-btn', 'n_clicks'),
#     State('edit-grant-id', 'data'),
#     State({'type': 'grant-input', 'name': 'grant-title'}, 'value'),
#     State({'type': 'grant-input', 'name': 'funding-agency'}, 'value'),
#     State({'type': 'grant-input', 'name': 'total-duration'}, 'value'),
#     State({'type': 'grant-input', 'name': 'grant-status'}, 'value'),
#     State({'type': 'grant-input', 'name': 'start-date'}, 'date'),
#     State({'type': 'grant-input', 'name': 'end-date'}, 'date'),
#     State({'type': 'grant-input', 'name': 'grant-description'}, 'value'),
#     State('personnel-values-store', 'data'),
#     State('hours-store', 'data'),
#     State('domestic-travel-values-store', 'data'),
#     State('international-travel-values-store', 'data'),
#     State('materials-values-store', 'data'),
#     prevent_initial_call=True
# )
# def update_existing_grant(n_clicks, grant_id, title, agency, duration, status, start_date, end_date, desc,
#                           personnel_data, hours_data, dom_travel, intl_travel, materials_data):
#     if not grant_id or not title:
#         return False, True

#     session = get_db_session()
#     try:
#         grant = session.query(Grant).filter_by(id=int(grant_id), user_id=current_user.id).first()
#         if not grant:
#             return False, True

#         with session.begin():
#             grant.title = title
#             grant.funding_agency = agency
#             grant.duration = duration
#             grant.status = status
#             grant.start_date = start_date
#             grant.end_date = end_date
#             grant.description = desc

#             session.query(GrantPersonnel).filter_by(grant_id=grant.id).delete()
#             session.query(GrantTravel).filter_by(grant_id=grant.id).delete()
#             session.query(GrantMaterial).filter_by(grant_id=grant.id).delete()

#             start_year = date.fromisoformat(start_date).year
#             for p in personnel_data:
#                 idx, name, pos = p['index'], p['name'], p['position']
#                 for yr_offset in range(int(duration)):
#                     actual_year = start_year + yr_offset
#                     key = f"{idx}-{yr_offset+1}"
#                     hours = hours_data.get(key)
#                     if hours:
#                         session.add(GrantPersonnel(
#                             grant_id=grant.id,
#                             name=name,
#                             position=pos,
#                             year=actual_year,
#                             estimated_hours=hours
#                         ))

#             for t in dom_travel.values():
#                 session.add(GrantTravel(
#                     grant_id=grant.id,
#                     travel_type='Domestic',
#                     name=t['name'],
#                     description=t['desc'],
#                     amount=t['amount'],
#                     year=t['year']
#                 ))
#             for t in intl_travel.values():
#                 session.add(GrantTravel(
#                     grant_id=grant.id,
#                     travel_type='International',
#                     name=t['name'],
#                     description=t['desc'],
#                     amount=t['amount'],
#                     year=t['year']
#                 ))

#             for m in materials_data.values():
#                 subcat = session.query(ExpenseSubcategory).filter_by(name=m['name']).first()
#                 session.add(GrantMaterial(
#                     grant_id=grant.id,
#                     category_id=subcat.category_id if subcat else None,
#                     subcategory_id=subcat.id if subcat else None,
#                     cost=m['cost'],
#                     description=m['desc'],
#                     year=m['year']
#                 ))

#         return True, False

#     except SQLAlchemyError as e:
#         print("Update error:", e)
#         return False, True

#     finally:
#         session.close()
