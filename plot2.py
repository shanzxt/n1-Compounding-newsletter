import plotly.graph_objects as go

# ============================================================
# Data: AMFI Annual Report, Fiscal 2026, p.8
# "Holding period of SIP AUM as of March 2025 and March 2026"
# These are the ACTUAL published figures. Each column sums to 100% —
# it's a composition snapshot of the money sitting in SIPs as of
# March 2026, NOT a survival/decay curve of a single cohort.
# ============================================================
buckets = [
    "< 1 year",
    "1–2 years",
    "2–3 years",
    "3–4 years",
    "4–5 years",
    "> 5 years",
]

# Order: bottom of the stack -> top
direct_mar26  = [29, 20, 14, 10,  7, 20]   # sums to 100
regular_mar26 = [19, 15, 13, 11,  8, 34]   # sums to 100

plans = ["Direct plan<br>(self-directed)", "Regular plan<br>(via distributor)"]

# --- Sanity check: the whole point of this chart is that the numbers are real ---
assert sum(direct_mar26) == 100, "Direct column must sum to 100%"
assert sum(regular_mar26) == 100, "Regular column must sum to 100%"

BG    = "#0B0E14"
GRID  = "#22262E"
MUTED = "#9CA3AF"
FONT  = "Poppins, Helvetica, Arial, sans-serif"

# Ramp from amber (newest money) through neutral to teal (oldest money).
# Teal = the "still here after 5 years" bucket, matching the colour used
# for the winning lines in the portfolio charts.
BUCKET_COLORS = [
    "#FB923C",   # < 1 year   — amber
    "#F0A868",   # 1–2
    "#9CA3AF",   # 2–3        — neutral grey
    "#6B8F91",   # 3–4
    "#3FBFAE",   # 4–5
    "#5EEAD4",   # > 5 years  — teal
]

fig = go.Figure()

for i, bucket in enumerate(buckets):
    values = [direct_mar26[i], regular_mar26[i]]
    is_top = (i == len(buckets) - 1)
    fig.add_trace(go.Bar(
        x=plans, y=values, name=bucket,
        marker=dict(
            color=BUCKET_COLORS[i],
            line=dict(color=BG, width=1.5),
        ),
        text=[f"<b>{v}%</b>" for v in values],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(
            color=BG if is_top or i >= 4 else BG,
            size=15 if is_top else 13,
            family=FONT,
        ),
        hovertemplate="%{x}<br>" + bucket + ": <b>%{y}%</b><extra></extra>",
    ))

# --- Callout on the > 5 years bucket, which is the whole story ---
fig.add_annotation(
    x=0, y=83, ax=-30, ay=-60,
    text="<b>Only 20% of direct-plan SIP money<br>has been invested 5+ years</b>",
    showarrow=True, arrowhead=0, arrowcolor="#5EEAD4", arrowwidth=1.3,
    font=dict(color="#5EEAD4", size=13), align="left",
    bgcolor="rgba(11,14,20,0.92)", bordercolor="#5EEAD4", borderwidth=1, borderpad=6,
)

fig.add_annotation(
    x=1, y=83, ax=60, ay=-70,
    text="<b>34% for regular plans</b>",
    showarrow=True, arrowhead=0, arrowcolor="#5EEAD4", arrowwidth=1.3,
    font=dict(color="#5EEAD4", size=13), align="left",
    bgcolor="rgba(11,14,20,0.92)", bordercolor="#5EEAD4", borderwidth=1, borderpad=6,
)

fig.update_layout(
    barmode="stack",
    bargap=0.55,
    title=dict(
        text="How long has SIP money actually been invested?",
        font=dict(size=22, color="#F3F4F6", family=FONT),
        x=0.5, xanchor="center", y=0.955,
    ),
    plot_bgcolor=BG, paper_bgcolor=BG,
    font=dict(family=FONT, color="#E5E7EB", size=13),
    xaxis=dict(
        tickfont=dict(size=15, color="#E5E7EB"),
        showgrid=False, showline=True, linecolor=GRID, zeroline=False,
    ),
    yaxis=dict(
        title=dict(text="Share of SIP AUM", font=dict(color=MUTED, size=13)),
        ticksuffix="%", range=[0, 100], dtick=20,
        gridcolor=GRID, showline=False, zeroline=False,
    ),
    legend=dict(
        title=dict(text="Held for:", font=dict(color=MUTED, size=12)),
        bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
        x=1.02, y=1.0, xanchor="left", yanchor="top",
        orientation="v", font=dict(size=13),
        traceorder="reversed",     # top of the stack appears at top of the legend
    ),
    margin=dict(t=110, b=95, l=80, r=200),
    width=1200, height=720,
)

fig.add_annotation(
    text="Source: AMFI Annual Report, Fiscal 2026  ·  holding period of SIP AUM as of March 2026  ·  each column sums to 100%",
    showarrow=False, x=1, y=-0.13, xref="paper", yref="paper",
    font=dict(size=10.5, color=MUTED), xanchor="right",
)

fig.write_image("sip_holding_period.png", scale=2)