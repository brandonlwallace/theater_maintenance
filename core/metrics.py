import pandas as pd

def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average repair times per shop and total repairs completed.
    """
    if results.empty:
        return pd.DataFrame([{"shop": "None", "avg_repair_time": 0, "repairs_completed": 0}])

    summary = results.groupby("shop").agg(
        avg_repair_time=("repair_time", "mean"),
        repairs_completed=("repair_time", "count")
    ).reset_index()

    return summary
