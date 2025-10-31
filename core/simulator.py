import simpy
import random
import pandas as pd

def run_simulation(theater_data: dict, allocation: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    SimPy simulation: vehicles break down at units and are repaired at assigned shops.
    """
    env = simpy.Environment()
    
    shops = {
    row["shop_id"]: simpy.Resource(env, capacity=int(row["capacity"]))
    for _, row in theater_data["shops"].iterrows()}
    
    events = []

    def unit_process(unit, assigned_shop, break_rate, repair_time_mean):
        for day in range(days):
            if random.random() < break_rate:
                # Sample an integer repair duration between 1 and 7 days (inclusive)
                repair_days = random.randint(1, 7)
                with shops[assigned_shop].request() as req:
                    yield req
                    # Hold the resource for the full repair duration (in days)
                    yield env.timeout(repair_days)
                    # Record start and end day (end_day is exclusive: completion occurs at start+repair_days)
                    events.append({
                        "unit": unit,
                        "shop": assigned_shop,
                        "start_day": day,
                        "end_day": day + repair_days,
                        "repair_days": repair_days,
                    })

    for _, row in allocation.iterrows():
        u = row["unit_id"]
        s = row["assigned_shop"]
        break_rate = theater_data["units"].loc[theater_data["units"].unit_id == u, "avg_break_rate"].iloc[0]
        # repair_time_mean is no longer used for sampling discrete repair days, but keep signature
        env.process(unit_process(u, s, break_rate, None))

    env.run(until=days)
    return pd.DataFrame(events)
