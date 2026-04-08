#!/usr/bin/env python3
# memory overhead baseline only - T1/T2/T3 without extensions
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

topoLabels = ["T1\n(same-node)","T2\n(cross-node)","T3\n(service)"]
mem_mib = {
    "Flannel": [388.7, 417.8, 429.5],
    "Calico":  [998.4, 1031.4, 1043.9],
    "Cilium":  [969.1, 1025.7, 1044.1],
}

cnis = ["Flannel", "Calico", "Cilium"]
c = {"Flannel":"#4ECDC4", "Calico":"#FF6B6B", "Cilium":"#45B7D1"}

x = np.arange(len(topoLabels))
w = 0.22

fig,ax = plt.subplots(figsize=(9, 6))

for i, cni in enumerate(cnis):
    vals = mem_mib[cni]
    bars = ax.bar(x + (i-1)*w, vals, w, label=cni,
                  color=c[cni], edgecolor='black', linewidth=0.5)
    for bar,val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height()+15,
                f'{val:.0f}', ha='center', va='bottom', fontsize=8)

ax.set_xlabel('Topology', fontsize=12)
ax.set_ylabel('Mean Sampled Memory Usage (MiB)', fontsize=12)
ax.set_title('Mean Node-Container Memory Usage During Benchmark Windows', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(topoLabels, fontsize=10)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0, top=1200)

plt.tight_layout()
plt.savefig('plots/1_memory_overhead_baseline.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_memory_overhead_baseline.png")
