import streamlit as st
import pandas as pd
import plotly.express as px


import streamlit as st

# ---------- GLOBAL DARK BOLD THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    color: #E6EDF3;
    background-color: #0e1117;
}

h1, h2, h3, h4 {
    font-weight: 800 !important;
    color: #ffffff !important;
}

p, span, div, label {
    font-weight: 600 !important;
    color: #c9d1d9 !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #0b1220);
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 0 25px rgba(0,255,140,0.12);
    border: 1px solid #1f2933;
}

[data-testid="stMetricValue"] {
    font-size: 36px;
    font-weight: 800;
    color: #00ff99;
}

[data-testid="stMetricDelta"] {
    font-size: 18px;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background-color: #020617;
}

</style>
""", unsafe_allow_html=True)


# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Professional Trading PnL Dashboard",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
FILE = "pnl_data.csv"
df = pd.read_csv(FILE)

df["PL"] = pd.to_numeric(df["PL"], errors="coerce")

# ---------------- METRICS ----------------
net_pl = int(df["PL"].sum())

yearly = df.groupby("Year")["PL"].sum().reset_index()

best_year = yearly.loc[yearly["PL"].idxmax()]
worst_year = yearly.loc[yearly["PL"].idxmin()]

best_delta = int(best_year["PL"])
worst_delta = int(worst_year["PL"])

# ---------------- HEADER ----------------
st.markdown("## 🚀 Professional Trading PnL Dashboard")

c1, c2, c3 = st.columns(3)

c1.metric("Net P/L", f"{net_pl:,}")
c2.metric("Best Year", int(best_year["Year"]), f"{best_delta:,}")
c3.metric("Worst Year", int(worst_year["Year"]), f"{worst_delta:,}")

st.divider()

# ---------------- YEARLY BAR ----------------
yearly["Type"] = yearly["PL"].apply(lambda x: "Profit" if x > 0 else "Loss")

fig_year = px.bar(
    yearly,
    x="Year",
    y="PL",
    title="Yearly Profit / Loss",
    color="Type",
    color_discrete_map={
        "Profit": "#00ff4c",
        "Loss": "#ff2b2b"
    }
)

fig_year.update_layout(template="plotly_dark")
fig_year.update_traces(
    hovertemplate="Year: %{x}<br>P/L: %{y}<extra></extra>"
)

st.plotly_chart(fig_year, use_container_width=True)

# ---------------- EQUITY CURVE ----------------
df["Cumulative"] = df["PL"].cumsum()

fig_curve = px.line(
    df,
    y="Cumulative",
    title="Equity Curve"
)

fig_curve.update_layout(template="plotly_dark")
fig_curve.update_traces(line_color="#00ffe5")

st.plotly_chart(fig_curve, use_container_width=True)

# ---------------- HEATMAP ----------------
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

pivot = df.pivot_table(values="PL", index="Year", columns="Month")
pivot = pivot.reindex(columns=month_order)
pivot = pivot.sort_index()

max_val = abs(pivot.max().max())
min_val = -max_val

fig_heat = px.imshow(
    pivot,
    color_continuous_scale=[
        [0.0, "#b30000"],
        [0.5, "#ff4d4d"],
        [0.5, "#2ecc71"],
        [1.0, "#006400"]
    ],
    zmin=min_val,
    zmax=max_val,
    title="Monthly Performance Heatmap",
    aspect="auto"
)

fig_heat.update_traces(
    hovertemplate="Year: %{y}<br>Month: %{x}<br>P/L: %{z}<extra></extra>",
    xgap=2,
    ygap=2
)

fig_heat.update_layout(
    template="plotly_dark",
    xaxis_title="Month",
    yaxis_title="Year",
    coloraxis_colorbar_title="P/L"
)

st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- TABLE ----------------
st.subheader("Monthly Data")
st.dataframe(df, use_container_width=True)

