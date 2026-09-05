import pandas as pd

# ============================================================
# Robustness check: does the "value shows up at the end" shape
# survive a different start date, or is it an artifact of
# starting into the 1992 Harshad Mehta melt-up?
#
# Same load/clean/resample logic as plot1.py / plot3.py, same
# flat-SIP loop, just re-run for a handful of start years —
# each running through to Aug 2026. No chart, plain table.
# ============================================================

df = pd.read_csv("nifty50_full_history.csv")
df.rename(columns={"HistoricalDate": "date", "CLOSE": "close"}, inplace=True)
df_clean = df[["date", "close"]].copy()
df_clean["date"] = pd.to_datetime(df_clean["date"])
df_clean = df_clean[df_clean["date"].between("1991-08-25", "2026-08-25")]
df_clean = df_clean.set_index("date").sort_index()

monthly_full = df_clean["close"].resample("ME").last()

START_YEARS = [1991, 1996, 2001, 2006]
END_DATE = "2026-08-25"


def flat_sip(monthly_closing):
    port_value = []
    total_units = 0
    for close in monthly_closing:
        amount = 10000
        total_units += amount / close
        port_value.append(total_units * close)
    return pd.Series(port_value, index=monthly_closing.index)


rows = []
for year in START_YEARS:
    start = f"{year}-08-25"
    monthly = monthly_full[monthly_full.index.to_series().between(start, END_DATE)]
    s = flat_sip(monthly)

    n = len(s)
    final = s.iloc[-1]
    invested = 10000 * n
    multiple = final / invested

    years = (s.index[-1] - s.index[0]).days / 365.25
    xirr_ish = (final / invested) ** (1 / years) - 1

    five_ago = s.iloc[-61]
    pct_5yr = (final - five_ago) / final

    cross = s[s >= 0.03 * final].index[0]
    years_to_reveal = (cross - s.index[0]).days / 365.25

    rows.append(dict(
        start_year=year,
        final_cr=final / 1e7,
        invested_l=invested / 1e5,
        multiple=multiple,
        annualised=xirr_ish,
        last_5yr_pct=pct_5yr,
        years_to_reveal=years_to_reveal,
    ))

print(f"{'Start':>6} {'Final (Cr)':>12} {'Invested (L)':>13} {'Multiple':>9} "
      f"{'Annualised':>11} {'Last 5yr %':>11} {'Yrs to 3%':>10}")
for r in rows:
    print(f"{r['start_year']:>6} {r['final_cr']:>12.2f} {r['invested_l']:>13.2f} "
          f"{r['multiple']:>8.1f}x {r['annualised']:>10.1%} "
          f"{r['last_5yr_pct']:>10.0%} {r['years_to_reveal']:>9.1f}")
