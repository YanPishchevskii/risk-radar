import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

engine = create_engine("postgresql://postgres:risk@localhost:5432/risk")
PAST_DUE = ["past_due_30_59", "past_due_60_89", "past_due_90"]


def clean(df):
    """Чистка по итогам проверок из sql/02_checks.sql"""
    df = df[df.age >= 18].copy()                          # ошибка возраста
    df["revolving_util"] = df.revolving_util.clip(upper=1.5)  # выбросы лимитов
    for col in PAST_DUE:                                  # служебные коды 96/98
        df.loc[df[col] >= 90, col] = np.nan
    return df


def run():
    df = clean(pd.read_sql("SELECT * FROM raw_credit", engine))
    X = df.drop(columns=["client_id", "is_default"])
    y = df.is_default

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    model = make_pipeline(
        SimpleImputer(strategy="median"),   # пропуски дохода и иждивенцев
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=1000),
    )
    model.fit(Xtr, ytr)

    auc = roc_auc_score(yte, model.predict_proba(Xte)[:, 1])
    df["p_default"] = model.predict_proba(X)[:, 1]
    df["risk_band"] = pd.cut(df.p_default, [0, 0.3, 0.6, 1],
                             labels=["low", "medium", "high"], include_lowest=True).astype(str)
    df["scored_at"] = pd.Timestamp.now()
    df[["client_id", "p_default", "risk_band", "scored_at"]].to_sql(
        "fact_scores", engine, if_exists="replace", index=False)

    result = {
        "auc": round(auc, 3),
        "gini": round(2 * auc - 1, 3),
        "clients_scored": len(df),
        "high_risk": int((df.risk_band == "high").sum()),
    }
    return result


if __name__ == "__main__":
    print(run())
