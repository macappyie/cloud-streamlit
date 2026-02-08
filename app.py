import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Professional Trading PnL Dashboard",
                   layout="wide")

FILE = "pnl_data.csv"

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv(FILE)
except:
    df = pd.DataFrame(columns=["Year","Month","Day","PL"])

df["PL"] = pd.to_numeric(df["PL"], errors="coerce")

# Fill missing day as 1 (for old monthly rows)
if "Day" not in df.columns:
    df["Day"] = 1

# ---------------- SIDEBAR ----------------
st.sidebar.header("➕ Add Daily P/L")

d = st.sidebar.date_input("Select Date", date.today())
pl_input = st.sidebar.number_input("Profit / Loss Amount", value=0)

if st.sidebar.button("Save Daily Entry"):
    new_row = {
        "Year": d.year,
        "Month": d.strftime("%b"),
        "Day": d.day,
        "PL": pl_input
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Saved Successfully ✅")
    st.experimental_rerun()

# ---------------- AGGREGATE MONTHLY ----------------
monthly = df.groupby(["Year","Month"])["PL"].sum().reset_index()

# ---------------- METRICS ----------------
net_pl = int(monthly["PL"].sum())
yearly = monthly.groupby("Year")["PL"].sum().reset_index()

best_year = yearly.loc[yearly["PL"].idxmax()]
worst_year = yearly.loc[yearly["PL"].idxmin()]

# ---------------- HEADER ----------------
st.markdown("## 🚀 Professional Trading PnL Dashboard")

c1,c2,c3 = st.columns(3)
c1.metric("Net P/L", f"{net_pl:,}")
c2.metric("Best Year", int(best_year["Year"]), f"{int(best_year['PL']):,}")
c3.metric("Worst Year", int(worst_year["Year"]), f"{int(worst_year['PL']):,}")

st.divider()

# ---------------- YEARLY BAR ----------------
yearly["Type"] = yearly["PL"].apply(lambda x: "Profit" if x>0 else "Loss")

fig_year = px.bar(
    yearly, x="Year", y="PL",
    color="Type",
    color_discrete_map={"Profit":"#00ff4c","Loss":"#ff2b2b"},
    title="Yearly Profit / Loss"
)
fig_year.update_layout(template="plotly_dark")
st.plotly_chart(fig_year, use_container_width=True)

# ---------------- EQUITY CURVE ----------------
df = df.sort_values(["Year","Month","Day"])
df["Cumulative"] = df["PL"].cumsum()

fig_curve = px.line(df, y="Cumulative", title="Equity Curve")
fig_curve.update_layout(template="plotly_dark")
fig_curve.update_traces(line_color="#00ffe5")
st.plotly_chart(fig_curve, use_container_width=True)

# ---------------- HEATMAP ----------------
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
pivot = monthly.pivot_table(values="PL", index="Year", columns="Month")
pivot = pivot.reindex(columns=month_order)

fig_heat = px.imshow(
    pivot,
    color_continuous_scale=[[0,"#b30000"],[0.5,"#ff4d4d"],
                            [0.5,"#2ecc71"],[1,"#006400"]],
    title="Monthly Performance Heatmap",
    aspect="auto"
)
fig_heat.update_layout(template="plotly_dark")
st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- DAILY TABLE ----------------
st.subheader("All Daily Entries")

def color_pl(v):
    if v>0: return "color:#00ff4c;font-weight:bold"
    if v<0: return "color:#ff2b2b;font-weight:bold"
    return ""

styled = df.style.applymap(color_pl, subset=["PL","Cumulative"])
st.dataframe(styled, use_container_width=True)

