import streamlit as st
from core.data_generator import generate_theater_data
from core.allocator import allocate_repairs
from core.simulator import run_simulation
from core.metrics import summarize_results
from core.visualizer import plot_results

st.set_page_config(page_title="Theater Maintenance & Supply Queue Simulator", layout="wide")

st.title("Theater Maintenance & Supply Queue Simulator")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Parameters")
n_units = st.sidebar.slider("Number of Combat Units", 3, 20, 8)
n_shops = st.sidebar.slider("Number of Maintenance Depots", 1, 10, 3)
sim_days = st.sidebar.slider("Days to Simulate", 10, 120, 30)
break_rate = st.sidebar.slider("Daily Breakdown Probability", 0.01, 0.2, 0.05)

if st.sidebar.button("Run Simulation"):
    with st.spinner("Generating data and optimizing allocation..."):
        theater_data = generate_theater_data(n_units, n_shops, break_rate)
        allocation = allocate_repairs(theater_data)
        results = run_simulation(theater_data, allocation, sim_days)
        summary = summarize_results(results)

    st.success("Simulation complete!")
    st.write("### Key Results")
    st.dataframe(summary)

    fig = plot_results(results)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Adjust parameters in the sidebar and click **Run Simulation** to begin.")
