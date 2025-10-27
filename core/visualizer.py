import plotly.express as px
import pandas as pd

def plot_results(results: pd.DataFrame):
    """
    Simple time-series scatter showing repairs completed over time.
    """
    if results.empty:
        return px.scatter(title="No repairs occurred.")

    df = results.groupby("day").size().reset_index(name="repairs")
    fig = px.bar(df, x="day", y="repairs", title="Repairs Completed Over Time")
    return fig

