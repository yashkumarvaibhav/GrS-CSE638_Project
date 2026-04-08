#!/usr/bin/env python3
# throughput comparision plot - grouped bar chart
# shows TCP thruput for T1/T2/T3 at 1MB msg size with 16 streams
# hardcoded from our benchamrk runs (see data/1_*_iperf3.csv)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# benchmark results (iperf3 TCP throughput, 1MB payload, 16 parallel streams)
data = {
    "T1 Same-node":  {"Flannel": 51.72, "Calico": 47.67, "Cilium": 60.94},
    "T2 Cross-node": {"Flannel": 30.96, "Calico": 23.83, "Cilium": 27.40},
    "T3 Service":    {"Flannel": 30.92, "Calico": 22.87, "Cilium": 27.78},
}

scenarios = list(data.keys())
cniList = ["Flannel","Calico","Cilium"]
clrs = {"Flannel":"#4ECDC4", "Calico":"#FF6B6B", "Cilium":"#45B7D1"}

x = np.arange(len(scenarios))
barW = 0.22

fig, ax = plt.subplots(figsize=(10,6))

for i,cni in enumerate(cniList):
    vals = [data[s][cni] for s in scenarios]
    bars = ax.bar(x + (i-1)*barW, vals, barW, label=cni,
                  color=clrs[cni], edgecolor='black', linewidth=0.5)
    for bar,val in zip(bars,vals):
        ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+0.5,
                f'{val:.1f}', ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Scenario', fontsize=12)
ax.set_ylabel('TCP Throughput (Gbps)', fontsize=12)
ax.set_title('TCP Throughput Comparison (1 MB payload, 16 streams)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=10)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('plots/1_throughput_comparison.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_throughput_comparison.png")
