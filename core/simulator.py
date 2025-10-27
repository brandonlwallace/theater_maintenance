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
                with shops[assigned_shop].request() as req:
                    yield req
                    repair_time = random.expovariate(1 / repair_time_mean)
                    yield env.timeout(repair_time)
                    events.append({"unit": unit, "shop": assigned_shop, "day": day, "repair_time": repair_time})

    for _, row in allocation.iterrows():
        u = row["unit_id"]
        s = row["assigned_shop"]
        break_rate = theater_data["units"].loc[theater_data["units"].unit_id == u, "avg_break_rate"].iloc[0]
        repair_time = theater_data["shops"].loc[theater_data["shops"].shop_id == s, "repair_time_mean"].iloc[0]
        env.process(unit_process(u, s, break_rate, repair_time))

    env.run(until=days)
    return pd.DataFrame(events)
