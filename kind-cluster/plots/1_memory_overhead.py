#!/usr/bin/env python3
# memory overhead chart
# shows avg memory usage (MiB) per CNI during benchmark windows
# includes both baseline and extension scenarios

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# mean memory in MiB from docker stats csvs
scn = ["T1\n(same)","T2\n(cross)","T3\n(svc)","E1\n(policy)","E2\n(encrypt)","E3\n(KPR)"]
memData = {
    "Flannel":[388.7, 417.8, 429.5, None, None, None],
    "Calico": [998.4, 1031.4, 1043.9, 1040.1, 1048.8, None],
    "Cilium": [969.1, 1025.7, 1044.1, 1041.9, 1166.6, 1252.2],
}

cnis = ["Flannel","Calico","Cilium"]
clr = {"Flannel":"#4ECDC4","Calico":"#FF6B6B","Cilium":"#45B7D1"}

x = np.arange(len(scn))
w = 0.22

fig, ax = plt.subplots(figsize=(11, 6))

for i, cni in enumerate(cnis):
    vals = memData[cni]
    pv = [v if v is not None else 0 for v in vals]
    bars = ax.bar(x + (i-1)*w, pv, w, label=cni,
                  color=clr[cni], edgecolor='black', linewidth=0.5)
    for bar, val in zip(bars, vals):
        if val is not None:
            ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+15,
                    f'{val:.0f}', ha='center', va='bottom', fontsize=7)
        else:
            bar.set_alpha(0.0)

ax.set_xlabel('Topology / Extension', fontsize=12)
ax.set_ylabel('Mean Sampled Memory Usage (MiB)', fontsize=12)
ax.set_title('Mean Node-Container Memory Usage During Benchmark Windows', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scn, fontsize=10)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0, top=1400)

plt.tight_layout()
plt.savefig('plots/1_memory_overhead.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_memory_overhead.png")
