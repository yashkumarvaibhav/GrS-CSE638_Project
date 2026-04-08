#!/usr/bin/env python3
# cpu overhead for baseline topologys only (no extensions)
# same data source as cpu_overhead.py but just T1/T2/T3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

scenarioLabels = ["T1\n(same-node)", "T2\n(cross-node)", "T3\n(service)"]
cpu_pct = {
    "Flannel":[110.77, 116.81, 79.84],
    "Calico": [114.07, 123.02, 81.17],
    "Cilium": [116.90, 117.94, 101.59],
}

cniList = ["Flannel","Calico","Cilium"]
colors  = {"Flannel":"#4ECDC4","Calico":"#FF6B6B","Cilium":"#45B7D1"}

x = np.arange(len(scenarioLabels))
w = 0.22

fig, ax = plt.subplots(figsize=(9,6))

for i, cni in enumerate(cniList):
    vals = cpu_pct[cni]
    bars = ax.bar(x+(i-1)*w, vals, w, label=cni,
                  color=colors[cni], edgecolor='black', linewidth=0.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+1.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Topology', fontsize=12)
ax.set_ylabel('Mean Sampled CPU %', fontsize=12)
ax.set_title('Mean Node-Container CPU % During Benchmark Windows', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarioLabels, fontsize=10)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0, top=160)

plt.tight_layout()
plt.savefig('plots/1_cpu_overhead_baseline.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_cpu_overhead_baseline.png")
