# ======= Plot Engine Deck =======
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ---- Read Engine Deck ----
file_path = "C:\\Users\\churk\\OneDrive\\Documents\\GeorgiaTech\\Aero6361\\Project3\\AE6361_Project3\\Project_3_NPSS_Release1\\view\\engine_deck.csv"
engine_deck = pd.read_csv(file_path)

# ---- Store Data ----
machs = engine_deck['Mach']
alts = engine_deck['Alt']
Fn = engine_deck['Fg']-engine_deck['Fr']
engine_deck['Fn'] = Fn

# ---- Find Max Thrust Data ----
thrust_curve = pd.DataFrame()
tsfc_curve = pd.DataFrame()
for im in np.unique(machs):
    for ia in np.unique(alts):
        subset = engine_deck[(engine_deck['Mach']==im) & (engine_deck['Alt']==ia)]
        fsub = subset[subset['Fn']==subset['Fn'].max()]
        thrust_curve = pd.concat([thrust_curve,fsub], ignore_index = True)
        
        tsub = subset[subset['TSFC']==subset['TSFC'].min()]
        tsfc_curve = pd.concat([tsfc_curve,tsub], ignore_index = True)
        
# ---- Reshape Data Arrays ----        
mns = np.array(thrust_curve['Mach']).reshape(len(np.unique(machs)),len(np.unique(alts)))
mns = mns.T
als = np.array(thrust_curve['Alt']).reshape(len(np.unique(machs)),len(np.unique(alts)))
als = als.T
fns = np.array(thrust_curve['Fn']).reshape(len(np.unique(machs)),len(np.unique(alts)))
fns = fns.T
sfcs = np.array(tsfc_curve['TSFC']).reshape(len(np.unique(machs)),len(np.unique(alts)))
sfcs = sfcs.T

# ---- Plot Thrust Contours ----
fig, ax = plt.subplots(figsize=(8,6))
cf = ax.contourf(mns,fns,als, levels=len(np.unique(alts))-1)
cl = ax.contour(mns,fns,als, levels=len(np.unique(alts))-1, colors='black', linewidths=0.5, alpha=1.0)
ax.clabel(cl, fmt='%.2f', fontsize=7)
plt.colorbar(cf, ax=ax, label='Altitude (ft)')
ax.set_title('Thrust Contours', fontsize=13, fontweight='bold')
ax.set_xlabel('Mach')
ax.set_ylabel('Net Thrust (lbf)')
ax.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()


# ---- Plot TSFC Contours ----
fig, ax = plt.subplots(figsize=(8,6))
cf = ax.contourf(mns,sfcs,als, levels=len(np.unique(alts))-1)
cl = ax.contour(mns,sfcs,als, levels=len(np.unique(alts))-1, colors='black', linewidths=0.5, alpha=1.0)
ax.clabel(cl, fmt='%.2f', fontsize=7)
plt.colorbar(cf, ax=ax, label='Altitude (ft)')
ax.set_title('TSFC Contours', fontsize=13, fontweight='bold')
ax.set_xlabel('Mach')
ax.set_ylabel('TSFC (lbm/(hr*lbf))')
ax.grid(True, linestyle='--', alpha=0.3)
plt.tight_layout()
plt.show()
        