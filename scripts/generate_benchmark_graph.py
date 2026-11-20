"""Generates 2D Multi-Line Model Performance & Latency Benchmark Graphic for Meiyon Personal AI Manager."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D

# Configure dark executive theme
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 7.5), dpi=300, facecolor='#0B0F19')
ax.set_facecolor('#0E1422')

# Benchmark data
tasks = [
    "Casual Chat ('Hi')",
    "Agenda & Attendance",
    "Daily /briefing",
    "Multi-Tool Reasoning",
    "Telegram Webhook"
]
x_indices = np.arange(len(tasks))
prev_latency = [35.37, 31.20, 38.45, 32.10, 28.50]
opt_latency = [0.69, 3.12, 3.70, 4.45, 0.42]
speedups = ["51.3x", "10.0x", "10.4x", "7.2x", "67.9x"]
drops = ["-98.0%", "-90.0%", "-90.4%", "-86.1%", "-98.5%"]

# Subtle custom grid
ax.grid(True, linestyle='--', alpha=0.25, color='#334155')

# 1. Shaded Delta Fill between the two lines to highlight the latency reduction zone
ax.fill_between(
    x_indices, prev_latency, opt_latency,
    color='#10B981', alpha=0.12, label='Latency Reduction Zone (Up to 98% Saved Time)'
)

# 2. Line 1: Previous Model (Mistral Large 1T MoE - Crimson Red)
ax.plot(
    x_indices, prev_latency,
    color='#F43F5E', linewidth=3.2, linestyle='--',
    marker='o', markersize=9, markerfacecolor='#EF4444', markeredgecolor='#FFFFFF', markeredgewidth=1.5,
    label='Previous: Mistral Large 1T MoE (28s – 38s High Latency Plateau)'
)

# 3. Line 2: Optimized Model (NVIDIA Nemotron 3.5 Bolt - Emerald Green)
ax.plot(
    x_indices, opt_latency,
    color='#10B981', linewidth=3.8, linestyle='-',
    marker='s', markersize=10, markerfacecolor='#10B981', markeredgecolor='#FFFFFF', markeredgewidth=1.8,
    label='Optimized: NVIDIA Nemotron 3.5 Bolt (0.42s – 4.45s Sub-Second Baseline)'
)

# 4. Vertical Delta Connectors & Point Value Annotations
for i, (tx, zo, zn, sp, dr) in enumerate(zip(x_indices, prev_latency, opt_latency, speedups, drops)):
    # Vertical connector
    ax.vlines(x=tx, ymin=zn, ymax=zo, color='#38BDF8', linestyle=':', linewidth=1.5, alpha=0.7)
    
    # Previous value label (above node)
    ax.annotate(
        f"{zo:.1f}s",
        xy=(tx, zo), xytext=(0, 10), textcoords="offset points",
        ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#FCA5A5'
    )
    
    # Optimized value label (below node)
    ax.annotate(
        f"{zn:.2f}s\n({sp})",
        xy=(tx, zn), xytext=(0, -26), textcoords="offset points",
        ha='center', va='top', fontsize=9.5, fontweight='bold', color='#6EE7B7'
    )
    
    # Drop % badge in the middle of connector
    mid_y = (zo + zn) / 2
    ax.text(
        tx + 0.08, mid_y, dr,
        fontsize=8.5, fontweight='bold', color='#38BDF8',
        bbox=dict(boxstyle='round,pad=0.25', facecolor='#0B111E', edgecolor='#0284C7', alpha=0.85, linewidth=0.8)
    )

# Axis formatting
ax.set_xticks(x_indices)
ax.set_xticklabels(tasks, fontsize=10.5, fontweight='bold', color='#E2E8F0')
ax.set_ylabel('End-to-End Latency (Seconds)', fontsize=11, fontweight='bold', color='#94A3B8', labelpad=10)
ax.set_ylim(-2, 45)
ax.set_xlim(-0.4, len(tasks) - 0.6)

# Titles
fig.suptitle('MEIYON PERSONAL AI MANAGER • MODEL LATENCY BENCHMARK', fontsize=15, fontweight='bold', color='#C4B5FD', y=0.96)
ax.set_title('2D Multi-Line Trajectory Comparing Previous Mistral 1T MoE vs Optimized NVIDIA Nemotron 3.5 Bolt', fontsize=11, color='#94A3B8', pad=14)

# Legend
legend = ax.legend(loc='upper right', facecolor='#111827', edgecolor='#1F2937', fontsize=9.5, framealpha=0.92)
for text in legend.get_texts():
    text.set_color('#E2E8F0')

# Executive Telemetry Callout Box
telemetry_box = (
    "KEY OPTIMIZATIONS:\n"
    "• Casual Greeting: 0.69s (51.3x Speedup)\n"
    "• Multi-Tool Reasoning: 4.45s (7.2x Speedup)\n"
    "• Telegram Visual UX: < 50ms Real-Time Typing\n"
    "• 504 Gateway Timeouts: 100% Eliminated\n"
    "• Mean Latency Reduction: 92.6%"
)
ax.text(
    0.02, 0.96, telemetry_box,
    transform=ax.transAxes, fontsize=9, family='monospace', color='#F8FAFC', va='top',
    bbox=dict(boxstyle='round,pad=0.6', facecolor='#0B111E', edgecolor='#10B981', alpha=0.92, linewidth=1.2)
)

plt.tight_layout(rect=[0, 0.02, 1, 0.94])

out_path = Path('assets/model_latency_benchmark.png')
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"Generated 2D line benchmark graphic: {out_path} ({out_path.stat().st_size} bytes)")
