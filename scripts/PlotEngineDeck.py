# ======= Plot Engine Deck =======
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ---- Read Engine Deck ----
file_path = "C:\\Users\\churk\\OneDrive\\Documents\\Projects\\engine_decks\\engine_deck.csv"
engine_deck = pd.read_csv(file_path)

# ---- Store Data ----
machs = engine_deck['Mach']
alts = engine_deck['Alt']
Fn = engine_deck['Fn']

# ---- Find Max Thrust Data ----
thrust_curve = pd.DataFrame()
for im in np.unique(machs):
    for ia in np.unique(alts):
        subset = engine_deck[(engine_deck['Mach']==im) & (engine_deck['Alt']==ia)]
        subset = subset[subset['Fn']==subset['Fn'].max()]
        thrust_curve = pd.concat([thrust_curve,subset], ignore_index = True)

# ---- Reshape Data Arrays ----        
mns = np.array(thrust_curve['Mach']).reshape(len(np.unique(machs)),len(np.unique(alts)))
mns = mns.T
als = np.array(thrust_curve['Alt']).reshape(len(np.unique(machs)),len(np.unique(alts)))
als = als.T
fns = np.array(thrust_curve['Fn']).reshape(len(np.unique(machs)),len(np.unique(alts)))
fns = fns.T

# ---- Plot Contours ----
fig, ax = plt.subplots(figsize=(8,6))
cf = ax.contourf(mns,fns,als)
cl = ax.contour(mns,fns,als, levels=len(np.unique(alts))-1, colors='black', linewidths=0.5, alpha=1.0)
ax.clabel(cl, fmt='%.2f', fontsize=7)
plt.colorbar(cf, ax=ax, label='Altitude (ft)')
ax.set_title('Contour Plot', fontsize=13, fontweight='bold')
ax.set_xlabel('Mach')
ax.set_ylabel('Net Thrust (lbf)')
ax.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()
        


'''#########################
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = 'browser'
fig = go.Figure()

fig.add_trace(go.Contour(
        z=als,
        x=np.unique(machs),
        y=np.linspace(0,40000,9),
        colorscale='RdYlGn',
        contours=dict(
            start=alts.min(),
            end=alts.max(),
            size=len(np.unique(alts)),     # number of levels
            showlabels=True,                    # show contour labels
            labelfont=dict(size=10, color='black'),
        ),
        colorbar=dict(
            title='Altitudes',
            titleside='right',
        ),
        line=dict(width=0.5, color='black'),   # contour line style
    ))

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    title=dict(text='Contour Plot', font=dict(size=16), x=0.5),
    xaxis=dict(title='Mach', showgrid=True),
    yaxis=dict(title='Fn (lbf)', showgrid=True),
    plot_bgcolor='white',
    paper_bgcolor='white',
)

fig.show()'''
        



