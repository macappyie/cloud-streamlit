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

# ---------------- CREATE FILE IF NOT EXISTS ----------------
if not os.path.exists(FILE):
    pd.DataFrame(columns=["Year","Month","PL"]).to_csv(FILE, index=False)

# ---------------- LOAD DATA ----------------
df = pd.read_csv(FILE)
df["PL"] = pd.to_numeric(df["PL"], errors="coerce")

# ---------------- SIDEBAR : ADD ENTRY ----------------
st.sidebar.header("➕ Add Monthly P/L")

year = st.sidebar.number_input("Year", min_value=2020, max_value=2100, value=2026)
month = st.sidebar.selectbox(
    "Month",
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
)
pl_value = st.sidebar.number_input("Profit / Loss Amount", value=0)

if st.sidebar.button("Save Entry"):
    new_row = pd.DataFrame([[year, month, pl_value]], columns=["Year","Month","PL"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Saved Successfully!")
    st.rerun()

# ---------------- SIDEBAR : DELETE ENTRY ----------------
st.sidebar.divider()
st.sidebar.header("🗑 Delete Entry")

delete_index = st.sidebar.number_input(
    "Row Number (Index)",
    min_value=0,
    max_value=len(df)-1 if len(df)>0 else 0,
    step=1
)

if st.sidebar.button("Delete Selected Row"):
    df = df.drop(index=int(delete_index))
    df = df.reset_index(drop=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Row Deleted Successfully!")
    st.rerun()

# ---------------- SORT DATA ----------------
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
df = df.sort_values(["Year","Month"])

# ---------------- CALCULATIONS ----------------
df["Cumulative"] = df["PL"].cumsum()
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

# ---------------- EQUITY CURVE ----------------
fig_curve = px.line(df, y="Cumulative", title="Equity Curve")
fig_curve.update_layout(template="plotly_dark")
fig_curve.update_traces(line_color="#00ffe5")
st.plotly_chart(fig_curve, use_container_width=True)

# ---------------- HEATMAP ----------------
pivot = df.pivot_table(values="PL", index="Year", columns="Month")
pivot = pivot.reindex(columns=month_order)
max_val = abs(pivot.max().max())

fig_heat = px.imshow(
    pivot,
    zmin=-max_val,
    zmax=max_val,
    color_continuous_scale=[
        [0.0, "#b30000"],
        [0.5, "#ff4d4d"],
        [0.5, "#2ecc71"],
        [1.0, "#006400"]
    ],
    title="Monthly Performance Heatmap",
    aspect="auto"
)

fig_heat.update_layout(template="plotly_dark")
fig_heat.update_traces(
    hovertemplate="Year: %{y}<br>Month: %{x}<br>P/L: %{z}<extra></extra>",
    xgap=2,
    ygap=2
)
st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- TABLE ----------------
st.subheader("Monthly Data")

def color_pl(val):
    if val > 0:
        return "color:#00ff4c;font-weight:bold"
    elif val < 0:
        return "color:#ff2b2b;font-weight:bold"
    return ""

styled = (
    df.style
    .applymap(color_pl, subset=["PL"])
    .applymap(color_pl, subset=["Cumulative"])
)

st.dataframe(styled, use_container_width=True)

