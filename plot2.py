import plotly.graph_objects as go

# --- Data derived from AMFI Annual Report FY26 (holding period of SIP AUM, March 2026) ---
years = [0, 1, 2, 3, 4, 5]
direct_survival  = [100, 71, 51, 38, 28, 20]
regular_survival = [100, 81, 66, 53, 42, 34]
x_labels = ['Start', '1 yr', '2 yrs', '3 yrs', '4 yrs', '5 yrs']

COL_REGULAR = '#5EEAD4'
COL_DIRECT  = '#FB923C'
BG          = '#0B0E14'
GRID        = '#22262E'
MUTED       = '#9CA3AF'

fig = go.Figure()

# --- Fills added FIRST so the lines/markers render crisply on top ---

# Orange fill under the direct-plan curve, down to zero (mirrors the teal band)
fig.add_trace(go.Scatter(
    x=years + years[::-1],
    y=direct_survival + [0]*len(years),
    fill='toself', fillcolor='rgba(251, 146, 60, 0.07)',
    line=dict(width=0), showlegend=False, hoverinfo='skip'
))

# Teal band between the two curves
fig.add_trace(go.Scatter(
    x=years + years[::-1],
    y=regular_survival + direct_survival[::-1],
    fill='toself', fillcolor='rgba(94, 234, 212, 0.06)',
    line=dict(width=0), showlegend=False, hoverinfo='skip'
))

fig.add_trace(go.Scatter(
    x=years, y=regular_survival, mode='lines+markers',
    name='Regular plan (via distributor)',
    line=dict(color=COL_REGULAR, width=3.5, shape='spline', smoothing=0.3),
    marker=dict(size=9, color=BG, line=dict(color=COL_REGULAR, width=2.5)),
))

fig.add_trace(go.Scatter(
    x=years, y=direct_survival, mode='lines+markers',
    name='Direct plan (self-directed)',
    line=dict(color=COL_DIRECT, width=3.5, shape='spline', smoothing=0.3),
    marker=dict(size=9, color=BG, line=dict(color=COL_DIRECT, width=2.5)),
))

# --- Data labels ---
for i, (x, y) in enumerate(zip(years, regular_survival)):
    xshift, yshift = (26, 8) if i == 0 else (0, 18)
    fig.add_annotation(x=x, y=y, text=f'<b>{y}%</b>', showarrow=False,
                        xshift=xshift, yshift=yshift,
                        font=dict(color=COL_REGULAR, size=14),
                        bgcolor='rgba(11,14,20,0.75)', borderpad=2)

for i, (x, y) in enumerate(zip(years, direct_survival)):
    xshift, yshift = (26, -20) if i == 0 else (0, -22)
    fig.add_annotation(x=x, y=y, text=f'<b>{y}%</b>', showarrow=False,
                        xshift=xshift, yshift=yshift,
                        font=dict(color=COL_DIRECT, size=14),
                        bgcolor='rgba(11,14,20,0.75)', borderpad=2)

# --- Callout: anchored to the actual (5, 20) point, but pushed into empty space via PIXEL offsets ---
# (no axref/ayref override -> defaults to 'pixel', which is relative and predictable,
#  unlike data-coordinate anchoring which is what caused the overlap last time)
fig.add_annotation(
    x=5, y=20,                      # the point being called out
    ax=-175, ay=-70,                # text box pushed left + up, in pixels, away from the label
    text="<b>Only 1 in 5 direct-plan<br>SIPs survive 5 years</b>",
    showarrow=True, arrowhead=0, arrowcolor=COL_DIRECT, arrowwidth=1.3,
    font=dict(color=COL_DIRECT, size=13), align='left',
    bgcolor='rgba(11,14,20,0.9)', bordercolor=COL_DIRECT, borderwidth=1, borderpad=6
)

fig.update_layout(
    title=dict(text="Most SIP investors quit long before compounding pays off",
               font=dict(size=22, color='#F3F4F6', family='Poppins, Helvetica, Arial, sans-serif'),
               x=0.5, xanchor='center', y=0.96),
    plot_bgcolor=BG, paper_bgcolor=BG,
    font=dict(family='Poppins, Helvetica, Arial, sans-serif', color='#E5E7EB', size=13),
    xaxis=dict(tickmode='array', tickvals=years, ticktext=x_labels,
               title=dict(text="Time since starting a SIP", font=dict(color=MUTED, size=13)),
               gridcolor=GRID, showline=True, linecolor=GRID, zeroline=False,
               range=[-0.3, 5.9]),
    yaxis=dict(title=dict(text="Still invested (% of SIP AUM)", font=dict(color=MUTED, size=13)),
               ticksuffix='%', range=[0, 112],
               gridcolor=GRID, showline=False, zeroline=False),
    legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)',
                x=0.99, y=1.12, xanchor='right', yanchor='top',
                orientation='h', font=dict(size=12)),
    margin=dict(t=110, b=90, l=70, r=40),
    width=1200, height=720,
)

fig.add_annotation(
    text="Source: AMFI Annual Report, Fiscal 2026  ·  holding period of SIP AUM, March 2026",
    showarrow=False, x=1, y=-0.145, xref='paper', yref='paper',
    font=dict(size=10.5, color=MUTED), xanchor='right'
)

fig.write_image("sip_retention_funnel_v3.png", scale=2)