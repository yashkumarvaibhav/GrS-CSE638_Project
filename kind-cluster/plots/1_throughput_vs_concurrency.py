#!/usr/bin/env python3
# throughput vs concurrency plot
# shows how TCP throughput changes as we increase parallal streams
# T2 cross-node, 1MB payload

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# iperf3 TCP Gbps - T2 cross-node at 1MB msg size
concurrencies = [1, 16, 64]
thruput = {
    "Flannel": [32.97, 30.96, 27.69],
    "Calico": [24.01, 23.83, 19.97],
    "Cilium": [29.92, 27.40, 25.78],
}

colrs = {"Flannel":"#4ECDC4","Calico":"#FF6B6B","Cilium":"#45B7D1"}
mkr   = {"Flannel":"o","Calico":"s","Cilium":"^"}

fig,ax = plt.subplots(figsize=(9,6))

for cni,vals in thruput.items():
    ax.plot(concurrencies, vals, marker=mkr[cni], color=colrs[cni],
            linewidth=2.5, markersize=9, label=cni)
    for c,v in zip(concurrencies, vals):
        ax.annotate(f'{v:.1f}', (c,v), textcoords='offset points',
                    xytext=(0,10), ha='center', fontsize=8)

ax.set_xlabel('Number of Parallel Streams', fontsize=12)
ax.set_ylabel('TCP Throughput (Gbps)', fontsize=12)
ax.set_title('Throughput vs Concurrency - Cross-Node (T2, 1 MB)', fontsize=14, fontweight='bold')
ax.set_xscale('log', base=2)
ax.set_xticks(concurrencies)
ax.set_xticklabels([str(c) for c in concurrencies], fontsize=11)
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('plots/1_throughput_vs_concurrency.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_throughput_vs_concurrency.png")
