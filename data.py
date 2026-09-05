from jugaad_data.nse import index_df
from datetime import date

df = index_df(
    symbol="NIFTY 50",
    from_date=date(1990, 1, 1),
    to_date=date(2026, 8, 26)
)
df.to_csv("nifty50_full_history.csv", index=False)