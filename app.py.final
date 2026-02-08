import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Professional Trading PnL Dashboard",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
FILE = "pnl_data.csv"
df = pd.read_csv(FILE)

df["PL"] = pd.to_numeric(df["PL"], errors="coerce")

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
    color_discrete_map={
        "Profit": "#00ff4c",
        "Loss": "#ff2b2b"
    }
)

fig_year.update_layout(template="plotly_dark")
st.plotly_chart(fig_year, use_container_width=True)

# ---------------- EQUITY CURVE ----------------
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

max_val = abs(pivot.max().max())
min_val = -max_val

fig_heat = px.imshow(
    pivot,
    title="Monthly Performance Heatmap",
    aspect="auto",
    zmin=min_val,
    zmax=max_val,
    color_continuous_scale=[
        [0.0, "#b30000"],
        [0.5, "#ff4d4d"],
        [0.5, "#2ecc71"],
        [1.0, "#006400"]
    ]
)

fig_heat.update_layout(template="plotly_dark")
st.plotly_chart(fig_heat, use_container_width=True)

# ---------------- TABLE ----------------
st.subheader("Monthly Data")

def color_pl(val):
    if val > 0:
        return "color:#00ff4c; font-weight:bold;"
    elif val < 0:
        return "color:#ff2b2b; font-weight:bold;"
    else:
        return ""

styled_df = (
    df.style
    .applymap(color_pl, subset=["PL"])
    .applymap(color_pl, subset=["Cumulative"])
    .set_table_styles([
        {
            "selector": "th",
            "props": [
                ("background-color", "#1f2937"),
                ("color", "white"),
                ("font-weight", "bold")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("background-color", "#0f172a")
            ]
        }
    ])
)

st.data_editor(
    styled_df,
    use_container_width=True,
    disabled=True
)

