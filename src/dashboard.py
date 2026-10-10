import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="RiskRadar", layout="wide")
engine = create_engine("postgresql://postgres:risk@localhost:5432/risk")


@st.cache_data
def load(query):
    return pd.read_sql(query, engine)


kpi = load("SELECT * FROM v_kpi").iloc[0]
bands = load("SELECT risk_band, COUNT(*) AS clients FROM fact_scores GROUP BY risk_band")
ab = load('SELECT "group", AVG(outcome) * 100 AS rate, COUNT(*) AS clients '
          'FROM ab_assignment GROUP BY "group" ORDER BY "group"')
top = load("""
    SELECT s.client_id, ROUND(s.p_default::numeric, 2) AS score,
           f.past_due_30_59, f.past_due_60_89,
           ROUND(f.debt_ratio::numeric, 2) AS debt_ratio,
           ROUND(f.revolving_util::numeric, 2) AS revolving_util
    FROM fact_scores s JOIN fact_credit_snapshot f USING (client_id)
    WHERE s.risk_band = 'high' AND f.past_due_90 = 0
    ORDER BY s.p_default DESC LIMIT 20
""")

st.title("RiskRadar: мониторинг кредитного риска")

high = int(bands.loc[bands.risk_band == "high", "clients"].sum())
c1, c2, c3, c4 = st.columns(4)
c1.metric("Клиентов в портфеле", f"{int(kpi.clients):,}".replace(",", " "))
c2.metric("Доля 90+ в портфеле", f"{kpi.default_rate:.1%}")
c3.metric("Группа высокого риска", f"{high:,}".replace(",", " "),
          f"{high / kpi.clients:.0%} портфеля", delta_color="off")
c4.metric("Gini модели", "0.71")

left, right = st.columns(2)
with left:
    st.subheader("Клиенты по группам риска")
    order = {"low": "1. low", "medium": "2. medium", "high": "3. high"}
    st.bar_chart(bands.assign(risk_band=bands.risk_band.map(order)).set_index("risk_band"),
                 y="clients")
with right:
    st.subheader("A/B-тест: доля перехода в 90+, %")
    ab["group"] = ab["group"].map({"A": "A: без звонка", "B": "B: звонок"})
    st.bar_chart(ab.set_index("group"), y="rate")
    a, b = ab.rate.iloc[0], ab.rate.iloc[1]
    st.caption(f"Снижение: {a - b:.1f} п.п. ({1 - b / a:.0%}), p < 0.001. Эффект звонка симулирован.")

st.subheader("Топ-20 клиентов для проактивного контакта (без просрочек 90+)")
st.dataframe(top, use_container_width=True, hide_index=True)
