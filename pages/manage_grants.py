import dash
from dash import html, dcc, Input, Output, State, callback
import dash_table
import pandas as pd
from sqlalchemy import func, distinct
from db_utils import get_db_session
from models import (
    Grant, GrantPersonnel, GrantTravel, TravelItinerary, GrantMaterial,
    PI, CoPI, NSFPersonnelCompensation, NIHPersonnelCompensation,
    ProfessionalStaff, Postdoc, GRA, Undergrad, TempHelp,
    NSFFringeRate, NIHFringeRate,
    ExpenseSubcategory
)

dash.register_page(__name__, path="/subawards")

def layout():
    return html.Div([
        html.H1("Subawards Totals", className="my-4"),
        html.Div([
            dcc.Input(id="grant-id-input", type="number",
                      placeholder="Enter Grant ID",
                      style={"width":"200px","marginRight":"8px"}),
            html.Button("Load Totals", id="load-totals-btn", n_clicks=0)
        ]),
        html.Div(id="totals-container", style={"marginTop":"2rem"})
    ], className="container")


@callback(
    Output("totals-container", "children"),
    Input("load-totals-btn", "n_clicks"),
    State("grant-id-input", "value"),
    prevent_initial_call=True
)
def load_totals(n_clicks, grant_id):
    if not grant_id:
        return html.Div("⚠️ Please enter a Grant ID.", style={"color":"red"})

    session = get_db_session()
    grant = session.query(Grant).get(grant_id)
    if not grant:
        session.close()
        return html.Div(f"⚠️ Grant ID {grant_id} not found.", style={"color":"red"})

    # --- SETUP ---
    start_year = grant.start_date.year
    n_years    = grant.duration
    year_cols  = [f"Y{i+1}" for i in range(n_years)]
    all_cols   = year_cols + ["Total"]

    # running total per column
    totals = {col: 0.0 for col in all_cols}

    # track raw personnel‐compensation by (fringe_category, year_idx)
    pers_by_cat = {}

    # ----- 1) PERSONNEL COMPENSATION -----
    # map position → ORM class for base‐rate lookup
    pos_model = {
        "PI": PI,
        "Co-PI": CoPI,
        "UI Professional Staff": ProfessionalStaff,
        "Postdoc": Postdoc,
        "GRA": GRA,
        "Undergrad": Undergrad,
        "Temp Help": TempHelp
    }
    # choose which compensation‐increase table
    CompTbl = (
        NSFPersonnelCompensation
        if "nsf" in grant.funding_agency.lower()
        else NIHPersonnelCompensation
    )
    # fringe‐category mapping
    fringe_cat = {
        "PI":    "Faculty",
        "Co-PI": "Faculty",
        "UI Professional Staff": "UI professional staff & Post Docs",
        "Postdoc": "UI professional staff & Post Docs",
        "GRA":    "GRAs/UGrads",
        "Undergrad": "GRAs/UGrads",
        "Temp Help": "Temp Help"
    }
    # fetch each distinct person+position
    people = session.query(
        GrantPersonnel.name,
        GrantPersonnel.position
    ).filter_by(grant_id=grant_id).distinct().all()

    for name, pos in people:
        # 1a) base rate
        raw_base = session.query(pos_model[pos].expected_hourly_salary) \
                          .filter_by(full_name=name).scalar()
        base_rate = float(raw_base or 0.0)

        # 1b) raise‐schedule row
        comp_row = session.query(CompTbl) \
                          .filter(CompTbl.role.ilike(pos)).first()
        current_rate = base_rate

        # 1c) loop each project year
        for i in range(n_years):
            year = start_year + i
            hrs = session.query(
                func.coalesce(func.sum(GrantPersonnel.estimated_hours), 0)
            ).filter_by(
                grant_id=grant_id,
                name=name,
                position=pos,
                year=year
            ).scalar()
            hrs = float(hrs or 0.0)
            if hrs <= 0 or base_rate <= 0:
                continue

            # apply raise from Year‐2 on
            if i > 0 and comp_row:
                raw_inc = getattr(comp_row, f"y{i+1}_rate_increase", 0) or 0
                inc     = float(raw_inc)
                current_rate *= (1.0 + inc)

            cost = hrs * current_rate
            totals[year_cols[i]] += cost

            # bucket for fringe
            cat_key = fringe_cat[pos]
            pers_by_cat.setdefault((cat_key, i), 0.0)
            pers_by_cat[(cat_key, i)] += cost

    # ----- 2) FRINGE on PERSONNEL only -----
    FringeTbl = (
        NSFFringeRate
        if "nsf" in grant.funding_agency.lower()
        else NIHFringeRate
    )
    for (cat_key, i), pcost in pers_by_cat.items():
        raw_rate = session.query(FringeTbl.fringe_rate) \
                          .filter_by(role=cat_key, year=i+1).scalar()
        rate     = float(raw_rate or 0.0)
        fringe_amt = pcost * (rate/100.0)
        totals[year_cols[i]] += fringe_amt

    # ----- 3) TRAVEL -----
    for tr in session.query(GrantTravel).filter_by(grant_id=grant_id):
        itin    = tr.itinerary
        flight  = float(itin.flight_cost or 0)
        days    = int(itin.days_stay or 0)
        per_day = float(itin.per_day_food_lodging or 0) \
                + float(itin.per_day_transportation or 0)
        cost    = flight + days*per_day
        offs    = tr.year - start_year
        if 0 <= offs < n_years:
            totals[year_cols[offs]] += cost

    # ----- 4) EQUIPMENT >$5000 -----
    eqs = session.query(GrantMaterial) \
        .join(ExpenseSubcategory,
              GrantMaterial.subcategory_id == ExpenseSubcategory.id) \
        .filter(
            GrantMaterial.grant_id == grant_id,
            ExpenseSubcategory.name == "Equipment >5K"
        ).all()
    for gm in eqs:
        cost = float(gm.cost or 0)
        offs = (gm.year or start_year) - start_year
        if 0 <= offs < n_years:
            totals[year_cols[offs]] += cost

    # ----- 5) OTHER DIRECT COSTS (cat_id=4 minus >5K) -----
    other_ids = [r[0] for r in session.query(ExpenseSubcategory.id)
                 .filter(
                     ExpenseSubcategory.category_id==4,
                     ExpenseSubcategory.name!="Equipment >5K"
                 ).all()]
    others = session.query(GrantMaterial) \
        .filter(
            GrantMaterial.grant_id==grant_id,
            GrantMaterial.subcategory_id.in_(other_ids)
        ).all()
    for gm in others:
        cost = float(gm.cost or 0)
        offs = (gm.year or start_year) - start_year
        if 0 <= offs < n_years:
            totals[year_cols[offs]] += cost

    # ----- 6) PARTICIPANT SUPPORT COSTS (NSF only) -----
    ps = session.query(GrantMaterial) \
        .join(ExpenseSubcategory,
              GrantMaterial.subcategory_id == ExpenseSubcategory.id) \
        .filter(
            GrantMaterial.grant_id==grant_id,
            ExpenseSubcategory.name.ilike("%Participant Support%")
        ).all()
    for gm in ps:
        cost = float(gm.cost or 0)
        offs = (gm.year or start_year) - start_year
        if 0 <= offs < n_years:
            totals[year_cols[offs]] += cost

    session.close()

    # ----- 7) GRAND TOTAL -----
    totals["Total"] = sum(totals[c] for c in year_cols)

    # build column list including Grant ID and Grant Name
    year_cols = [f"Y{i+1}" for i in range(n_years)]
    all_cols  = ["Grant ID", "Grant Name"] + year_cols + ["Total"]

    # build a single‐row dict
    row_dict = {
        "Grant ID":   grant_id,
        "Grant Name": grant.title or ""
    }
    # add all the Y1…Yn and Total values
    for c in year_cols + ["Total"]:
        row_dict[c] = round(totals[c], 2)

    # make DataFrame
    df = pd.DataFrame([row_dict], columns=all_cols)

    # render
    table = dash_table.DataTable(
        data=df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in all_cols],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "center"},
    )

    return html.Div([
        html.H4(f"Aggregated Totals for Grant {grant_id}", className="my-2"),
        table
    ])
