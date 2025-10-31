import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def plot_results(results: pd.DataFrame):
    """
    Improved bar chart: stacked repairs per shop by day (when shop info present).
    If `shop` column is missing, fall back to a simple daily repairs bar chart.
    """
    if results is None or results.empty:
        return px.scatter(title="No repairs occurred.")

    if "shop" in results.columns:
        df = results.groupby(["day", "shop"]).size().reset_index(name="repairs")
        # stacked bar by shop to show distribution across shops per day
        fig = px.bar(df, x="day", y="repairs", color="shop",
                     title="Repairs Completed Over Time (stacked by shop)",
                     labels={"repairs": "Repairs", "day": "Day"},
                     category_orders={"day": sorted(df["day"].unique())})
        fig.update_layout(barmode="stack", xaxis=dict(type="category"))
        return fig
    else:
        df = results.groupby("day").size().reset_index(name="repairs")
        fig = px.bar(df, x="day", y="repairs", title="Repairs Completed Over Time")
        return fig


def plot_map(theater_data: dict, allocation: pd.DataFrame, sample_lines: Optional[int] = 200):
    """
    Create a simple map showing units and shops and the assignment links.

    - `theater_data` should contain `units` and `shops` DataFrames with `lat` and `lon`.
    - `allocation` is a DataFrame with columns `unit_id` and `assigned_shop`.

    Returns a Plotly Figure (mapbox with open-street-map style).
    """
    units = theater_data.get("units")
    shops = theater_data.get("shops")

    # Basic validation
    if units is None or shops is None or units.empty or shops.empty:
        return px.scatter_mapbox(title="No geographic data available.")

    # Prepare traces
    fig = go.Figure()

    # Shops as larger markers
    fig.add_trace(go.Scattermapbox(
        lat=shops["lat"], lon=shops["lon"], mode="markers+text",
        marker=dict(size=12, color="red"), text=shops["shop_id"], textposition="top right",
        name="Shops"
    ))

    # Units as smaller markers
    fig.add_trace(go.Scattermapbox(
        lat=units["lat"], lon=units["lon"], mode="markers+text",
        marker=dict(size=8, color="blue"), text=units["unit_id"], textposition="bottom right",
        name="Units"
    ))

    # Draw lines from unit -> assigned shop (sample if too many)
    if allocation is not None and not allocation.empty:
        # merge units with allocation and shops to get coordinates
        merged = allocation.merge(units, left_on="unit_id", right_on="unit_id", how="left")
        merged = merged.merge(shops.add_prefix("shop_"), left_on="assigned_shop", right_on="shop_shop_id", how="left")

        # Limit the number of lines drawn for performance
        if len(merged) > sample_lines:
            merged = merged.sample(sample_lines, random_state=1)

        for _, row in merged.iterrows():
            if pd.isna(row.get("lat")) or pd.isna(row.get("lon")) or pd.isna(row.get("shop_lat")) or pd.isna(row.get("shop_lon")):
                continue
            fig.add_trace(go.Scattermapbox(
                lat=[row["lat"], row["shop_lat"]], lon=[row["lon"], row["shop_lon"]],
                mode="lines", line=dict(width=1, color="gray"), hoverinfo="none", showlegend=False
            ))

    # Center map roughly at mean location
    center_lat = float(pd.concat([units["lat"], shops["lat"]]).mean())
    center_lon = float(pd.concat([units["lon"], shops["lon"]]).mean())

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=center_lat, lon=center_lon), zoom=7),
        margin={"l":0,"r":0,"t":30,"b":0},
        title="Units, Shops, and Assigned Repair Routes"
    )

    return fig


def _compute_daily_shop_metrics(results: pd.DataFrame, max_days: Optional[int] = None) -> pd.DataFrame:
    """
    From simulation `results` (with start_day and end_day), compute per-day per-shop
    metrics:
      - under_maintenance: number of vehicles under maintenance that day (start_day <= d < end_day)
      - completed: number of repairs completed on that day (end_day == d)

    Returns DataFrame with columns: day, shop, under_maintenance, completed
    """
    if results is None or results.empty:
        return pd.DataFrame(columns=["day", "shop", "under_maintenance", "completed"]) 

    # determine day range
    max_day = int(results["end_day"].max()) if max_days is None else int(max_days)
    shops = results["shop"].unique()

    rows = []
    for d in range(0, max_day + 1):
        for s in shops:
            under = int(((results["shop"] == s) & (results["start_day"] <= d) & (results["end_day"] > d)).sum())
            completed = int(((results["shop"] == s) & (results["end_day"] == d)).sum())
            rows.append({"day": d, "shop": s, "under_maintenance": under, "completed": completed})

    return pd.DataFrame(rows)


def plot_downtime(results: pd.DataFrame):
    """
    Plot total downtime (vehicle-days under maintenance) per day.
    """
    df_metrics = _compute_daily_shop_metrics(results)
    if df_metrics.empty:
        return px.line(title="No downtime data available")

    total_by_day = df_metrics.groupby("day")["under_maintenance"].sum().reset_index()
    fig = px.area(total_by_day, x="day", y="under_maintenance", title="Total Vehicles Under Maintenance (vehicle-days)",
                  labels={"under_maintenance": "Vehicle-days under maintenance", "day": "Day"})
    fig.update_traces(line=dict(color="firebrick"), fillcolor="rgba(178,34,34,0.2)")
    return fig


def plot_load_and_completions(results: pd.DataFrame):
    """
    Plot per-shop load (under maintenance) as a stacked bar and overlay daily completions as a line.
    """
    df_metrics = _compute_daily_shop_metrics(results)
    if df_metrics.empty:
        return px.bar(title="No load/completion data available")

    # stacked bar of under maintenance by shop
    fig = px.bar(df_metrics, x="day", y="under_maintenance", color="shop",
                 title="Shop Load: Vehicles Under Maintenance (stacked by shop)",
                 labels={"under_maintenance": "Under maintenance", "day": "Day"})
    fig.update_layout(barmode="stack")

    # overlay total completions per day
    completions = df_metrics.groupby("day")["completed"].sum().reset_index()
    fig.add_trace(go.Scatter(x=completions["day"], y=completions["completed"], mode="lines+markers",
                             name="Repairs Completed (total)", line=dict(color="white", width=2), yaxis="y"))

    return fig

