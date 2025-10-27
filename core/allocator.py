import pulp
import pandas as pd

def allocate_repairs(theater_data: dict) -> pd.DataFrame:
    """
    Allocate broken vehicles from units to maintenance shops using MILP.
    Objective: minimize travel distance subject to shop capacity.
    """
    units = theater_data["units"]
    shops = theater_data["shops"]
    distances = theater_data["distances"]

    prob = pulp.LpProblem("Repair_Allocation", pulp.LpMinimize)

    x = pulp.LpVariable.dicts("assign",
                              ((u, s) for u in units.unit_id for s in shops.shop_id),
                              cat="Binary")

    # Objective: minimize total distance
    prob += pulp.lpSum(x[(u, s)] * distances.loc[u, s] for u in units.unit_id for s in shops.shop_id)

    # Constraints
    for u in units.unit_id:
        prob += pulp.lpSum(x[(u, s)] for s in shops.shop_id) == 1

    for s in shops.shop_id:
        prob += pulp.lpSum(x[(u, s)] for u in units.unit_id) <= shops.loc[shops.shop_id == s, "capacity"].iloc[0]

    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    allocation = [(u, s) for u in units.unit_id for s in shops.shop_id if x[(u, s)].value() == 1]
    return pd.DataFrame(allocation, columns=["unit_id", "assigned_shop"])
