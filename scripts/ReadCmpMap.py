import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

file_path = "C:\\Users\\churk\\OneDrive\\Documents\\GeorgiaTech\\Aero6361\\Project3\\AE6361_Project3\\Project_3_NPSS_Release1\\src\\CmpH.map"

with open(file_path, "r") as f:
    text = f.read()

def parse_table(text):
    all_tables = {}
    
    # -- Step 0: Split into Main Tables ----------------------
    table_pattern = re.compile(r'Table\s+(\w+)\s*\([^)]+\)\s*\{', re.DOTALL)
    table_matches = list(table_pattern.finditer(text))
    
    for udx, table_match in enumerate(table_matches):
        table_name  = table_match.group(1)
        block_start = table_match.end()
        block_end   = table_matches[udx + 1].start() if udx + 1 < len(table_matches) else len(text)
        table_block = text[block_start:block_end]

        all_tables[table_name] = {}

        # ── Step 1: split into alphaMap blocks ──────────────────────────────────
        alpha_pattern = re.compile(r'\s+alphaMap\s*=\s*([\d.]+)\s*\{')
        alpha_matches  = list(alpha_pattern.finditer(table_block))
        
        for idx, alpha_match in enumerate(alpha_matches):
            alpha_val = float(alpha_match.group(1))
            all_tables[table_name][alpha_val] = {}
    
            # Grab everything inside this alphaMap block
            block_start = alpha_match.end()
            block_end   = alpha_matches[idx + 1].start() if idx + 1 < len(alpha_matches) else len(text)
            alpha_block = table_block[block_start:block_end]
    
            # ── Step 2: split into NcorrMap blocks ──────────────────────────────
            ncorr_pattern = re.compile(r'NcorrMap\s*=\s*([\d.]+)\s*\{')
            ncorr_matches  = list(ncorr_pattern.finditer(alpha_block))
            current_rline  = None   # used when RlineMap = *
    
            for jdx, ncorr_match in enumerate(ncorr_matches):
                ncorr_val = float(ncorr_match.group(1))
    
                # Grab everything inside this NcorrMap block
                ncorr_start = ncorr_match.end()
                ncorr_end   = ncorr_matches[jdx + 1].start() if jdx + 1 < len(ncorr_matches) else len(alpha_block)
                ncorr_block = alpha_block[ncorr_start:ncorr_end]
    
                # ── Step 3: extract RlineMap ─────────────────────────────────────
                rline_match = re.search(r'RlineMap\s*=\s*(\*|{[^}]+})', ncorr_block)
                if rline_match:
                    rline_str = rline_match.group(1).strip()
                    if rline_str == '*':
                        rline = current_rline        # inherit from previous block
                    else:
                        rline = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', rline_str)]
                        current_rline = rline
                else:
                    rline = current_rline
    
                # ── Step 5: Extract output map (PratioMap / WcorrMap / effAdiabMap)
                output_map   = {}
                map_pattern  = re.compile(r'(\w+Map)\s*=\s*\{([^}]+)\}')
                for map_match in map_pattern.finditer(ncorr_block):
                    map_name   = map_match.group(1)
                    if map_name in ('RlineMap', 'NcorrMap', 'alphaMap'):
                        continue
                    map_values = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', map_match.group(2))]
                    output_map[map_name] = map_values

                all_tables[table_name][alpha_val][ncorr_val] = {
                    'RlineMap': rline,
                    **output_map
                }

    return all_tables


# ── Parse ────────────────────────────────────────────────────────────────────
TB = parse_table(text)


# ── Plot ─────────────────────────────────────────────────────────────────────
# ── Settings ──────────────────────────────────────────────────────────────────
alpha_val       = 0.0
NCORR_STEP      = 1        # plot every Nth speed line (1 = all, 2 = every other, etc.)
EFF_CONTOUR_LEVELS = [0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86, 0.88]

# ── Extract data ─────────────────────────────────────────────────────────────
wc_data  = TB['TB_Wc' ][alpha_val]
eff_data = TB['TB_eff'][alpha_val]
pr_data  = TB['TB_PR' ][alpha_val]

# Common NcorrMap values across all three tables
ncorr_vals = sorted(set(wc_data.keys()) & set(eff_data.keys()) & set(pr_data.keys()))
ncorr_vals = np.array(list(wc_data.keys()))

# ── Build grid for efficiency contours ───────────────────────────────────────
# Collect all (Wcorr, PR, eff) points across all speed lines
all_wc  = []
all_pr  = []
all_eff = []

for ncorr in ncorr_vals:
    wc_list  = wc_data[ncorr]['WcorrMap']
    pr_list  = pr_data[ncorr]['PratioMap']
    eff_list = eff_data[ncorr]['effAdiabMap']
    min_len  = min(len(wc_list), len(pr_list), len(eff_list))
    all_wc .extend(wc_list [:min_len])
    all_pr .extend(pr_list [:min_len])
    all_eff.extend(eff_list[:min_len])

all_wc  = np.array(all_wc)
all_pr  = np.array(all_pr)
all_eff = np.array(all_eff)

# Interpolate scattered points onto a regular grid for contour plotting
from scipy.interpolate import griddata

wc_grid  = np.linspace(all_wc.min(),  all_wc.max(),  300)
pr_grid  = np.linspace(all_pr.min(),  all_pr.max(),  300)
WC, PR   = np.meshgrid(wc_grid, pr_grid)
EFF_GRID = griddata((all_wc, all_pr), all_eff, (WC, PR), method='linear')

# ── Plot ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 10))

# --- Efficiency contours (filled background) ---------------------------------
eff_fill = ax.contourf(WC, PR, EFF_GRID,
                        levels=np.linspace(0.60, 0.90, 31),
                        cmap='RdYlGn', alpha=0.5)
cbar = plt.colorbar(eff_fill, ax=ax, pad=0.02)
cbar.set_label('Adiabatic Efficiency', fontsize=11)

# --- Efficiency contour lines ------------------------------------------------
eff_lines = ax.contour(WC, PR, EFF_GRID,
                        levels=EFF_CONTOUR_LEVELS,
                        colors='black', linewidths=0.8, linestyles='--', alpha=0.7)
ax.clabel(eff_lines, fmt='η=%.2f', fontsize=7, inline=True)

# --- Speed lines (Wcorr vs PR for each NcorrMap) -----------------------------
colors     = cm.rainbow(np.linspace(0, 1, len(ncorr_vals)))
label_step = max(1, len(ncorr_vals) // 15)   # label ~15 speed lines max

for idx, (ncorr, color) in enumerate(zip(ncorr_vals, colors)):
    wc_list  = wc_data[ncorr]['WcorrMap']
    pr_list  = pr_data[ncorr]['PratioMap']
    min_len  = min(len(wc_list), len(pr_list))

    label = f'Nc={ncorr:.2f}' if idx % label_step == 0 else None
    ax.plot(wc_list[:min_len], pr_list[:min_len],
            color=color, linewidth=1.8, label=label, zorder=3)

    # Label at the end of each speed line
    if idx % label_step == 0:
        ax.annotate(f'{ncorr:.2f}',
                    xy=(wc_list[0], pr_list[0]),
                    fontsize=6.5, color=color,
                    xytext=(3, 2), textcoords='offset points')

# --- R-line markers (constant Rline across speed lines) ----------------------
rline_vals = wc_data[ncorr_vals[0]]['RlineMap']
rline_colors = cm.cool(np.linspace(0, 1, len(rline_vals)))

for r_idx, r_color in enumerate(rline_colors):
    rline_wc = []
    rline_pr = []
    for ncorr in ncorr_vals:
        wc_list = wc_data[ncorr]['WcorrMap']
        pr_list = pr_data[ncorr]['PratioMap']
        if r_idx < len(wc_list) and r_idx < len(pr_list):
            rline_wc.append(wc_list[r_idx])
            rline_pr.append(pr_list[r_idx])
    if rline_wc:
        lbl = f'R={rline_vals[r_idx]:.1f}' if r_idx in [0, 7, 14] else None
        ax.plot(rline_wc, rline_pr,
                color=r_color, linewidth=1.2, linestyle=':', alpha=0.8,
                label=lbl, zorder=2)

# ── Formatting ────────────────────────────────────────────────────────────────
ax.set_title(f'Compressor Map  (alphaMap = {alpha_val})', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('Corrected Mass Flow  —  WcorrMap  [lbm/s]', fontsize=12)
ax.set_ylabel('Pressure Ratio  —  PratioMap  [-]',         fontsize=12)
ax.grid(True, linestyle='--', alpha=0.3)
ax.set_xlim(all_wc.min() * 0.98, all_wc.max() * 1.02)
ax.set_ylim(all_pr.min() * 0.98, all_pr.max() * 1.02)

# Legend (speed lines + selected R-lines only)
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels,
          loc='upper left', bbox_to_anchor=(1.08, 1),
          fontsize=7, title='Speed / R-line', title_fontsize=8,
          borderaxespad=0, framealpha=0.9)

plt.tight_layout()
plt.savefig('compressor_map.png', dpi=150, bbox_inches='tight')
plt.show()
print("Compressor map saved to compressor_map.png")
