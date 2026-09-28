#!/usr/bin/env python3
"""Latency (TCP_RR transactions/sec) by payload size across CNI plugins."""
import matplotlib.pyplot as plt
import numpy as np

# Hardcoded from data/1_*_latency_sizes.csv (mean trans/sec, 5 runs each)
sizes = ['1 B', '64 B', '256 B']

# mean trans/sec per CNI per size
data = {
    'Flannel VXLAN':  [202.25, 191.02, 214.03],
    'Flannel Host-GW':[208.68, 194.76, 189.93],
    'Calico VXLAN':   [175.79, 139.93, 154.65],
    'Calico BGP':     [129.72, 164.38, 177.88],
    'Cilium VXLAN':   [162.73, 167.93, 190.10],
    'Cilium Native':  [110.62, 111.04, 114.72],
}

stdevs = {
    'Flannel VXLAN':  [21.98, 9.97, 15.42],
    'Flannel Host-GW':[14.51, 12.13, 11.10],
    'Calico VXLAN':   [41.13, 33.25, 47.04],
    'Calico BGP':     [23.03, 43.54, 28.59],
    'Cilium VXLAN':   [30.12, 12.76, 31.68],
    'Cilium Native':  [22.55, 4.68, 2.58],
}

colors = ['#4e79a7', '#59a14f', '#f28e2b', '#e15759', '#76b7b2', '#b07aa1']
x = np.arange(len(sizes))
width = 0.13
fig, ax = plt.subplots(figsize=(10, 5))

for i, (cni, vals) in enumerate(data.items()):
    errs = stdevs[cni]
    ax.bar(x + i * width, vals, width, label=cni, color=colors[i],
           yerr=errs, capsize=3, edgecolor='black', linewidth=0.4)

ax.set_xlabel('Payload Size')
ax.set_ylabel('Transactions/sec (TCP_RR)')
ax.set_title('Latency by Payload Size — Bare-Metal Cluster')
ax.set_xticks(x + width * 2.5)
ax.set_xticklabels(sizes)
ax.legend(fontsize=8, ncol=3)
plt.tight_layout()
plt.savefig('1_latency_comparison.png', dpi=150)
print("Saved 1_latency_comparison.png")
