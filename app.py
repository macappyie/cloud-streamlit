import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Professional Trading PnL Dashboard",
    layout="wide"
)

FILE = "pnl_data.csv"

# ---------------- LOAD DATA ----------------
if not os.path.exists(FILE):
    pd.DataFrame(columns=["Year","Month","PL"]).to_csv(FILE, index=False)

df = pd.read_csv(FILE)
df["PL"] = pd.to_numeric(df["PL"], errors="coerce")

# ---------------- SIDEBAR : ADD MONTHLY ----------------
st.sidebar.header("➕ Add Monthly P/L")

year = st.sidebar.number_input("Year", 2020, 2035, 2026)
month = st.sidebar.selectbox(
    "Month",
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
)
pl_value = st.sidebar.number_input("Profit / Loss Amount", step=100)

if st.sidebar.button("Save Entry"):
    new_row = pd.DataFrame([[year, month, pl_value]], columns=["Year","Month","PL"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Saved Successfully!")
    st.experimental_rerun()

# ---------------- METRICS ----------------
net_pl = int(df["PL"].sum())

yearly = df.groupby("Year")["PL"].sum().reset_index()
best_year = yearly.loc[yearly["PL"].idxmax()]
worst_year = yearly.loc[yearly["PL"].idxmin()]

# ---------------- HEADER ----------------
st.markdown("## 🚀 Professional Trading PnL Dashboard")

c1, c2, c3 = st.columns(3)
c1.metric("Net P/L", f"{net_pl:,}")
c2.metric("Best Year", int(best_year["Year"]), f"{int(best_year['PL']):,}")
c3.metric("Worst Year", int(worst_year["Year"]), f"{int(worst_year['PL']):,}")

st.divider()

# ---------------- YEARLY BAR ----------------
yearly["Type"] = yearly["PL"].apply(lambda x: "Profit" if x > 0 else "Loss")

fig_year = px.bar(
    yearly,
    x="Year",
    y="PL",
    color="Type",
    title="Yearly Profit / Loss",
    color_discrete_map={"Profit":"#00ff4c","Loss":"#ff2b2b"}
)
fig_year.update_layout(template="plotly_dark")
st.plotly_chart(fig_year, use_container_width=True)

# ---------------- MONTHLY RUNNING TABLE ----------------
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

monthly = df.groupby(["Year","Month"])["PL"].sum().reset_index()
monthly["Month"] = pd.Categorical(monthly["Month"], categories=month_order, ordered=True)
monthly = monthly.sort_values(["Year","Month"])

# ✅ Correct Running Cumulative
monthly["Cumulative"] = monthly["PL"].cumsum()

# ---------------- EQUITY CURVE ----------------
fig_curve = px.line(
    monthly,
    y="Cumulative",
    title="Equity Curve"
)
fig_curve.update_layout(template="plotly_dark")
fig_curve.update_traces(line_color="#00ffe5")
st.plotly_chart(fig_curve, use_container_width=True)

# ---------------- HEATMAP ----------------
pivot = monthly.pivot_table(values="PL", index="Year", columns="Month")
pivot = pivot.reindex(columns=month_order)

max_val = abs(pivot.max().max())
fig_heat = px.imshow(
    pivot,
    zmin=-max_val,
    zmax=max_val,
    color_continuous_scale=[
        [0.0,"#b30000"],
        [0.5,"#ff4d4d"],
        [0.5,"#2ecc71"],
        [1.0,"#006400"]
    ],
    title="Monthly Performance Heatmap",
    aspect="auto"
)
fig_heat.update_layout(template="plotly_dark")
st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- COLORED TABLE ----------------
st.subheader("Monthly Data")

def color_pl(v):
    if v > 0:
        return "color:#00ff4c; font-weight:bold"
    elif v < 0:
        return "color:#ff2b2b; font-weight:bold"
    return ""

styled = monthly.style\
    .applymap(color_pl, subset=["PL"])\
    .applymap(color_pl, subset=["Cumulative"])

st.dataframe(styled, use_container_width=True)

