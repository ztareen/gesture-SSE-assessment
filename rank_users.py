import pandas as pd
from pathlib import Path

IN_PATH = Path("data/user_features.csv")
OUT_PATH = Path("data/top_users.csv")

df = pd.read_csv(IN_PATH)
top = df.sort_values("score", ascending=False).head(10)[
    ["user_id", "username", "score", "score_label", "explanation", "converted"]
]
top.to_csv(OUT_PATH, index=False)
print(f"Wrote {OUT_PATH} with {len(top)} rows")