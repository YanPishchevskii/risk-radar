import pandas as pd
from fastapi import FastAPI
from sqlalchemy import text
from score import run, engine

app = FastAPI(title="RiskRadar API")


@app.post("/score")
def score():
    """Пересчитать скоринг всего портфеля"""
    return run()


@app.get("/high-risk")
def high_risk(limit: int = 5):
    """Топ клиентов группы риска без просрочек 90+ — для ранних алертов"""
    query = text("""
        SELECT s.client_id,
               ROUND(s.p_default::numeric, 2)::float      AS p_default,
               f.past_due_30_59, f.past_due_60_89, f.past_due_90,
               ROUND(f.debt_ratio::numeric, 2)::float     AS debt_ratio,
               ROUND(f.revolving_util::numeric, 2)::float AS revolving_util
        FROM fact_scores s
        JOIN fact_credit_snapshot f USING (client_id)
        WHERE s.risk_band = 'high' AND f.past_due_90 = 0
        ORDER BY s.p_default DESC
        LIMIT :limit
    """)
    return pd.read_sql(query, engine, params={"limit": limit}).to_dict(orient="records")
