#!/usr/bin/env python3
# network policy overhead plot
# compares baseline vs E1 (network policy) vs E2 (wireguard) using fortio QPS
# only for calico and cilium since flannel dosent support these extensions
# FIXME: should probably include KPR here too but its only cilium

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# fortio QPS at 4KB, 16 concurrent connections
cni_names = ["Calico", "Cilium"]
conditions = ["Baseline (T2)", "NetworkPolicy (E1)", "WireGuard (E2)"]
qps_data = {
    "Calico": [29147, 28108, 19544],
    "Cilium": [49816, 49677, 18229],
}

condColors = ["#80CBC4", "#FF6B6B", "#45B7D1"]

x = np.arange(len(cni_names))
bw = 0.22  # bar width

fig, ax = plt.subplots(figsize=(9, 6))

for i, cond in enumerate(conditions):
    vals = [qps_data[c][i] for c in cni_names]
    bars = ax.bar(x + (i-1)*bw, vals, bw, label=cond,
                  color=condColors[i], edgecolor='black', linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()+500,
                f'{val:,}', ha='center', va='bottom', fontsize=8)

ax.set_xlabel('CNI Plugin', fontsize=12)
ax.set_ylabel('Fortio QPS', fontsize=12)
ax.set_title('Extension Overhead - Fortio QPS (4 KB, c=16)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(cni_names, fontsize=11)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('plots/1_network_policy_overhead.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_network_policy_overhead.png")
