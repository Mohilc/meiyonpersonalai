"""Generates 3D Financial Stock-Style Performance Landscape & Latency Benchmark Graphic for Meiyon Personal AI Manager."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Configure dark financial terminal theme
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), dpi=300, facecolor='#06090F')
ax = fig.add_subplot(111, projection='3d', facecolor='#06090F')

# Pane colors - financial dark trading desk aesthetic
ax.xaxis.set_pane_color((0.05, 0.08, 0.13, 1.0))
ax.yaxis.set_pane_color((0.05, 0.08, 0.13, 1.0))
ax.zaxis.set_pane_color((0.04, 0.06, 0.10, 1.0))

# Financial grid lines
ax.xaxis._axinfo['grid']['color'] = (0.16, 0.22, 0.32, 0.45)
ax.yaxis._axinfo['grid']['color'] = (0.16, 0.22, 0.32, 0.45)
ax.zaxis._axinfo['grid']['color'] = (0.16, 0.22, 0.32, 0.45)

# Benchmark Stock Ticks (Workloads across test runs)
ticks = [
    {"name": "T1: Chat ('Hi')", "open": 35.37, "close": 0.69, "high": 38.45, "low": 0.65, "speedup": "51.3x", "x": 1.0},
    {"name": "T2: Agenda Query", "open": 31.20, "close": 3.12, "high": 34.00, "low": 2.80, "speedup": "10.0x", "x": 2.5},
    {"name": "T3: Daily /briefing", "open": 38.45, "close": 3.70, "high": 40.00, "low": 3.10, "speedup": "10.4x", "x": 4.0},
    {"name": "T4: Multi-Tool Chain", "open": 32.10, "close": 4.45, "high": 36.20, "low": 3.80, "speedup": "7.2x", "x": 5.5},
    {"name": "T5: Webhook / Poller", "open": 28.50, "close": 0.42, "high": 31.00, "low": 0.38, "speedup": "67.9x", "x": 7.0},
]

# Continuous X curve for smooth 3D Stock Mountain Ribbons
x_smooth = np.linspace(0.8, 7.2, 100)
# Interpolated spline curves for Old (High Latency) vs New (Low Latency)
x_pts = [t["x"] for t in ticks]
y_old_pts = [t["open"] for t in ticks]
y_new_pts = [t["close"] for t in ticks]

# Polynomial smooth trendlines
poly_old = np.poly1d(np.polyfit(x_pts, y_old_pts, 3))
poly_new = np.poly1d(np.polyfit(x_pts, y_new_pts, 3))

z_old_smooth = poly_old(x_smooth)
z_new_smooth = poly_new(x_smooth)

# Y-axis depth offsets:
# Y = 1: $MSTR-1T (Previous High-Latency Bear Channel)
# Y = 3: $NEMO-35 (Optimized Sub-Second Bull Channel)
# Y = 5: Volume & Throughput
y_channel_old = 1.0
y_channel_new = 3.2

# 1. Plot 3D Ribbon Mountain Curtain for $MSTR (Crimson/Red)
verts_old = []
for i in range(len(x_smooth) - 1):
    x0, x1 = x_smooth[i], x_smooth[i+1]
    z0, z1 = z_old_smooth[i], z_old_smooth[i+1]
    # Polygon dropping from ribbon to floor (z=0)
    verts_old.append([[x0, y_channel_old, 0], [x1, y_channel_old, 0], [x1, y_channel_old, z1], [x0, y_channel_old, z0]])

poly_coll_old = Poly3DCollection(verts_old, facecolors='crimson', edgecolors='none', alpha=0.35)
ax.add_collection3d(poly_coll_old)

# Top Glowing Trend Ridge for $MSTR
ax.plot(x_smooth, np.full_like(x_smooth, y_channel_old), z_old_smooth, color='#F43F5E', linewidth=3.5, label='$MSTR-1T (Previous High Latency: 28s-38s)')

# 2. Plot 3D Ribbon Mountain Curtain for $NEMO (Emerald/Green Bull Baseline)
verts_new = []
for i in range(len(x_smooth) - 1):
    x0, x1 = x_smooth[i], x_smooth[i+1]
    z0, z1 = z_new_smooth[i], z_new_smooth[i+1]
    verts_new.append([[x0, y_channel_new, 0], [x1, y_channel_new, 0], [x1, y_channel_new, z1], [x0, y_channel_new, z0]])

poly_coll_new = Poly3DCollection(verts_new, facecolors='mediumspringgreen', edgecolors='none', alpha=0.55)
ax.add_collection3d(poly_coll_new)

# Top Glowing Bull Trend Ridge for $NEMO
ax.plot(x_smooth, np.full_like(x_smooth, y_channel_new), z_new_smooth, color='#10B981', linewidth=4.0, label='$NEMO-35 (Optimized Sub-Second: 0.42s-4.45s)')

# 3. Plot 3D Stock Candlestick Stems and OHLC Wicks at each Benchmark Tick
for t in ticks:
    tx = t["x"]
    
    # Candlestick High/Low Wick on $MSTR channel
    ax.plot([tx, tx], [y_channel_old, y_channel_old], [t["open"], t["high"]], color='#FB7185', linewidth=2.0)
    # Candlestick High/Low Wick on $NEMO channel
    ax.plot([tx, tx], [y_channel_new, y_channel_new], [t["low"], t["close"]], color='#6EE7B7', linewidth=2.0)
    
    # 3D Dotted Acceleration Laser connecting Old to New
    ax.plot([tx, tx], [y_channel_old, y_channel_new], [t["open"], t["close"]], color='#38BDF8', linestyle='--', linewidth=1.8, alpha=0.85)
    
    # Old Node (Bear Peak)
    ax.scatter([tx], [y_channel_old], [t["open"]], color='#EF4444', s=90, edgecolor='#FFFFFF', linewidth=1.5, depthshade=False)
    # New Node (Bull Landing)
    ax.scatter([tx], [y_channel_new], [t["close"]], color='#10B981', s=110, edgecolor='#FFFFFF', linewidth=1.8, depthshade=False)
    
    # Labels
    ax.text(tx, y_channel_old, t["open"] + 1.6, f"{t['open']:.1f}s", color='#FCA5A5', fontsize=8.5, fontweight='bold', ha='center')
    ax.text(tx, y_channel_new, t["close"] - 2.8, f"{t['name']}\n{t['close']:.2f}s\n(+{t['speedup']})", color='#34D399', fontsize=8.5, fontweight='bold', ha='center')

# 4. 3D Volume & Throughput Histograms on floor (Y = 4.8)
y_vol = 4.8
volumes = [980, 720, 680, 850, 1200]
for t, vol in zip(ticks, volumes):
    tx = t["x"]
    vz = (vol / 1200) * 12.0  # Scale volume height to max 12s equivalent
    ax.bar3d(tx - 0.25, y_vol - 0.25, 0, 0.5, 0.5, vz, color='#38BDF8', alpha=0.65, edgecolor='#7DD3FC')

# Configure Axes & Limits
ax.set_xlim(0.5, 7.8)
ax.set_ylim(0.2, 5.5)
ax.set_zlim(0, 44)

# Custom Financial Axis Tick Labels
ax.set_xticks(x_pts)
ax.set_xticklabels([t["name"].split(':')[0] for t in ticks], fontsize=9, color='#94A3B8', fontweight='bold')

ax.set_yticks([y_channel_old, y_channel_new, y_vol])
ax.set_yticklabels(['$MSTR Channel', '$NEMO Channel', 'Volume'], fontsize=9, color='#94A3B8', fontweight='bold')

ax.set_xlabel('Benchmark Execution Ticks', fontsize=10, fontweight='bold', color='#9CA3AF', labelpad=14)
ax.set_ylabel('Trading Channels', fontsize=10, fontweight='bold', color='#9CA3AF', labelpad=14)
ax.set_zlabel('Execution Latency (Seconds)', fontsize=10, fontweight='bold', color='#9CA3AF', labelpad=14)

# Set Strategic Financial Orbit View
ax.view_init(elev=22, azim=-55)

# Header & Financial HUD
fig.suptitle('MEIYON PERSONAL AI MANAGER • 3D FINANCIAL LATENCY & PERFORMANCE STREAM', fontsize=15, fontweight='bold', color='#A78BFA', y=0.96)
ax.set_title('3D Candlestick & Mountain Ribbon Volatility: 98% Latency Crash vs 51.3x Throughput Bull Market', fontsize=11, color='#94A3B8', pad=16)

# Financial Legend
legend_elements = [
    Line2D([0], [0], color='#F43F5E', lw=3.5, label='$MSTR-1T (Mistral MoE): High-Latency Crash Plateau (28s - 38s)'),
    Line2D([0], [0], color='#10B981', lw=4.0, label='$NEMO-35 (Nemotron Bolt): Sub-Second Bull Rally (0.42s - 4.45s)'),
    Line2D([0], [0], color='#38BDF8', lw=1.8, linestyle='--', label='Acceleration Vector (Up to 51.3x Latency Reduction)'),
    Line2D([0], [0], color='#38BDF8', lw=6, alpha=0.65, label='Token Throughput Volume (Floor Histogram)')
]
ax.legend(handles=legend_elements, loc='upper left', facecolor='#0D131F', edgecolor='#1F293D', fontsize=8.5, framealpha=0.92)

# Market Telemetry Callout Box
telemetry_hud = (
    "MARKET TELEMETRY ($NEMO-35):\n"
    "• Current Latency: 0.69s (▲ +5,130% SPEED)\n"
    "• Latency Drawdown: -98.0% (-34.68s DROP)\n"
    "• Volatility: 0% TIMEOUTS (ALL-TIME HIGH)\n"
    "• Visual UX: < 50ms Real-Time Typing Pulse\n"
    "• Status: [BULLISH] ULTRA-LOW LATENCY RUN"
)
fig.text(0.81, 0.81, telemetry_hud, fontsize=8.5, color='#F8FAFC', family='monospace',
         bbox=dict(boxstyle='round,pad=0.6', facecolor='#0B111E', edgecolor='#10B981', alpha=0.95, linewidth=1.4))

plt.tight_layout(rect=[0, 0.02, 1, 0.94])

out_path = Path('assets/model_latency_benchmark.png')
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"✅ Generated 3D stock-style financial graphic: {out_path} ({out_path.stat().st_size} bytes)")
