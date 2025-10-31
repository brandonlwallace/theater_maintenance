import pandas as pd

def summarize_results(results: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average repair times per shop and total repairs completed.
    """
    if results is None or results.empty:
        return pd.DataFrame([{"shop": "None", "avg_repair_time": 0, "repairs_completed": 0}])

    # Prefer legacy 'repair_time' if present, otherwise use 'repair_days'.
    if "repair_time" in results.columns:
        time_col = "repair_time"
    elif "repair_days" in results.columns:
        time_col = "repair_days"
    else:
        time_col = None

    # Ensure there is a 'shop' column to group by
    if "shop" not in results.columns:
        # If allocation used different naming, try to find an alternative.
        # Fallback: return an overall summary.
        total_repairs = len(results)
        avg_time = results[time_col].mean() if time_col is not None and total_repairs > 0 else 0
        return pd.DataFrame([{"shop": "None", "avg_repair_time": float(avg_time), "repairs_completed": int(total_repairs)}])

    if time_col is not None:
        summary = results.groupby("shop").agg(
            avg_repair_time=(time_col, "mean"),
            repairs_completed=(time_col, "count")
        ).reset_index()
    else:
        # No time column available; count repairs per shop only
        summary = results.groupby("shop").size().reset_index(name="repairs_completed")
        summary["avg_repair_time"] = 0

    # Normalize column order
    summary = summary[["shop", "avg_repair_time", "repairs_completed"]]
    return summary
