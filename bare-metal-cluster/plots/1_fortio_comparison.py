#!/usr/bin/env python3
"""Fortio HTTP latency (P50/P99/Max) across CNI plugins."""
import matplotlib.pyplot as plt
import numpy as np

# Hardcoded from data/1_*_fortio.csv (mean ms, 5 runs except calico_bgp 4 runs)
metrics = ['P50', 'P99', 'Max']

data = {
    'Flannel VXLAN':  [9.26,  38.77, 188.54],
    'Flannel Host-GW':[8.34,  90.33, 681.78],
    'Calico VXLAN':   [9.23,  46.21, 248.93],
    'Calico BGP':     [9.36, 111.24, 291.04],
    'Cilium VXLAN':   [6.56,  27.75,  38.72],
    'Cilium Native':  [11.54, 60.19, 242.44],
}

colors = ['#4e79a7', '#59a14f', '#f28e2b', '#e15759', '#76b7b2', '#b07aa1']
x = np.arange(len(metrics))
width = 0.13
fig, ax = plt.subplots(figsize=(10, 5))

for i, (cni, vals) in enumerate(data.items()):
    ax.bar(x + i * width, vals, width, label=cni, color=colors[i],
           edgecolor='black', linewidth=0.4)

ax.set_xlabel('Percentile')
ax.set_ylabel('Latency (ms)')
ax.set_title('Fortio HTTP Latency — Bare-Metal Cluster')
ax.set_xticks(x + width * 2.5)
ax.set_xticklabels(metrics)
ax.set_yscale('log')
ax.legend(fontsize=8, ncol=3)
plt.tight_layout()
plt.savefig('1_fortio_comparison.png', dpi=150)
print("Saved 1_fortio_comparison.png")
