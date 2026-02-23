import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- INDIAN NUMBER FORMAT ----------------
def format_indian_unit(num):
    abs_num = abs(num)
    if abs_num >= 10000000:
        return f"{num/10000000:.2f} Cr"
    elif abs_num >= 100000:
        return f"{num/100000:.2f} Lakh"
    elif abs_num >= 1000:
        return f"{num/1000:.2f} K"
    else:
        return str(num)

def indian_comma(x):
    try:
        x = int(x)
    except:
        return x

    sign = "-" if x < 0 else ""
    x = abs(x)
    s = str(x)

    if len(s) <= 3:
        return sign + s

    last3 = s[-3:]
    rest = s[:-3]
    parts = []

    while len(rest) > 2:
        parts.append(rest[-2:])
        rest = rest[:-2]

    if rest:
        parts.append(rest)

    return sign + ",".join(reversed(parts)) + "," + last3

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Professional Trading PnL Dashboard", layout="wide")

FILE = "pnl_data.csv"

if not os.path.exists(FILE):
    pd.DataFrame(columns=["Year","Month","PL"]).to_csv(FILE, index=False)

df = pd.read_csv(FILE)
df["PL"] = pd.to_numeric(df["PL"], errors="coerce").fillna(0)

# ---------------- SIDEBAR ----------------
st.sidebar.header("➕ Add Monthly P/L")

year = st.sidebar.number_input("Year", 2020, 2100, 2026)
month = st.sidebar.selectbox("Month", ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
pl_value = st.sidebar.number_input("Profit / Loss Amount", value=0)

if st.sidebar.button("Save Entry"):
    mask = (df["Year"]==year) & (df["Month"]==month)

    if mask.any():
        df.loc[mask,"PL"] += pl_value
    else:
        df = pd.concat([df, pd.DataFrame([[year,month,pl_value]],columns=["Year","Month","PL"])], ignore_index=True)

    df.to_csv(FILE,index=False)
    st.rerun()

# ---------------- SORT ----------------
month_order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
df["Month"]=pd.Categorical(df["Month"],categories=month_order,ordered=True)
df=df.sort_values(["Year","Month"])
df["Cumulative"]=df["PL"].cumsum()

# ---------------- METRICS ----------------
net_pl=int(df["PL"].sum())
yearly=df.groupby("Year")["PL"].sum().reset_index()
best_year=yearly.loc[yearly["PL"].idxmax()]
worst_year=yearly.loc[yearly["PL"].idxmin()]

st.markdown("## 🚀 Professional Trading PnL Dashboard")
c1,c2,c3=st.columns(3)
c1.metric("Net P/L", format_indian_unit(net_pl))
c2.metric("Best Year", int(best_year["Year"]), format_indian_unit(int(best_year["PL"])))
c3.metric("Worst Year", int(worst_year["Year"]), format_indian_unit(int(worst_year["PL"])))

# ---------------- YEARLY BAR ----------------
yearly["Type"]=yearly["PL"].apply(lambda x:"Profit" if x>0 else "Loss")

fig_year=px.bar(yearly,x="Year",y="PL",color="Type",
                color_discrete_map={"Profit":"#00ff4c","Loss":"#ff2b2b"},
                title="Yearly Profit / Loss")

fig_year.update_layout(template="plotly_dark")
fig_year.update_traces(
    hovertemplate="Year: %{x}<br>P/L: %{customdata}<extra></extra>",
    customdata=yearly["PL"].apply(indian_comma)
)

st.plotly_chart(fig_year,use_container_width=True)

# ---------------- EQUITY CURVE ----------------
fig_curve=px.line(df,y="Cumulative",title="Equity Curve")
fig_curve.update_layout(template="plotly_dark")
fig_curve.update_traces(line_color="#00ffe5")
st.plotly_chart(fig_curve,use_container_width=True)

# ---------------- HEATMAP ----------------
pivot=df.pivot_table(values="PL",index="Year",columns="Month").reindex(columns=month_order)

fig_heat=px.imshow(pivot,
                   color_continuous_scale=[[0,"#b30000"],[0.5,"#ff4d4d"],[0.5,"#2ecc71"],[1,"#006400"]],
                   title="Monthly Performance Heatmap")

fig_heat.update_layout(template="plotly_dark")
fig_heat.update_traces(
    hovertemplate="Year: %{y}<br>Month: %{x}<br>P/L: %{customdata}<extra></extra>",
    customdata=pivot.applymap(indian_comma)
)

st.plotly_chart(fig_heat,use_container_width=True)

# ---------------- TABLE ----------------
st.subheader("Monthly Data")
df_display=df.copy()
df_display["PL"]=df_display["PL"].apply(indian_comma)
df_display["Cumulative"]=df_display["Cumulative"].apply(indian_comma)
st.dataframe(df_display,use_container_width=True)
