#!/usr/bin/env python3
# latency vs msg size line chart
# compares how latnecy grows with differnt message sizes
# uses netperf data for the T2 cross-node topology

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# netperf mean latency (microseconds), T2 topology
sizes = ["64 B", "4 KB", "1 MB"]
data  = {
    "Flannel": [24.18, 26.51, 468.48],
    "Calico":  [32.91, 36.25, 657.85],
    "Cilium":  [24.63, 29.57, 511.91],
}

clrs    = {"Flannel":"#4ECDC4", "Calico":"#FF6B6B", "Cilium":"#45B7D1"}
mkrs    = {"Flannel":"o",       "Calico":"s",        "Cilium":"^"}

fig, ax = plt.subplots(figsize=(9,6))

xPos = np.arange(len(sizes))
for cni,vals in data.items():
    ax.plot(xPos, vals, marker=mkrs[cni], color=clrs[cni], linewidth=2.5,
            markersize=9, label=cni)
    for xi,v in zip(xPos, vals):
        ax.annotate(f'{v:.1f}', (xi,v), textcoords='offset points',
                    xytext=(0,10), ha='center', fontsize=8)

ax.set_xlabel('Message Size', fontsize=12)
ax.set_ylabel('Mean Latency (us)', fontsize=12)
ax.set_title('Latency vs Message Size - Cross-Node (T2)', fontsize=14, fontweight='bold')
ax.set_xticks(xPos)
ax.set_xticklabels(sizes, fontsize=11)
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('plots/1_latency_vs_msgsize.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_latency_vs_msgsize.png")
