import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

# --- Same font/style setup as code.py, so this chart matches the rest of the issue ---
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Poppins', 'DejaVu Sans']
plt.rcParams['font.size'] = 15

# --- Load + clean, same as code.py ---
df = pd.read_csv("nifty50_full_history.csv")
df.rename(columns={"HistoricalDate": "date", "CLOSE": "close"}, inplace=True)
df_clean = df[["date", "close"]]
df_clean["date"] = pd.to_datetime(df_clean["date"])
df_clean = df_clean[df_clean["date"].between("1991-08-25", "2026-08-25")]
df_clean = df_clean.set_index("date")
df_clean = df_clean.sort_index(ascending=True)

monthly_closing = df_clean['close'].resample('ME').last()

# --- Flat SIP (same logic as code.py) ---
PortValue = []
total_units = 0
for close in monthly_closing:
    amount = 10000
    total_units += amount / close
    PortValue.append(total_units * close)

# --- Step-up SIP: +10% every 12 months (same logic as code.py) ---
PortValueStepUp = []
total_units_stepup = 0
amount_stepup = 10000
for i, close in enumerate(monthly_closing):
    if i > 0 and i % 12 == 0:
        amount_stepup *= 1.10
    total_units_stepup += amount_stepup / close
    PortValueStepUp.append(total_units_stepup * close)

s_flat   = pd.Series(PortValue, index=monthly_closing.index)
s_stepup = pd.Series(PortValueStepUp, index=monthly_closing.index)

# ============================================================
# Reveal stats — computed once per series
# ============================================================
def reveal_stats(s, label):
    final    = s.iloc[-1]
    five_ago = s.iloc[-61]
    ten_ago  = s.iloc[-121]
    pct_5yr  = (final - five_ago) / final
    pct_10yr = (final - ten_ago) / final
    cross = s[s >= 0.03 * final].index[0]
    years_to_reveal = (cross - s.index[0]).days / 365.25      # years IN to the crossing
    years_after     = (s.index[-1] - cross).days / 365.25     # years still to run after it

    print(f"--- {label} ---")
    print(f"Final value:                    ₹{final/1e7:.2f} Cr")
    print(f"Created in last 5 years:        {pct_5yr:.0%} of it")
    print(f"Created in last 10 years:       {pct_10yr:.0%} of it")
    print(f"Hit 3% of final value in {cross:%b %Y} — "
          f"{years_to_reveal:.1f} years in, {years_after:.1f} years still to run.\n")

    return dict(final=final, cross=cross, pct_5yr=pct_5yr,
                years_to_reveal=years_to_reveal, years_after=years_after)

stats_flat   = reveal_stats(s_flat, "Flat SIP")
stats_stepup = reveal_stats(s_stepup, "10% Step-up SIP")

# ============================================================
# Plot: one reveal panel per strategy, stacked so they're
# directly comparable (same x-axis timeline, own y-scale each)
# ============================================================
BG          = '#0B0E14'
COL_QUIET   = '#374151'
COL_REVEAL  = '#5EEAD4'   # teal — matches sip_retention_funnel_v2.png
COL_MARK    = '#FB923C'   # amber — matches sip_retention_funnel_v2.png
COL_FLAT    = '#E5E7EB'   # near-white — matches code.py's flat SIP line
COL_STEPUP  = '#00e676'   # green — matches code.py's step-up SIP line


def plot_reveal_panel(ax, s, stats, line_color, title):
    final = stats['final']
    cross = stats['cross']
    reveal_value = s.loc[cross]
    five_yr_start = s.index[-61]

    ax.plot(s.index, s.values, color=line_color, linewidth=2, zorder=3)

    # Quiet years: start -> reveal point
    ax.axvspan(s.index[0], cross, color=COL_QUIET, alpha=0.35, zorder=1)
    # Last 5 years: where most of the value was actually created
    ax.axvspan(five_yr_start, s.index[-1], color=COL_REVEAL, alpha=0.12, zorder=1)

    ax.scatter([cross], [reveal_value], color=COL_MARK, s=55, zorder=5,
               edgecolor=BG, linewidth=1.5)

    ax.annotate(
        f"3% of final value.\n{stats['years_to_reveal']:.0f} years in — "
        f"{stats['years_after']:.0f} still to run.",
        xy=(cross, reveal_value), xytext=(25, 55), textcoords='offset points',
        color=COL_MARK, fontsize=10, ha='left',
        arrowprops=dict(arrowstyle='-', color=COL_MARK, lw=1, alpha=0.7),
        bbox=dict(boxstyle='round,pad=0.4', facecolor=BG, edgecolor=COL_MARK, alpha=0.9)
    )
    ax.annotate(
        f"Last 5 years = {stats['pct_5yr']:.0%} of everything",
        xy=(five_yr_start, final * 0.5), xytext=(-150, 0), textcoords='offset points',
        color=COL_REVEAL, fontsize=10, ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=BG, edgecolor=COL_REVEAL, alpha=0.9)
    )
    ax.annotate(
        f"Final: ₹{final/1e7:.2f} Cr",
        xy=(s.index[-1], final), xytext=(-10, 12), textcoords='offset points',
        color=line_color, fontsize=11, fontweight='bold', ha='right',
    )

    ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.25, color='gray')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{x/1e7:.2f}'))
    ax.set_ylabel("₹ Crores", color=line_color)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.set_title(title, color=line_color, fontweight='bold', fontsize=14, pad=12)
    ax.tick_params(colors=line_color, which='both')
    for spine in ax.spines.values():
        spine.set_color(COL_QUIET)
    ax.set_facecolor(BG)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12), sharex=True)
fig.patch.set_facecolor(BG)

plot_reveal_panel(ax1, s_flat, stats_flat, COL_FLAT,
                   "Flat SIP (Rs 10,000/mo): most of it happens at the very end")
plot_reveal_panel(ax2, s_stepup, stats_stepup, COL_STEPUP,
                   "10% Step-up SIP: bigger contributions, same lopsided timing")

ax2.set_xlabel("Year", color=COL_STEPUP)
plt.setp(ax2.get_xticklabels(), rotation=45)

fig.suptitle("The reveal happens late - no matter how you contribute",
             color='#E5E7EB', fontsize=18, fontweight='bold', y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.savefig('day29_reveal_chart.png', dpi=150, facecolor=BG)
#plt.show()