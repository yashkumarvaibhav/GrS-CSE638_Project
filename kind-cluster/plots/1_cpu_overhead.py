#!/usr/bin/env python3
# cpu overhead plot - shows mean CPU% during benchamrk runs
# includes both baseline topologys and extensions
# collected from docker stats CSVs sampled every ~3sec
# (sampling rate is in fast_benchmark.py start_stats func)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# mean CPU % from docker stats during benchmarks
scn_labels = ["T1\n(same)","T2\n(cross)","T3\n(svc)","E1\n(policy)","E2\n(encrypt)","E3\n(KPR)"]
cpuData = {
    "Flannel": [110.77, 116.81, 79.84, None, None, None],
    "Calico":  [114.07, 123.02, 81.17, 125.57, 62.64, None],
    "Cilium":  [116.90, 117.94, 101.59, 123.84, 45.57, 109.91],
}

cnis = ["Flannel","Calico","Cilium"]
clr  = {"Flannel":"#4ECDC4","Calico":"#FF6B6B","Cilium":"#45B7D1"}

x = np.arange(len(scn_labels))
w = 0.22

fig,ax = plt.subplots(figsize=(11,6))

for i,cni in enumerate(cnis):
    vals = cpuData[cni]
    # replace None with 0 for plotting, will hide bar later
    plotVals = [v if v is not None else 0 for v in vals]
    bars = ax.bar(x+(i-1)*w, plotVals, w, label=cni,
                  color=clr[cni], edgecolor='black', linewidth=0.5)
    for bar,val in zip(bars, vals):
        if val is not None:
            ax.text(bar.get_x()+bar.get_width()/2., bar.get_height()+1.5,
                    f'{val:.1f}%', ha='center', va='bottom', fontsize=7)
        else:
            bar.set_alpha(0.0)  # make invisible for N/A entries

ax.set_xlabel('Topology / Extension', fontsize=12)
ax.set_ylabel('Mean Sampled CPU %', fontsize=12)
ax.set_title('Mean Node-Container CPU % During Benchmark Windows', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scn_labels, fontsize=10)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(bottom=0, top=160)

plt.tight_layout()
plt.savefig('plots/1_cpu_overhead.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_cpu_overhead.png")
