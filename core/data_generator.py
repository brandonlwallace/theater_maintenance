import pandas as pd
import numpy as np

def generate_theater_data(n_units: int, n_shops: int, break_rate: float) -> dict:
    """
    Generate synthetic data for a theater-level logistics network.
    Each unit can experience equipment breakdowns; each shop has capacity limits.
    """
    np.random.seed(42)
    
    # NOTE: add geographic coordinates (lat/lon) for visualization.
    # We'll place the theater roughly within a small bounding box and scatter units/shops
    # within it. These ranges are arbitrary and can be parameterized later.
    lat_min, lat_max = 34.0, 36.0
    lon_min, lon_max = -118.0, -116.0

    units = pd.DataFrame({
        "unit_id": [f"U{i}" for i in range(1, n_units + 1)],
        "daily_ops_tempo": np.random.uniform(0.7, 1.3, n_units),
        "avg_break_rate": break_rate,
        "lat": np.random.uniform(lat_min, lat_max, n_units),
        "lon": np.random.uniform(lon_min, lon_max, n_units),
    })

    shops = pd.DataFrame({
        "shop_id": [f"S{j}" for j in range(1, n_shops + 1)],
        "capacity": np.random.randint(2, 6, n_shops),
        "repair_time_mean": np.random.uniform(2, 6, n_shops),
        "lat": np.random.uniform(lat_min, lat_max, n_shops),
        "lon": np.random.uniform(lon_min, lon_max, n_shops),
    })

    distances = pd.DataFrame(
        np.random.randint(50, 500, size=(n_units, n_shops)),
        index=units["unit_id"], columns=shops["shop_id"]
    )

    return {"units": units, "shops": shops, "distances": distances}
