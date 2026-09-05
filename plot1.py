import pandas as pd
import plotly.graph_objects as go

# ============================================================
# Data prep — identical logic to the matplotlib version
# ============================================================
df = pd.read_csv("nifty50_full_history.csv")
df.rename(columns={"HistoricalDate": "date", "CLOSE": "close"}, inplace=True)
df_clean = df[["date", "close"]].copy()
df_clean["date"] = pd.to_datetime(df_clean["date"])
df_clean = df_clean[df_clean["date"].between("1991-08-25", "2026-08-25")]
df_clean = df_clean.set_index("date").sort_index()

monthly_closing = df_clean["close"].resample("ME").last()

# --- Flat SIP ---
PortValue, InvestedFlat = [], []
total_units = total_invested_flat = 0
for close in monthly_closing:
    amount = 10000
    total_units += amount / close
    total_invested_flat += amount
    PortValue.append(total_units * close)
    InvestedFlat.append(total_invested_flat)

# --- Step-up SIP: +10% every 12 months ---
PortValueStepUp, InvestedStepUp = [], []
total_units_stepup = total_invested_stepup = 0
amount_stepup = 10000
for i, close in enumerate(monthly_closing):
    if i > 0 and i % 12 == 0:
        amount_stepup *= 1.10
    total_units_stepup += amount_stepup / close
    total_invested_stepup += amount_stepup
    PortValueStepUp.append(total_units_stepup * close)
    InvestedStepUp.append(total_invested_stepup)

# --- Panic SIP: sells everything at -20% from ATH, re-enters at a new ATH ---
CRASH_THRESHOLD = 0.20
PortValuePanic, InvestedPanic = [], []
units_panic = cash_panic = total_invested_panic = 0
ath = None
state = "in"
for close in monthly_closing:
    ath = close if ath is None else max(ath, close)
    drawdown = (close - ath) / ath

    if state == "in":
        if drawdown <= -CRASH_THRESHOLD:
            cash_panic = units_panic * close
            units_panic = 0
            state = "out"
        else:
            units_panic += 10000 / close
            total_invested_panic += 10000
    else:
        if close >= ath:
            units_panic += cash_panic / close
            cash_panic = 0
            state = "in"
            units_panic += 10000 / close
            total_invested_panic += 10000

    PortValuePanic.append(units_panic * close + cash_panic)
    InvestedPanic.append(total_invested_panic)

dates = monthly_closing.index
CR = 1e7  # 1 crore

flat = [v / CR for v in PortValue]
stepup = [v / CR for v in PortValueStepUp]
panic = [v / CR for v in PortValuePanic]

# ============================================================
# Style
# ============================================================
BG          = "#0B0E14"
GRID        = "#22262E"
MUTED       = "#9CA3AF"
COL_FLAT    = "#E5E7EB"   # near-white
COL_STEPUP  = "#5EEAD4"   # teal
COL_PANIC   = "#FB923C"   # amber

COL_GAP_FILL     = "rgba(148, 163, 184, 0.07)"   # neutral grey — cost-of-panic band
COL_STEPUP_FILL  = "rgba(94, 234, 212, 0.10)"    # soft teal — step-up premium band

FONT = "Poppins, Helvetica, Arial, sans-serif"


def fmt_cr(x):
    return f"₹{x/CR:.2f} Cr"


def fmt_lakh(x):
    return f"₹{x/1e5:.1f} L"


fig = go.Figure()

# --- Fill 1: cost-of-panic band, between flat and panic ---
fig.add_trace(go.Scatter(
    x=list(dates) + list(dates[::-1]),
    y=flat + panic[::-1],
    fill="toself", fillcolor=COL_GAP_FILL,
    line=dict(width=0), showlegend=False, hoverinfo="skip",
))

# --- Fill 2: step-up premium band, between step-up and flat ---
fig.add_trace(go.Scatter(
    x=list(dates) + list(dates[::-1]),
    y=stepup + flat[::-1],
    fill="toself", fillcolor=COL_STEPUP_FILL,
    line=dict(width=0), showlegend=False, hoverinfo="skip",
))

# --- Step-up line: dark halo first for contrast, then the colored line on top ---
fig.add_trace(go.Scatter(
    x=dates, y=stepup, mode="lines",
    line=dict(color=BG, width=5.5),
    showlegend=False, hoverinfo="skip",
))
fig.add_trace(go.Scatter(
    x=dates, y=stepup, mode="lines",
    name="Step-up SIP (+10% every 12 mo)",
    line=dict(color=COL_STEPUP, width=3),
    hovertemplate="%{x|%b %Y}<br><b>₹%{y:.2f} Cr</b><extra>Step-up SIP</extra>",
))

fig.add_trace(go.Scatter(
    x=dates, y=flat, mode="lines",
    name="Flat SIP (₹10,000/mo)",
    line=dict(color=COL_FLAT, width=2.8),
    hovertemplate="%{x|%b %Y}<br><b>₹%{y:.2f} Cr</b><extra>Flat SIP</extra>",
))

# --- Panic line: same dark-halo treatment so it survives sitting on the fill edge ---
fig.add_trace(go.Scatter(
    x=dates, y=panic, mode="lines",
    line=dict(color=BG, width=5),
    showlegend=False, hoverinfo="skip",
))
fig.add_trace(go.Scatter(
    x=dates, y=panic, mode="lines",
    name="Panic SIP (sells at −20% crash)",
    line=dict(color=COL_PANIC, width=2.8),
    hovertemplate="%{x|%b %Y}<br><b>₹%{y:.2f} Cr</b><extra>Panic SIP</extra>",
))

# --- End-point dots ---
last = dates[-1]
for value, color in [(stepup[-1], COL_STEPUP), (flat[-1], COL_FLAT), (panic[-1], COL_PANIC)]:
    fig.add_trace(go.Scatter(
        x=[last], y=[value], mode="markers",
        marker=dict(size=9, color=BG, line=dict(color=color, width=2.5)),
        showlegend=False, hoverinfo="skip",
    ))

# --- Final-value callouts ---
callouts = [
    (stepup[-1], COL_STEPUP, PortValueStepUp[-1], InvestedStepUp[-1], -210, -55),
    (flat[-1],   COL_FLAT,   PortValue[-1],       InvestedFlat[-1],    -195,  40),
    (panic[-1],  COL_PANIC,  PortValuePanic[-1],  InvestedPanic[-1],   -185,  50),
]
for y, color, final_val, invested, ax_off, ay_off in callouts:
    fig.add_annotation(
        x=last, y=y, ax=ax_off, ay=ay_off,
        text=f"<b>{fmt_cr(final_val)}</b><br>invested {fmt_lakh(invested)}",
        showarrow=True, arrowhead=0, arrowcolor=color, arrowwidth=1.2,
        font=dict(color=color, size=12.5), align="left",
        bgcolor="rgba(11,14,20,0.9)", bordercolor=color, borderwidth=1, borderpad=6,
    )

# --- Narrative callout: what the panic cost ---
# FIX: previously anchored around 82% along the timeline, which put the box
# right on top of the flat SIP's final-value callout (~2018-2020 in pixel
# space once ax/ay pushed it left). Moved earlier (65%, ~2015-2016) where
# there's clear empty space below the step-up climb and above the flat
# line, well clear of the cluster of end-of-chart callouts.
gap = PortValue[-1] - PortValuePanic[-1]
anchor_idx = int(len(dates) * 0.65)
fig.add_annotation(
    x=dates[anchor_idx], y=panic[anchor_idx],
    ax=10, ay=-140,
    text=f"<b>Selling at every −20% crash<br>cost {fmt_cr(gap)}</b>",
    showarrow=True, arrowhead=0, arrowcolor=COL_PANIC, arrowwidth=1.4,
    font=dict(color=COL_PANIC, size=13), align="left",
    bgcolor="rgba(11,14,20,0.9)", bordercolor=COL_PANIC, borderwidth=1, borderpad=6,
)

fig.update_layout(
    title=dict(
        text="Staying in beats timing it — by an entire portfolio",
        font=dict(size=22, color="#F3F4F6", family=FONT),
        x=0.5, xanchor="center", y=0.96,
    ),
    plot_bgcolor=BG, paper_bgcolor=BG,
    font=dict(family=FONT, color="#E5E7EB", size=13),
    hovermode="x unified",
    xaxis=dict(
        title=dict(text="Year", font=dict(color=MUTED, size=13)),
        dtick="M24", tickformat="%Y",
        gridcolor=GRID, showline=True, linecolor=GRID, zeroline=False,
        range=[dates[0], last + pd.Timedelta(days=400)],
    ),
    yaxis=dict(
        title=dict(text="Portfolio value (₹ crores)", font=dict(color=MUTED, size=13)),
        tickformat=".2f",
        gridcolor=GRID, showline=False, zeroline=False,
        rangemode="tozero",
    ),
    # FIX: legend swatches were thin/small and hard to read at a glance.
    # itemwidth widens the line swatch itself; bumping font size and giving
    # the legend its own row of breathing room (higher y) makes it read
    # as a proper key rather than fine print.
    legend=dict(
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
        x=0.0, y=1.16, xanchor="left", yanchor="top",
        orientation="h", font=dict(size=16),
        itemwidth=60, tracegroupgap=25,
    ),
    margin=dict(t=130, b=100, l=80, r=40),
    width=1200, height=760,
)

fig.add_annotation(
    text="Nifty 50 monthly closes, Aug 1991 – Aug 2026  ·  price index only, dividends excluded  ·  no expense ratio or exit load",
    showarrow=False, x=1, y=-0.16, xref="paper", yref="paper",
    font=dict(size=10.5, color=MUTED), xanchor="right",
)

fig.write_image("sip_portfolio.png", scale=2)