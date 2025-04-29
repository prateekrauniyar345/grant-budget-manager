import dash
from dash import html, dcc, Input, Output, State, callback, ALL, MATCH, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from models import Grant, User
from db_utils import get_db_session
from flask_login import current_user
import io
import base64
from datetime import datetime
from sqlalchemy import distinct
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from models import Grant, GrantPersonnel, GrantTravel,TravelItinerary, GrantMaterial, ExpenseSubcategory, PI, CoPI, ProfessionalStaff, Postdoc, GRA, Undergrad, TempHelp


# Register the page
dash.register_page(__name__, path='/dashboard')

# Define the layout
def layout():
    return html.Div([
        dcc.Store(id="selected-grant-id"),
        dcc.Location(id="redirect-location", refresh=True),


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




@callback(
    Output("download-excel", "data"),
    Input({'type': 'download-excel-btn', 'index': ALL}, "n_clicks"),
    prevent_initial_call=True
)
def download_excel(n_clicks_list):
    if not any(n_clicks_list):
        raise PreventUpdate

    triggered = ctx.triggered_id
    if not triggered:
        raise PreventUpdate

    try:
        grant_id = triggered['index']
        session = get_db_session()

        if not current_user.is_authenticated:
            raise PreventUpdate

        grant = session.query(Grant).get(grant_id)
        if not grant or grant.user_id != current_user.id:
            raise PreventUpdate

        # Create Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Grant Budget"
        # set the row height
        for i in range(1, 101):
            ws.row_dimensions[i].height = 20
        # Set font size to 12 for all written cells
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:  # Only set font for non-empty cells
                    cell.font = Font(size=12)
                    cell.alignment = Alignment(horizontal='center', vertical='center')

        bold = Font(bold=True)
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        ######################################
        # Section 1: Grant Information
        ######################################
        # Row 1
        ws["A1"] = "Title:"
        ws["A1"].font = bold
        ws["B1"] = grant.title or ""
        ws["J1"] = "PI FTE"
        ws["J1"].font = bold
        ws["J1"].fill = yellow_fill
        ws["K1"] = 0.00
        ws["K1"].fill = yellow_fill

        # Merge B1:I1
        ws.merge_cells('B1:I1')
        # Merge B2:I2
        ws.merge_cells('B2:I2')
        # merge from B3:I3
        ws.merge_cells('B3:I3')

        # Row 2
        ws["A2"] = "Funding source:"
        ws["A2"].font = bold
        ws["B2"] = grant.funding_agency or ""

        # --- Get PI ---
        # There should only be ONE PI normally, so just use a simple query without distinct
        pi_obj = session.query(GrantPersonnel).filter_by(grant_id=grant.id, position="PI").first()
        pi_name = pi_obj.name if pi_obj else "N/A"

        # --- Get unique CoPIs ---
        copi_names = session.query(distinct(GrantPersonnel.name)) \
            .filter_by(grant_id=grant.id, position="Co-PI") \
            .all()

        # Flatten tuple result
        copi_names_list = [name[0] for name in copi_names]
        CoPIs_names = ", ".join(copi_names_list) if copi_names_list else "N/A"

        ws["A3"] = f"PIs: {pi_name}"
        ws["A3"].font = bold
        ws["B3"] = f"CoPIs: {CoPIs_names}"
        ws["B3"].font = bold
        ws["C3"].font = bold

    

        # Row 4
        ws["A4"] = "Project Start and End Dates:"
        ws["A4"].font = bold
        if grant.start_date and grant.end_date:
            ws["B4"] = f"{grant.start_date.strftime('%Y-%m-%d')}  -  {grant.end_date.strftime('%Y-%m-%d')}"

        # Adjust column widths
        ws.column_dimensions["A"].width = 39
        ws.column_dimensions["B"].width = 10
        ws.column_dimensions["C"].width = 15
        ws.column_dimensions["J"].width = 32.5
        for col in range(4, 9):  # D to I
            ws.column_dimensions[chr(64+col)].width = 18



        ######################################
        # Section 2: Personnel Compensation
        ######################################
        ws.column_dimensions['C'].width = 11
        ws.column_dimensions['D'].width = 11
        ws.column_dimensions['E'].width = 11
        ws.column_dimensions['F'].width = 11
        ws.column_dimensions['G'].width = 11
        ws.column_dimensions['H'].width = 11
        ws.column_dimensions['I'].width = 11
        # Define a thin black border
        thin_border = Border(
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        # Apply the border to all cells in Row 5 (C5, D5, E5, etc.)
        for i in range(1, 11):  
            cell = ws.cell(row=5, column=i)
            cell.border = thin_border
        header = ["Hourly rate at Start Date", "Y1", "Y2", "Y3", "Y4", "Y5", "Total", "Notes"]
        ws.row_dimensions[5].height = 32
        # Start writing from column 3 (which is Column C in Excel)
        for i, text in enumerate(header):
            cell = ws.cell(row=5, column=3 + i, value=text)  # 3 = column C
            cell.font = bold
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True )
            

        
        # Save to in-memory stream
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        return dcc.send_bytes(
            output.getvalue(),
            filename=f"grant_{grant_id}_budget.xlsx"
        )

    except Exception as err:
        print(f"Error while downloading Excel: {err}")
        raise PreventUpdate

    finally:
        try:
            session.close()
        except:
            pass



# callack for the editing the grants
@callback(
    Output("selected-grant-id", "data"),
    Input({'type': 'edit-btn', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def store_edit_id(n_clicks_list):
    if not any(n_clicks_list):
        raise PreventUpdate
    triggered_id = ctx.triggered_id
    return triggered_id["index"]

@callback(
    Output("redirect-location", "href"),
    Input("selected-grant-id", "data"),
    prevent_initial_call=True
)
def redirect_to_edit_page(grant_id):
    if grant_id:
        return f"/home/generate-grants?edit_id={grant_id}"
    raise PreventUpdate
