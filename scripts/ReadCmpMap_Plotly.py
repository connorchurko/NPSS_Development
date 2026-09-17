import re
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

cmp_type = "CmpL"
file_path = f"C:\\Users\\churk\\OneDrive\\Documents\\GeorgiaTech\\Aero6361\\Project3\\AE6361_Project3\\Project_3_NPSS_Release1\\src\\{cmp_type}.map"

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
EFF_CONTOUR_LEVELS = [0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.9]

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
import plotly.graph_objects as go
from scipy.interpolate import griddata
import plotly.io as pio
pio.renderers.default = "browser"

# ── Grid for efficiency contours ─────────────────────────────────────────────
wc_grid  = np.linspace(all_wc.min(), all_wc.max(), 300)
pr_grid  = np.linspace(all_pr.min(), all_pr.max(), 300)
WC, PR   = np.meshgrid(wc_grid, pr_grid)
EFF_GRID = griddata((all_wc, all_pr), all_eff, (WC, PR), method='linear')

# ── Colormap for speed lines (rainbow) ───────────────────────────────────────
def rainbow_color(i, n):
    """Returns a plotly-compatible RGB string across the rainbow spectrum."""
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(i / n, 1.0, 1.0)
    return f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'

def cool_color(i, n):
    """Returns a plotly-compatible RGB string across the cool (cyan→magenta) spectrum."""
    t = i / max(n - 1, 1)
    r = int(t * 255)
    g = int((1 - t) * 255)
    b = 255
    return f'rgb({r},{g},{b})'

# ── Build figure ──────────────────────────────────────────────────────────────
fig = go.Figure()

# ── 1. Efficiency filled contour (background) ─────────────────────────────────
fig.add_trace(go.Contour(
    x=wc_grid,
    y=pr_grid,
    z=EFF_GRID,
    colorscale='rdylgn',
    zmin=all_eff.min(), zmax=all_eff.max(),
    opacity=0.65,
    contours=dict(
        start=0.50, end=0.90, size=(0.90 - 0.50) / 10,
        #start=all_eff.min(), end=all_eff.max(), size=(all_eff.max()-all_eff.min())/30,
        showlabels=True,
        labelfont=dict(size=9, color='black'),
        labelformat='.2f',
    ),
    #line=dict(width=0.8,dash='dash'),
    colorbar=dict(
        title=dict(text='Efficiency', side='right',font=dict(size=20)),
        tickmode='array',
        tickvals=EFF_CONTOUR_LEVELS,
        ticktext=[str(i) for i in EFF_CONTOUR_LEVELS],
        tickfont=dict(size=16),
        thickness=20, len=0.85,
    ),
    name='Efficiency',
    showlegend=False,
    hoverinfo='skip',
))

# ── 2. R-lines (constant RlineMap index across speed lines) ───────────────────
rline_vals = wc_data[ncorr_vals[0]]['RlineMap']
n_rlines   = len(rline_vals)

for r_idx in range(n_rlines):
    rline_wc = []
    rline_pr = []

    for ncorr in ncorr_vals:
        wc_list = wc_data[ncorr]['WcorrMap']
        pr_list = pr_data[ncorr]['PratioMap']
        if r_idx < len(wc_list) and r_idx < len(pr_list):
            rline_wc.append(wc_list[r_idx])
            rline_pr.append(pr_list[r_idx])

    if not rline_wc:
        continue

    show_rline = r_idx in [0, 7, 14]
    color      = cool_color(r_idx, n_rlines)

    fig.add_trace(go.Scatter(
        x=rline_wc,
        y=rline_pr,
        mode='lines',
        line=dict(color=color, width=1.2, dash='dot'),
        opacity=0.8,
        name=f'R={rline_vals[r_idx]:.1f}' if show_rline else None,
        legendgroup='rlines',
        legendgrouptitle=dict(text='R-Lines') if r_idx == 0 else None,
        showlegend=show_rline,
        hovertemplate=(f'<b>Rline = {rline_vals[r_idx]:.1f}</b><br>'
                       f'Wcorr = %{{x:.2f}} lbm/s<br>'
                       f'PR = %{{y:.4f}}<extra></extra>'),
    ))

# ── 3. Speed lines (Wcorr vs PR for each NcorrMap) ───────────────────────────
n          = len(ncorr_vals)
label_step = 4

for idx, ncorr in enumerate(ncorr_vals):
    wc_list = wc_data[ncorr]['WcorrMap']
    pr_list = pr_data[ncorr]['PratioMap']
    min_len = min(len(wc_list), len(pr_list))
    color   = rainbow_color(idx, n)
    show    = idx % label_step == 0

    fig.add_trace(go.Scatter(
        x=wc_list[:min_len],
        y=pr_list[:min_len],
        mode='lines+text',
        line=dict(color=color, width=1.8),
        name=f'Nc={ncorr:.2f}' if show else None,
        legendgroup='speed_lines',
        legendgrouptitle=dict(text='Speed Lines') if idx == 0 else None,
        showlegend=show,
        text=[f'Nc={ncorr:.2f}'] + [''] * (min_len - 1) if show else None,
        textposition='top right',
        textfont=dict(size=7, color=color),
        hovertemplate=(f'<b>Nc = {ncorr:.3f}</b><br>'
                       f'Wcorr = %{{x:.2f}} lbm/s<br>'
                       f'PR = %{{y:.4f}}<extra></extra>'), # note only top level hover template (last plotted) will show when hover mode is 'closest' 
    ))


# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text=f'{cmp_type} Map  (alpha = {alpha_val})',
        font=dict(size=24, family='Arial Black',color="black"),
        x=0.45,
        y=0.92,
    ),
    xaxis=dict(
        title=dict(text='Corrected Mass Flow (lbm/s)', font=dict(size=22)),
        tickfont=dict(family="Arial Black",size=14,color="black"),
        range=[all_wc.min() * 0.98, all_wc.max() * 1.02],
        showgrid=True, gridcolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        automargin=True,
    ),
    yaxis=dict(
        title=dict(text='Pressure Ratio',font=dict(size=22)),
        tickfont=dict(family="Arial Black",size=14,color="black"),
        range=[all_pr.min() * 0.98, all_pr.max() * 1.02],
        showgrid=True, gridcolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        automargin=True,
    ),
    legend=dict(
        x=1.15, y=1,
        xanchor='left', yanchor='top',
        font=dict(size=18),
        title=dict(text='Speed / R-Lines', font=dict(size=18)),
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black', borderwidth=1,
        groupclick='toggleitem',
    ),
    width=1300, height=900,
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='closest',
)


fig.write_html(f'{cmp_type}_map.html')
fig.show()
print(f"{cmp_type} map saved to {cmp_type}_map.html")
