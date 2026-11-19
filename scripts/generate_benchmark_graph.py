"""Generates production-grade benchmark comparison visual for Meiyon Personal AI Manager."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configure dark executive theme
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, facecolor='#0B0F19')

tasks = [
    'Conversational Chat\n(Hi / Banter)',
    'Academic Attendance\n& Compliance Tool',
    'Task Commitment &\nZapier Scheduling',
    'Google Web Intel\n& Live Grounding',
    'Daily Executive\nBriefing Synthesis'
]

before_latencies = [35.37, 30.50, 29.80, 32.00, 28.20]
after_latencies = [0.69, 3.70, 2.90, 4.10, 3.20]
speedups = [f"{b/a:.1f}x" for b, a in zip(before_latencies, after_latencies)]

y = np.arange(len(tasks))
bar_height = 0.35

# Panel 1: Latency Horizontal Bar Chart
ax1.set_facecolor('#111827')
bars1 = ax1.barh(y + bar_height/2, before_latencies, bar_height, label='Original (Mistral 1T MoE + Retries)', color='#EF4444', alpha=0.9, edgecolor='#F87171')
bars2 = ax1.barh(y - bar_height/2, after_latencies, bar_height, label='Optimized (Nemotron 3.5 Bolt e4b)', color='#10B981', alpha=0.95, edgecolor='#34D399')

ax1.set_yticks(y)
ax1.set_yticklabels(tasks, fontsize=10, fontweight='bold', color='#E5E7EB')
ax1.set_xlabel('End-to-End Latency in Seconds (Lower is Better)', fontsize=11, fontweight='bold', color='#9CA3AF', labelpad=10)
ax1.set_title('Latency Benchmark: Before vs After Optimization', fontsize=13, fontweight='bold', color='#F3F4F6', pad=15)
ax1.grid(axis='x', linestyle='--', alpha=0.25, color='#6B7280')
ax1.legend(loc='lower right', framealpha=0.85, facecolor='#1F2937', edgecolor='#374151', fontsize=9)

# Value annotations
for bar in bars1:
    w = bar.get_width()
    ax1.text(w + 0.6, bar.get_y() + bar.get_height()/2, f"{w:.1f}s", va='center', ha='left', fontsize=9, color='#FCA5A5', fontweight='bold')

for bar, sp in zip(bars2, speedups):
    w = bar.get_width()
    ax1.text(w + 0.6, bar.get_y() + bar.get_height()/2, f"{w:.2f}s ({sp})", va='center', ha='left', fontsize=9, color='#6EE7B7', fontweight='bold')

ax1.set_xlim(0, 43)

# Panel 2: Speedup Multiplier
ax2.set_facecolor('#111827')
factors = [b/a for b, a in zip(before_latencies, after_latencies)]
colors = ['#8B5CF6', '#3B82F6', '#06B6D4', '#10B981', '#F59E0B']
bars_f = ax2.bar(np.arange(len(tasks)), factors, width=0.55, color=colors, edgecolor='#E5E7EB', alpha=0.9)
ax2.set_xticks(np.arange(len(tasks)))
ax2.set_xticklabels(['Chat', 'Attendance', 'Tasks', 'Search', 'Briefing'], fontsize=10, fontweight='bold', color='#E5E7EB')
ax2.set_ylabel('Speedup Factor (Times Faster)', fontsize=11, fontweight='bold', color='#9CA3AF', labelpad=10)
ax2.set_title('Acceleration Factor (Up to 51.3x Faster)', fontsize=13, fontweight='bold', color='#F3F4F6', pad=15)
ax2.grid(axis='y', linestyle='--', alpha=0.25, color='#6B7280')

for bar in bars_f:
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 1.2, f"{h:.1f}x", ha='center', va='bottom', fontsize=10, color='#F3F4F6', fontweight='bold')

ax2.set_ylim(0, 58)

# Title Header
fig.suptitle('MEIYON PERSONAL AI MANAGER • MODEL PERFORMANCE & LATENCY BENCHMARKS', fontsize=14, fontweight='bold', color='#C4B5FD', y=0.98)

plt.tight_layout(rect=[0, 0.03, 1, 0.94])
out_path = Path('assets/model_latency_benchmark.png')
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()
print(f"✅ Generated benchmark graphic: {out_path} ({out_path.stat().st_size} bytes)")
