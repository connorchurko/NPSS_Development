import pandas as pd

file_dir = "C:\\Users\\churk\\OneDrive\\Documents\\Projects\\engine_decks\\"

# ── Load CSV ──────────────────────────────────────────────────────────────────
file_path = file_dir+"engine_deck.csv"           # ← change to your file path
df = pd.read_csv(file_path,header = None)
df = df.drop(0, axis=0) # drop first row
delim = '\s+'
df = df[0].str.split(delim, expand=True)
last_col = len(df.columns)-1
df = df.drop([0,last_col],axis=1) # remove first/last whitespace columns
df.columns = df.iloc[0]         # set first row as header
df = df[1:]                     # remove first row from data
df = df.reset_index(drop=True)  # reset index
df['Case'] = range(1,len(df['Case'])+1)

# ── Step 5: Save output ───────────────────────────────────────────────────────
output_path = file_dir+"engine_deck.csv"
df.to_csv(output_path, index=False)

import numpy as np
import matplotlib.pyplot as plt

ACTAB = np.zeros((7, 5))
VCTAB = np.zeros((7, 5))

# ── Column 1 (index 0) ────────────────────────────────────────────────────────
ACTAB[:, 0] = [0.0, 0.0, 1500.0, 10000.0, 15000.0, 20000.0, 28000.0]   # altitude schedule
VCTAB[:, 0] = [0.0, 0.3, 250.0,  250.0,   323.0,   374.0,   424.0  ]   # climb speed schedule

# ── Column 2 (index 1) ────────────────────────────────────────────────────────
ACTAB[:, 1] = [0.0, 0.0, 1500.0, 10000.0, 15000.0, 20000.0, 31000.0]
VCTAB[:, 1] = [0.0, 0.3, 250.0,  250.0,   323.0,   374.0,   444.0  ]

# ── Column 3 (index 2) ────────────────────────────────────────────────────────
ACTAB[:, 2] = [0.0, 1500.0, 10000.0, 15000.0, 20000.0, 32500.0, 35000.0]
VCTAB[:, 2] = [0.3, 250.0,  250.0,   323.0,   374.0,   454.67,  449.60 ]

# ── Column 4 (index 3) ────────────────────────────────────────────────────────
ACTAB[:, 3] = [0.0, 1500.0, 10000.0, 15000.0, 20000.0, 32500.0, 39000.0]
VCTAB[:, 3] = [0.3, 250.0,  250.0,   323.0,   374.0,   454.67,  447.39 ]

# ── Column 5 (index 4) ────────────────────────────────────────────────────────
ACTAB[:, 4] = [0.0, 1500.0, 10000.0, 15000.0, 20000.0, 32500.0, 43000.0]
VCTAB[:, 4] = [0.3, 250.0,  250.0,   323.0,   374.0,   454.67,  447.39 ]

with np.errstate(divide='ignore', invalid='ignore'):
    TCTAB = np.where(VCTAB != 0, ACTAB / VCTAB, 0.0)
    
fig, ax = plt.subplots(figsize=(8, 6))

ax.plot(TCTAB[:, -1], ACTAB[:, -1] / 1000,
        linewidth=2, marker='o', markersize=4,
        label=str(ACTAB.shape[1]))   # equivalent to num2str(i) — last column index

ax.set_xlabel('Time (sec)',        fontsize=12)
ax.set_ylabel('Altitude (kft)',    fontsize=12)
ax.set_title('Aircraft Climb Schedule', fontsize=13, fontweight='bold')
ax.grid(True, linestyle='--', alpha=0.6)
#ax.legend()

plt.tight_layout()
plt.show()