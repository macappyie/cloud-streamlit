import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ---------------- CONFIG ----------------
st.set_page_config(page_title="PnL Dashboard", layout="wide")
FILE = "pnl_data.csv"

# ---------------- LOAD DATA ----------------
try:
    df = pd.read_csv(FILE)
except:
    df = pd.DataFrame(columns=["Year","Month","Day","PL"])

df["PL"] = pd.to_numeric(df["PL"], errors="coerce")
df = df.dropna()

# ---------------- DAILY ENTRY ----------------
st.sidebar.header("➕ Add Daily P/L")

entry_date = st.sidebar.date_input(
    "Select Date",
    value=date(2026,2,1)
)

pl_value = st.sidebar.number_input(
    "Profit / Loss Amount",
    value=0
)

if st.sidebar.button("Save Entry"):
    new_row = {
        "Year": entry_date.year,
        "Month": entry_date.strftime("%b"),
        "Day": entry_date.day,
        "PL": pl_value
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.sidebar.success("Saved Successfully ✅")
    st.rerun()

# ---------------- METRICS ----------------
net_pl = int(df["PL"].sum())
yearly = df.groupby("Year")["PL"].sum().reset_index()
best_year = yearly.loc[yearly["PL"].idxmax()]
worst_year = yearly.loc[yearly["PL"].idxmin()]

# ---------------- TITLE ----------------
st.title("📊 Professional Trading PnL Dashboard")

c1,c2,c3 = st.columns(3)
c1.metric("Net P/L", f"{net_pl:,}")
c2.metric("Best Year", int(best_year["Year"]), f"{int(best_year['PL']):,}")
c3.metric("Worst Year", int(worst_year["Year"]), f"{int(worst_year['PL']):,}")

# ---------------- YEARLY BAR ----------------
st.subheader("Yearly Profit / Loss")

yearly["Type"] = yearly["PL"].apply(lambda x: "Profit" if x>0 else "Loss")

fig_year = px.bar(
    yearly,
    x="Year",
    y="PL",
    color="Type",
    color_discrete_map={"Profit":"green","Loss":"red"}
)
st.plotly_chart(fig_year, use_container_width=True)

# ---------------- MONTHLY HEATMAP ----------------
st.subheader("Monthly Performance Heatmap")

month_order=["Jan","Feb","Mar","Apr","May","Jun",
             "Jul","Aug","Sep","Oct","Nov","Dec"]

pivot = df.pivot_table(index="Year",columns="Month",values="PL",aggfunc="sum")
pivot = pivot.reindex(columns=month_order)

fig_heat = px.imshow(
    pivot,
    color_continuous_scale=["red","white","green"],
    labels=dict(color="P/L")
)
st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- DATA TABLE ----------------
st.subheader("All Trades / Entries")
st.dataframe(df.sort_values(["Year","Month","Day"]))

