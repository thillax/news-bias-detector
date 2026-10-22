import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# Load bias data
with open('bias_analysis_results.json','r') as f:
    bias_data = json.load(f)

sources = ['CNN', 'The Hindu', 'Al Jazeera', 'NPR']
topics  = ['AI/Technology', 'Politics/Trump', 'War/Conflict', 'Economy']

# Build polarity matrix
matrix = []
for topic in topics:
    row = []
    topic_data = bias_data.get(topic, {})
    for src in sources:
        src_data = topic_data.get(src)
        if src_data and src_data.get('total',0) >= 3:
            row.append(src_data.get('avg_polarity', 0))
        else:
            row.append(None)
    matrix.append(row)

matrix_np = np.array([[v if v is not None else 0 for v in row] for row in matrix])

# Create heatmap
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor('#0f1419')
ax.set_facecolor('#1a1f2e')

# Custom colormap: red=negative, white=neutral, green=positive
colors_list = ['#f44336','#FF9800','#ffffff','#8BC34A','#4CAF50']
cmap = mcolors.LinearSegmentedColormap.from_list('bias', colors_list)

im = ax.imshow(matrix_np, cmap=cmap, aspect='auto', vmin=-0.5, vmax=0.5)

# Labels
ax.set_xticks(range(len(sources)))
ax.set_yticks(range(len(topics)))
ax.set_xticklabels(sources, color='white', fontsize=13, fontweight='bold')
ax.set_yticklabels(topics, color='white', fontsize=12)

# Add values in cells
for i in range(len(topics)):
    for j in range(len(sources)):
        val = matrix[i][j]
        if val is not None:
            color = 'black' if abs(val) < 0.2 else 'white'
            bias_label = '🔴 Neg' if val < -0.1 else ('🟢 Pos' if val > 0.1 else '🟡 Neu')
            ax.text(j, i, f'{val:.3f}\n{bias_label}',
                   ha='center', va='center',
                   color=color, fontsize=10, fontweight='bold')
        else:
            ax.text(j, i, 'N/A', ha='center', va='center',
                   color='gray', fontsize=10)

# Colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Bias Polarity Score', color='white', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

# Title
ax.set_title('📊 Cross-Source Bias Heatmap\nRed = Negative Bias | Green = Positive Bias',
             color='white', fontsize=14, fontweight='bold', pad=15)

ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#2a3142')

plt.tight_layout()
plt.savefig('bias_heatmap.png', dpi=150, bbox_inches='tight',
            facecolor='#0f1419', edgecolor='none')
plt.close()

print("✅ Bias heatmap saved: bias_heatmap.png")

# Also save as HTML for dashboard
html = """
<div style="background:#1a1f2e;border:1px solid #2a3142;border-radius:15px;padding:25px;margin:20px 0;">
    <h3 style="color:#667eea;margin-bottom:20px;">📊 Cross-Source Bias Heatmap</h3>
    <table style="width:100%;border-collapse:collapse;text-align:center;">
        <tr>
            <th style="padding:10px;color:#8899aa;"></th>
"""

for src in sources:
    html += f'<th style="padding:12px;color:#e0e0e0;font-size:14px;font-weight:bold;">{src}</th>\n'

html += '</tr>\n'

for i, topic in enumerate(topics):
    html += f'<tr><td style="padding:12px;color:#667eea;font-weight:bold;text-align:left;">{topic}</td>\n'
    for j, src in enumerate(sources):
        val = matrix[i][j]
        if val is not None:
            if val < -0.2:   bg,tc = '#f44336','white'
            elif val < -0.05: bg,tc = '#FF9800','white'
            elif val > 0.2:  bg,tc = '#4CAF50','white'
            elif val > 0.05: bg,tc = '#8BC34A','black'
            else:             bg,tc = '#607D8B','white'
            label = '🔴' if val < -0.1 else ('🟢' if val > 0.1 else '🟡')
            html += f'<td style="padding:12px;background:{bg};color:{tc};border-radius:8px;margin:2px;">{label} {val:.3f}</td>\n'
        else:
            html += '<td style="padding:12px;color:#8899aa;">N/A</td>\n'
    html += '</tr>\n'

html += """
    </table>
    <p style="color:#8899aa;font-size:12px;margin-top:15px;">
        🔴 Negative Bias | 🟡 Neutral | 🟢 Positive Bias
    </p>
</div>
"""

with open('bias_heatmap.html','w',encoding='utf-8') as f:
    f.write(html)

print("✅ Bias heatmap HTML saved: bias_heatmap.html")
print("✅ Bias Heatmap COMPLETE!")
