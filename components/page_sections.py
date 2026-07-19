"""Professional dashboard page renderers for QREI."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from components.charts import (
    allocation_chart,
    cashflow_chart,
    donut_chart,
    gauge_chart,
    metric_bar_chart,
    price_chart,
    radar_chart,
    scatter_value_chart,
)
from components.forms import coordinate_editor, import_panel, parcel_actions
from components.maps import render_parcel_map
from components.metrics import kpi_grid, metric_card, warning_from_payload
from qrei.geometry import to_geojson
from services.api_client import QREIClient
from utils.session import add_history, set_points


def render_home(client: QREIClient) -> None:
    """Render executive dashboard."""

    points = st.session_state.parcel_points
    geometry = client.geometry(points)
    construction = client.construction(
        {
            "land_area": geometry["area"],
            "total_floor_area": geometry["area"] * st.session_state.get("dashboard_far", 2.2),
            "footprint_area": geometry["area"] * 0.45,
            "allowed_far": st.session_state.get("dashboard_allowed_far", 2.5),
        }
    )
    valuation = client.valuation(
        {
            "land_area": geometry["area"],
            "building_area": geometry["area"] * 1.7,
            "road_frontage_m": st.session_state.get("dashboard_frontage", 18.0),
            "infrastructure_score": 0.78,
        }
    )
    finance = client.finance(
        {
            "property_value": valuation["estimated_value"],
            "annual_rent": valuation["estimated_value"] * 0.052,
        }
    )
    market = client.market({})

    kpi_grid(
        [
            ("Total Area", f"{geometry['area']:,.2f}", "active parcel"),
            ("Perimeter", f"{geometry['perimeter']:,.2f}", geometry["orientation"]),
            ("Estimated Value", _money(valuation["estimated_value"]), f"{valuation['confidence']:.0%} confidence"),
            ("Investment Score", f"{market['investment_score']:.1f}", "market + finance"),
            ("Road Frontage", f"{st.session_state.get('dashboard_frontage', 18.0):.1f} m", "valuation input"),
            ("Buildable Area", f"{construction['buildable_area']:,.2f}", "planning envelope"),
            ("FAR", f"{construction['far']:.2f}", "current scheme"),
            ("FSI", f"{construction['fsi']:.2f}", "current scheme"),
            ("Construction Cost", _money(construction["construction_cost"]), "estimated"),
            ("Expected ROI", f"{finance['roi']:.1%}", "cash model"),
        ],
        columns=5,
    )
    warning_from_payload(geometry)

    tabs = st.tabs(["Overview", "Parcel", "Portfolio"])
    with tabs[0]:
        left, right = st.columns([1.1, 0.9])
        with left:
            st.subheader("Market Movement")
            st.plotly_chart(price_chart(market.get("prices", [])), use_container_width=True)
        with right:
            st.subheader("Asset Quality")
            st.plotly_chart(
                radar_chart(
                    {
                        "Value": min(100.0, valuation["estimated_value"] / max(geometry["area"], 1.0) / 20.0),
                        "Access": 78.0,
                        "Buildability": min(100.0, construction["far"] * 28.0),
                        "Confidence": valuation["confidence"] * 100.0,
                        "Yield": min(100.0, finance["rental_yield"] * 1000.0),
                    }
                ),
                use_container_width=True,
            )
    with tabs[1]:
        left, right = st.columns([1.35, 0.65])
        with left:
            render_parcel_map(points, height=460, draw=False, tile_mode="Hybrid")
        with right:
            st.subheader("Parcel Controls")
            st.session_state.dashboard_frontage = st.slider("Road frontage m", 0.0, 80.0, 18.0)
            st.session_state.dashboard_far = st.slider("Modeled FAR", 0.1, 8.0, 2.2)
            st.session_state.dashboard_allowed_far = st.slider("Allowed FAR", 0.1, 8.0, 2.5)
            st.json(geometry["bounding_box"])
    with tabs[2]:
        st.subheader("Portfolio Snapshot")
        portfolio = pd.DataFrame(
            {
                "asset": ["Active Parcel", "Comparable A", "Comparable B", "Comparable C"],
                "land_area": [geometry["area"], 120.0, 145.0, 210.0],
                "value": [valuation["estimated_value"], 120000.0, 185000.0, 240000.0],
            }
        )
        st.plotly_chart(scatter_value_chart(portfolio, "land_area", "value", "value", "Comparable Positioning"), use_container_width=True)
        st.dataframe(portfolio, use_container_width=True, hide_index=True)


def render_geometry(client: QREIClient) -> None:
    """Render geometry engine page."""

    left, right = st.columns([1.35, 0.65])
    with right:
        st.subheader("Drawing Toolkit")
        tile = st.selectbox("Map layer", ["Street", "Satellite", "Terrain", "Hybrid"])
        show_grid = st.toggle("Grid overlay", value=True)
        snap = st.number_input("Coordinate precision", min_value=0, max_value=8, value=6)
        search = st.text_input("Move parcel center to", placeholder="72.8777, 19.0760")
        if st.button("Apply center", use_container_width=True) and search:
            _move_parcel_to(search)
        st.divider()
        edited = coordinate_editor(st.session_state.parcel_points)
        if st.button("Apply coordinate table", use_container_width=True):
            set_points([(round(x, snap), round(y, snap)) for x, y in edited])
            st.rerun()
        parcel_actions()
        import_panel()

    with left:
        map_data = render_parcel_map(
            st.session_state.parcel_points,
            height=610,
            draw=True,
            show_grid=show_grid,
            tile_mode=tile,
        )
        clicked = (map_data or {}).get("last_clicked")
        if clicked:
            c1, c2 = st.columns([0.7, 0.3])
            c1.caption(f"Last map click: {clicked['lng']:.6f}, {clicked['lat']:.6f}")
            if c2.button("Add point", use_container_width=True):
                st.session_state.parcel_points.append((round(clicked["lng"], snap), round(clicked["lat"], snap)))
                add_history("Point added from map")
                st.rerun()

    geometry = client.geometry(st.session_state.parcel_points)
    warning_from_payload(geometry)
    kpi_grid(
        [
            ("Shoelace Area", f"{geometry['shoelace']:,.6f}", None),
            ("Area", f"{geometry['area']:,.6f}", None),
            ("Perimeter", f"{geometry['perimeter']:,.6f}", None),
            ("Centroid", _pair(geometry["centroid"]), None),
            ("Orientation", geometry["orientation"], None),
            ("Validation", "Valid" if geometry["is_valid"] else "Check", None),
        ],
        columns=3,
    )
    t1, t2, t3 = st.tabs(["Edges", "Bounding Box", "Exports"])
    with t1:
        st.dataframe(
            pd.DataFrame(
                {
                    "edge": [f"E{idx + 1}" for idx in range(len(geometry["edge_lengths"]))],
                    "length": geometry["edge_lengths"],
                    "internal_angle": geometry["internal_angles"],
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    with t2:
        cols = st.columns(2)
        with cols[0]:
            st.json(geometry["bounding_box"])
        with cols[1]:
            st.plotly_chart(
                metric_bar_chart(
                    {
                        "Vertices": len(st.session_state.parcel_points),
                        "Hull Vertices": len(geometry["convex_hull"]),
                        "Self Intersections": len(geometry["self_intersections"]),
                    },
                    "Validation Diagnostics",
                ),
                use_container_width=True,
            )
    with t3:
        st.download_button(
            "Export GeoJSON",
            json.dumps(to_geojson(st.session_state.parcel_points), indent=2),
            "qrei_parcel.geojson",
            "application/geo+json",
        )
        st.download_button(
            "Export Coordinates CSV",
            pd.DataFrame(st.session_state.parcel_points, columns=["x", "y"]).to_csv(index=False),
            "qrei_coordinates.csv",
            "text/csv",
        )


def render_gis(client: QREIClient) -> None:
    """Render GIS explorer page."""

    left, right = st.columns([1.35, 0.65])
    with left:
        tile = st.selectbox("Base map", ["Street", "Satellite", "Terrain", "Hybrid"])
        render_parcel_map(
            st.session_state.parcel_points,
            height=610,
            draw=False,
            show_grid=st.toggle("Grid overlay", value=False),
            tile_mode=tile,
        )
    with right:
        st.subheader("Layer Manager")
        layers = {
            "Road network": st.checkbox("Road network", value=True),
            "Water bodies": st.checkbox("Water bodies"),
            "Utility lines": st.checkbox("Utility lines", value=True),
            "Zoning maps": st.checkbox("Zoning maps", value=True),
            "Flood zones": st.checkbox("Flood zones"),
            "Land use": st.checkbox("Land use", value=True),
        }
        import_panel()
        geometry = client.geometry(st.session_state.parcel_points)
        active_layers = [name for name, enabled in layers.items() if enabled]
        st.metric("Active Layers", len(active_layers))
        st.metric("Spatial Index Candidates", len(active_layers) * max(len(st.session_state.parcel_points), 1))
        st.json({"bbox": geometry["bounding_box"], "centroid": geometry["centroid"], "layers": active_layers})
    st.subheader("GIS Readiness")
    st.plotly_chart(
        radar_chart({"Roads": 78, "Utilities": 72, "Zoning": 84, "Flood Safety": 81, "Land Use": 88}),
        use_container_width=True,
    )


def render_survey(client: QREIClient) -> None:
    """Render survey tools page."""

    survey = client.survey(st.session_state.parcel_points)
    warning_from_payload(survey)
    kpi_grid(
        [(key.replace("_", " ").title(), f"{value:,.3f}", None) for key, value in survey["dimensions"].items()],
        columns=4,
    )
    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Boundary Report")
        boundary = pd.DataFrame(survey["boundary"])
        st.dataframe(boundary, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Survey Diagram")
        render_parcel_map(st.session_state.parcel_points, height=390, draw=False, show_grid=True, tile_mode="Street")
    st.subheader("Legal Description")
    st.info(survey["legal_description"])
    st.download_button("Download Survey JSON", json.dumps(survey, indent=2), "survey_report.json", "application/json")


def render_construction(client: QREIClient) -> None:
    """Render construction analytics page."""

    area = client.geometry(st.session_state.parcel_points)["area"]
    left, right = st.columns([0.72, 1.28])
    with left:
        st.subheader("Development Inputs")
        with st.form("construction_form"):
            footprint = st.number_input("Building footprint", value=float(max(area * 0.45, 1.0)), min_value=0.0)
            floors = st.number_input("Floors", value=5, min_value=1)
            allowed_far = st.number_input("Allowed FAR", value=2.5, min_value=0.0)
            height = st.number_input("Height m", value=16.0, min_value=0.0)
            cost = st.number_input("Cost per sqm", value=1500.0, min_value=0.0)
            submitted = st.form_submit_button("Analyze Construction")
    payload = {
        "land_area": area,
        "total_floor_area": footprint * floors,
        "footprint_area": footprint,
        "allowed_far": allowed_far,
        "height_m": height,
        "cost_per_sqm": cost,
    }
    result = client.construction(payload)
    if submitted:
        add_history("Construction analysis", payload)
    with right:
        kpi_grid(
            [
                ("Ground Coverage", f"{result['ground_coverage']:.1%}", None),
                ("Buildable Area", f"{result['buildable_area']:,.2f}", None),
                ("FAR", f"{result['far']:.2f}", None),
                ("FSI", f"{result['fsi']:.2f}", None),
                ("Parking", result["parking_spaces"], "spaces"),
                ("Volume", f"{result['construction_volume']:,.2f}", "cubic m"),
                ("Cost", _money(result["construction_cost"]), None),
            ],
            columns=4,
        )
        st.plotly_chart(
            donut_chart(
                {
                    "Concrete": result["materials"]["concrete_cubic_m"],
                    "Steel": result["materials"]["steel_kg"] / 100.0,
                    "Bricks": result["materials"]["bricks"] / 1000.0,
                },
                "Material Mix",
            ),
            use_container_width=True,
        )
    st.subheader("Material Quantities")
    st.dataframe(pd.DataFrame([result["materials"]]), use_container_width=True, hide_index=True)


def render_valuation(client: QREIClient) -> None:
    """Render property valuation page."""

    area = client.geometry(st.session_state.parcel_points)["area"]
    left, right = st.columns([0.72, 1.28])
    with left:
        st.subheader("Valuation Inputs")
        with st.form("valuation_form"):
            road = st.number_input("Road frontage m", value=18.0, min_value=0.0)
            building = st.number_input("Building area", value=float(max(area * 1.7, 1.0)), min_value=0.0)
            infra = st.slider("Infrastructure score", 0.0, 1.0, 0.78)
            corner = st.checkbox("Corner plot")
            submitted = st.form_submit_button("Run Valuation")
    result = client.valuation(
        {
            "land_area": area,
            "building_area": building,
            "road_frontage_m": road,
            "infrastructure_score": infra,
            "corner_plot": corner,
        }
    )
    if submitted:
        add_history("Valuation generated", result)
    with right:
        kpi_grid(
            [
                ("Estimated Value", _money(result["estimated_value"]), None),
                ("Confidence", f"{result['confidence']:.0%}", None),
                ("Price / Unit", _money(result["price_per_sqm"]), None),
                ("Neighborhood", f"{result['neighborhood_score']:.0f}", None),
                ("Commercial", f"{result['commercial_score']:.0f}", None),
                ("Residential", f"{result['residential_score']:.0f}", None),
            ],
            columns=3,
        )
    st.plotly_chart(
        radar_chart(
            {
                "Neighborhood": result["neighborhood_score"],
                "Commercial": result["commercial_score"],
                "Residential": result["residential_score"],
                "Confidence": result["confidence"] * 100.0,
            }
        ),
        use_container_width=True,
    )
    comparables = pd.DataFrame(
        {
            "asset": ["Comparable A", "Comparable B", "Comparable C", "Subject"],
            "land_area": [100.0, 145.0, 210.0, area],
            "value": [120000.0, 185000.0, 240000.0, result["estimated_value"]],
        }
    )
    st.plotly_chart(scatter_value_chart(comparables, "land_area", "value", "value", "Comparable Sales"), use_container_width=True)
    st.download_button("Download Valuation Report", json.dumps(result, indent=2), "valuation_report.json", "application/json")


def render_finance(client: QREIClient) -> None:
    """Render finance calculators page."""

    with st.form("finance_form"):
        col1, col2, col3 = st.columns(3)
        value = col1.number_input("Property value", value=250000.0, min_value=0.0)
        rent = col2.number_input("Annual rent", value=15000.0, min_value=0.0)
        rate = col3.number_input("Discount rate", value=0.1, min_value=0.0, max_value=1.0)
        loan = col1.number_input("Loan amount", value=175000.0, min_value=0.0)
        annual_rate = col2.number_input("Annual loan rate", value=0.09, min_value=0.0, max_value=1.0)
        months = col3.number_input("Loan months", value=240, min_value=1)
        flows = st.text_input("Cash flows", "-50000,9000,11000,13000,15000")
        submitted = st.form_submit_button("Calculate Finance")
    cash_flows = _parse_numbers(flows)
    result = client.finance(
        {
            "property_value": value,
            "annual_rent": rent,
            "discount_rate": rate,
            "cash_flows": cash_flows,
            "loan_amount": loan,
            "annual_rate": annual_rate,
            "months": months,
        }
    )
    if submitted:
        add_history("Finance calculated", result)
    kpi_grid(
        [
            ("ROI", f"{result['roi']:.1%}", None),
            ("NPV", _money(result["npv"]), None),
            ("EMI", _money(result["emi"]), "monthly"),
            ("Rental Yield", f"{result['rental_yield']:.1%}", None),
            ("Cap Rate", f"{result['cap_rate']:.1%}", None),
        ],
        columns=5,
    )
    left, right = st.columns([1.2, 0.8])
    with left:
        st.plotly_chart(cashflow_chart(cash_flows), use_container_width=True)
    with right:
        st.plotly_chart(
            donut_chart({"Equity": max(value - loan, 0.0), "Debt": loan}, "Capital Stack"),
            use_container_width=True,
        )


def render_traffic(client: QREIClient) -> None:
    """Render traffic analytics page."""

    with st.form("traffic_form"):
        c1, c2, c3, c4 = st.columns(4)
        payload = {
            "travel_time_min": c1.slider("Travel time", 0.0, 120.0, 24.0),
            "walkability": c2.slider("Walkability", 0.0, 1.0, 0.72),
            "transit_score": c3.slider("Transit", 0.0, 1.0, 0.68),
            "congestion_index": c4.slider("Congestion", 0.0, 1.0, 0.34),
        }
        st.form_submit_button("Update Accessibility")
    result = client.traffic(payload)
    kpi_grid(
        [
            ("Accessibility", f"{result['accessibility_score']:.1f}", None),
            ("Public Transport", f"{result['public_transport_score']:.1f}", None),
            ("Hospital Access", "74", "score"),
            ("School Access", "81", "score"),
            ("Airport Access", "63", "score"),
            ("Metro Access", "69", "score"),
        ],
        columns=3,
    )
    left, right = st.columns([1.25, 0.75])
    with left:
        render_parcel_map(st.session_state.parcel_points, height=460, draw=False, show_grid=False, tile_mode="Street")
    with right:
        st.plotly_chart(gauge_chart(result["accessibility_score"], "Accessibility"), use_container_width=True)


def render_urban(client: QREIClient) -> None:
    """Render urban analytics page."""

    with st.expander("Urban model inputs", expanded=False):
        c1, c2, c3 = st.columns(3)
        payload = {
            "green_space_score": c1.slider("Green space", 0.0, 1.0, 0.66),
            "air_quality_score": c2.slider("Air quality", 0.0, 1.0, 0.70),
            "noise_score": c3.slider("Noise quality", 0.0, 1.0, 0.61),
            "transit_score": c1.slider("Transit coverage", 0.0, 1.0, 0.72),
            "flood_risk": c2.slider("Flood risk", 0.0, 1.0, 0.16),
            "heat_island_risk": c3.slider("Heat island risk", 0.0, 1.0, 0.22),
        }
    result = client.urban(payload)
    kpi_grid(
        [
            ("Livability", f"{result['livability_score']:.1f}", None),
            ("Growth Rate", f"{result['city_growth_rate']:.1%}", "annual"),
            ("Population Density", f"{result['population_density']:.0f}", None),
            ("Flood Safety", f"{result['flood_safety']:.0f}", None),
            ("Air Quality", f"{result['air_quality']:.0f}", None),
            ("Infrastructure", f"{result['infrastructure_score']:.0f}", None),
        ],
        columns=3,
    )
    left, right = st.columns([0.9, 1.1])
    with left:
        st.plotly_chart(gauge_chart(result["livability_score"], "Livability"), use_container_width=True)
    with right:
        st.plotly_chart(
            radar_chart(
                {
                    "Population": result["population_density"],
                    "Green Space": result["green_space_score"],
                    "Flood Safety": result["flood_safety"],
                    "Noise": result["noise_quality"],
                    "Air": result["air_quality"],
                    "Infrastructure": result["infrastructure_score"],
                }
            ),
            use_container_width=True,
        )
    render_parcel_map(st.session_state.parcel_points, height=360, draw=False, tile_mode="Hybrid")


def render_market(client: QREIClient) -> None:
    """Render market intelligence page."""

    prices_text = st.text_input("Historical prices", "100,108,119,131,145,158")
    prices = _parse_numbers(prices_text)
    result = client.market({"prices": prices})
    kpi_grid(
        [
            ("Price Trend", f"{result['price_trend']:.2f}", "per period"),
            ("Investment Score", f"{result['investment_score']:.1f}", None),
            ("Demand", "High", "model input"),
            ("Supply", "Moderate", "model input"),
            ("Vacancy", "6.0%", "market input"),
        ],
        columns=5,
    )
    left, right = st.columns([1.25, 0.75])
    with left:
        st.plotly_chart(price_chart(result["prices"]), use_container_width=True)
    with right:
        st.plotly_chart(
            metric_bar_chart({"Residential": 86, "Commercial": 73, "Industrial": 58, "Rental": 79}, "Segment Strength"),
            use_container_width=True,
        )


def render_prediction(client: QREIClient) -> None:
    """Render AI prediction page."""

    with st.form("prediction_form"):
        c1, c2, c3 = st.columns(3)
        land_area = c1.number_input("Land area", value=120.0, min_value=0.0)
        frontage = c2.number_input("Road frontage m", value=14.0, min_value=0.0)
        infra = c3.slider("Infrastructure score", 0.0, 1.0, 0.74)
        submitted = st.form_submit_button("Run Prediction")
    result = client.predict(
        {
            "land_area": land_area,
            "road_frontage_m": frontage,
            "infrastructure_score": infra,
        }
    )
    if submitted:
        add_history("Prediction generated", result)
    kpi_grid(
        [
            ("Predicted Value", _money(result["predicted_value"]), None),
            ("Rental Prediction", _money(result["rental_prediction"]), None),
            ("Investment Grade", result["investment_grade"], None),
            ("Risk Score", f"{result['risk_score']:.2f}", None),
            ("Confidence", f"{result['confidence']:.0%}", None),
        ],
        columns=5,
    )
    left, right = st.columns([0.85, 1.15])
    with left:
        st.plotly_chart(gauge_chart(result["confidence"] * 100.0, "Model Confidence"), use_container_width=True)
    with right:
        st.subheader("Recommendation")
        st.info(result["construction_recommendation"])
        st.plotly_chart(
            radar_chart(
                {
                    "Value": min(100.0, result["predicted_value"] / max(land_area, 1.0) / 15.0),
                    "Rent": min(100.0, result["rental_prediction"] / max(result["predicted_value"], 1.0) * 1400.0),
                    "Confidence": result["confidence"] * 100.0,
                    "Risk Control": (1.0 - result["risk_score"]) * 100.0,
                }
            ),
            use_container_width=True,
        )


def render_optimization(client: QREIClient) -> None:
    """Render optimization page."""

    with st.form("optimization_form"):
        budget = st.number_input("Investment budget", value=100000.0, min_value=0.0)
        returns = st.text_input("Expected returns", "0.08,0.11,0.14")
        risks = st.text_input("Risk scores", "0.22,0.34,0.50")
        submitted = st.form_submit_button("Optimize Allocation")
    result = client.optimize(
        {
            "budget": budget,
            "expected_returns": _parse_numbers(returns),
            "risk_scores": _parse_numbers(risks),
        }
    )
    labels = [f"Option {idx + 1}" for idx in range(len(result["allocation"]))]
    if submitted:
        add_history("Optimization generated", result)
    kpi_grid([(label, _money(value), None) for label, value in zip(labels, result["allocation"])], columns=3)
    left, right = st.columns([1.1, 0.9])
    with left:
        st.plotly_chart(allocation_chart(labels, result["allocation"]), use_container_width=True)
    with right:
        render_parcel_map(st.session_state.parcel_points, height=360, draw=False, show_grid=True, tile_mode="Street")


def render_reports(client: QREIClient) -> None:
    """Render reports and exports page."""

    geometry = client.geometry(st.session_state.parcel_points)
    survey = client.survey(st.session_state.parcel_points)
    report = client.report(
        {
            "title": "QREI Parcel Intelligence Report",
            "sections": {
                "geometry": geometry,
                "survey": survey,
                "history": st.session_state.history,
            },
        }
    )
    left, right = st.columns([0.8, 1.2])
    with left:
        metric_card("Report Sections", "3", "geometry, survey, history")
        metric_card("Vertices", str(len(st.session_state.parcel_points)), "active parcel")
        metric_card("Backend", "API" if client.use_api else "Local", "render source")
    with right:
        st.subheader("Report Preview")
        st.json(report)
    st.download_button("Download JSON", json.dumps(report, indent=2), "qrei_report.json", "application/json")
    st.download_button(
        "Download GeoJSON",
        json.dumps(to_geojson(st.session_state.parcel_points), indent=2),
        "qrei_parcel.geojson",
        "application/geo+json",
    )
    st.download_button(
        "Download CSV",
        pd.DataFrame(st.session_state.parcel_points, columns=["x", "y"]).to_csv(index=False),
        "qrei_coordinates.csv",
        "text/csv",
    )


def render_settings(client: QREIClient) -> None:
    """Render settings and session management page."""

    left, right = st.columns([0.85, 1.15])
    with left:
        st.subheader("Workspace")
        project_name = st.text_input("Project name", st.session_state.get("project_name", "Active parcel"))
        st.session_state.project_name = project_name
        autosave = st.toggle("Autosave session", value=st.session_state.get("autosave", True))
        st.session_state.autosave = autosave
        if st.button("Bookmark parcel", use_container_width=True):
            st.session_state.bookmarks.append({"name": project_name, "points": st.session_state.parcel_points})
            add_history("Bookmark saved", {"name": project_name})
            st.success("Bookmark saved.")
    with right:
        st.subheader("Session History")
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True, hide_index=True)
    st.subheader("Bookmarks")
    st.json(st.session_state.bookmarks)


def _move_parcel_to(value: str) -> None:
    try:
        lon, lat = [float(item.strip()) for item in value.split(",")[:2]]
        points = st.session_state.parcel_points
        center_x = sum(x for x, _ in points) / len(points)
        center_y = sum(y for _, y in points) / len(points)
        set_points([(x + lon - center_x, y + lat - center_y) for x, y in points])
        st.rerun()
    except Exception as exc:
        st.error(f"Location update failed: {exc}")


def _parse_numbers(value: str) -> list[float]:
    try:
        return [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError:
        st.warning("Invalid number list. Using an empty series.")
        return []


def _money(value: float) -> str:
    return f"${value:,.0f}"


def _pair(value: Any) -> str:
    return f"{float(value[0]):.6f}, {float(value[1]):.6f}"
