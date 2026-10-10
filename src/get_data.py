from pathlib import Path
from sklearn.datasets import fetch_openml

# Give Me Some Credit с OpenML (id 45577): те же 150 000 строк, что cs-training.csv на Kaggle
data = fetch_openml(data_id=45577, as_frame=True, parser="auto")
df = data.frame
df["SeriousDlqin2yrs"] = df["SeriousDlqin2yrs"].astype(int)
df = df[["SeriousDlqin2yrs"] + [c for c in df.columns if c != "SeriousDlqin2yrs"]]
df.index = range(1, len(df) + 1)

Path("data").mkdir(exist_ok=True)
df.to_csv("data/cs-training.csv")

print("Готово: data/cs-training.csv")
print("Строк:", len(df))
print("Доля дефолтов:", round(df["SeriousDlqin2yrs"].mean(), 4))
print("Колонки:", list(df.columns))
