# decision_power_ui.py  -----------------------------------------------------------
# Streamlit playground for autonomy‑identity‑privacy dynamics
# -----------------------------------------------------------
# ▸ Launch with:  streamlit run decision_power_ui.py
# ▸ Requirements: streamlit>=1.30, numpy, pandas, plotly
#
# The game tracks **decision‑making power** over time among three actors:
#     • Individuals  (autonomy / identity control)
#     • Corporations (data‑driven profit & design choices)
#     • The State    (coercion, security, macro‑steering)
# plus the evolving **PET adoption rate**.
# Power flows are influenced by four dial‑up factors:
#     1) Regulation Strength   – privacy & AI oversight pressure
#     2) Security Pressure     – perceived threats ➔ surveillance demand
#     3) Innovation Dividend   – collective learning gains from raw data
#     4) PET Efficiency        – how much PETs preserve innovation value
# The sliders let you stress‑test rival futures and watch who ends up
# calling the shots.

from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Decision‑Power Sandbox", layout="wide")

# -------------------------------------------------------------------
# 1. Model core
# -------------------------------------------------------------------

def simulate(
    p_indiv0: float,
    p_corp0: float,
    p_state0: float,
    pet0: float,
    timesteps: int,
    step: float,
    reg_strength: float,
    sec_pressure: float,
    innovation: float,
    pet_efficiency: float,
) -> pd.DataFrame:
    """Return tidy DF with columns [t, metric, value]. Sums remain ~1."""
    A, C, S = p_indiv0, p_corp0, p_state0  # power shares
    P = pet0                               # PET adoption rate

    rows: list[tuple[int, str, float]] = []

    for t in range(timesteps + 1):
        rows.extend([
            (t, "Individual power", A),
            (t, "Corporate power", C),
            (t, "State power", S),
            (t, "PET adoption", P),
        ])

        # --- power transfers (Δ) --------------------------------------
        delta_C = (
            innovation * (1 - P * pet_efficiency)
            - reg_strength * 0.4
            - sec_pressure * 0.3
        ) * step

        delta_S = (
            sec_pressure * 0.6
            + reg_strength * 0.4
            - P * 0.1
        ) * step

        delta_A = -delta_C - delta_S

        # apply & normalise -------------------------------------------
        C = np.clip(C + delta_C, 0, 1)
        S = np.clip(S + delta_S, 0, 1)
        A = np.clip(A + delta_A, 0, 1)
        total = A + C + S
        if total > 0:
            A, C, S = A / total, C / total, S / total

        # --- PET dynamics --------------------------------------------
        delta_P = (
            reg_strength * 0.5
            + A * 0.3
            - innovation * 0.2
            - sec_pressure * 0.2
            - C * 0.3
        ) * step
        P = np.clip(P + delta_P, 0, 1)

    df = pd.DataFrame(rows, columns=["t", "metric", "value"])
    return df

# -------------------------------------------------------------------
# 2. Sidebar controls
# -------------------------------------------------------------------

st.sidebar.header("⚙️ Global parameters")
T = st.sidebar.slider("Timesteps", min_value=30, max_value=400, value=150, step=10)
step = st.sidebar.slider("Dynamics speed", min_value=0.01, max_value=0.5, value=0.05, step=0.01)

st.sidebar.markdown("---")
reg_strength = st.sidebar.slider("Regulation strength", 0.0, 1.0, 0.3, step=0.05)
sec_pressure = st.sidebar.slider("Security pressure", 0.0, 1.0, 0.2, step=0.05)
innovation    = st.sidebar.slider("Innovation dividend", 0.0, 1.0, 0.6, step=0.05)
pet_efficiency = st.sidebar.slider("PET efficiency", 0.0, 1.0, 0.8, step=0.05)

st.sidebar.markdown("---")

st.sidebar.subheader("Initial shares")
indiv0 = st.sidebar.slider("Individuals", 0.0, 1.0, 0.4, step=0.05)
corp0  = st.sidebar.slider("Corporations", 0.0, 1.0, 0.4, step=0.05)
state0 = st.sidebar.slider("State", 0.0, 1.0, 0.2, step=0.05)
pet0   = st.sidebar.slider("Initial PET adoption", 0.0, 1.0, 0.3, step=0.05)

# sanity normalise
norm = indiv0 + corp0 + state0
if norm == 0:
    indiv0, corp0, state0 = 0.34, 0.33, 0.33
else:
    indiv0, corp0, state0 = indiv0 / norm, corp0 / norm, state0 / norm

run_btn = st.sidebar.button("▶️ Run simulation", type="primary")

# -------------------------------------------------------------------
# 3. Main pane
# -------------------------------------------------------------------

st.title("🧮 Autonomy‑Identity‑Privacy Power Game")
st.write(
    "This toy model lets you explore how decision‑making power shifts between "
    "individuals, corporations, and the state under different pressures. "
    "PET adoption modulates the trade‑off between collective learning and "
    "privacy. Adjust the sliders, run the simulation, then inspect the plots "
    "and final power distribution."
)

if run_btn:
    df = simulate(
        indiv0,
        corp0,
        state0,
        pet0,
        timesteps=T,
        step=step,
        reg_strength=reg_strength,
        sec_pressure=sec_pressure,
        innovation=innovation,
        pet_efficiency=pet_efficiency,
    )

    # ----------- visualise ------------------------------------------
    metrics = ["Individual power", "Corporate power", "State power", "PET adoption"]
    cols = st.columns(len(metrics))
    for metric, col in zip(metrics, cols):
        with col:
            fig = px.line(
                df[df["metric"] == metric],
                x="t",
                y="value",
                title=metric,
            )
            fig.update_layout(xaxis_title="Timestep", yaxis_title="Share / Level")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Final snapshot")
    last = df[df["t"] == df["t"].max()]
    summary = last.pivot_table(index="metric", values="value")
    st.dataframe(summary.style.format("{:.2f}"), height=200)
else:
    st.info("Configure parameters on the left, then click **Run simulation**.")
