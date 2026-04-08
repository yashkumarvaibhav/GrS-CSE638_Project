#!/usr/bin/env python3
# netperf latency comparison - grouped bar chart
# compares latency across CNIs for T2 (cross-node) at differnt message sizes
# data from data/1_*_netperf.csv

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# netperf mean latency in microseconds, T2 cross-node topology
msg_sizes = ["64 B", "4 KB", "1 MB"]
latency_data = {
    "Flannel": [24.18, 26.51, 468.48],
    "Calico": [32.91, 36.25, 657.85],
    "Cilium": [24.63, 29.57, 511.91],
}

cnis = ["Flannel", "Calico", "Cilium"]
clr = {"Flannel": "#4ECDC4", "Calico": "#FF6B6B", "Cilium": "#45B7D1"}

x = np.arange(len(msg_sizes))
barWidth = 0.22

fig,ax = plt.subplots(figsize=(9,6))

for i,cni in enumerate(cnis):
    vals = latency_data[cni]
    bars = ax.bar(x+(i-1)*barWidth, vals, barWidth, label=cni,
                  color=clr[cni], edgecolor='black', linewidth=0.5)
    # add value labels on top of each bar
    for bar,val in zip(bars,vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()+8,
                f'{val:.1f}', ha='center', va='bottom', fontsize=7)

ax.set_xlabel('Message Size', fontsize=12)
ax.set_ylabel('Mean Latency (us)', fontsize=12)
ax.set_title('Netperf Latency by Message Size - Cross-Node (T2)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(msg_sizes, fontsize=11)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('plots/1_latency_comparison.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_latency_comparison.png")
