import pandas as pd
from sqlalchemy import create_engine

# Читаем CSV и даём колонкам короткие понятные имена
df = pd.read_csv("data/cs-training.csv", index_col=0)
df.columns = ["is_default", "revolving_util", "age", "past_due_30_59", "debt_ratio",
              "monthly_income", "open_credit_lines", "past_due_90", "real_estate_loans",
              "past_due_60_89", "dependents"]
df.index.name = "client_id"

# Подключаемся к базе в Docker и записываем таблицу raw_credit
engine = create_engine("postgresql://postgres:risk@localhost:5432/risk")
df.to_sql("raw_credit", engine, if_exists="replace")
print("Загружено строк:", len(df))
