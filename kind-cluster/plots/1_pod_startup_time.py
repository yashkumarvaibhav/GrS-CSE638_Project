#!/usr/bin/env python3
# pod startup time barchart with error bars
# mesures how long it takes for a pod to become reachable on each CNI
# (this was suprisingly consistent across runs which is nice)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# pod startup seconds - mean and std from 10 iterations each
cniNames = ["Flannel", "Calico", "Cilium"]
mu  = [3.229, 3.128, 3.231]
sig = [0.863, 0.544, 0.868]
bar_colors = ["#4ECDC4", "#FF6B6B", "#45B7D1"]

fig, ax = plt.subplots(figsize=(8, 6))

bars = ax.bar(cniNames, mu, yerr=sig, width=0.45, color=bar_colors,
              edgecolor='black', linewidth=0.5, capsize=8, error_kw={'linewidth':1.5})

# put the mean +/- std text above each bar
for bar, m, s in zip(bars, mu, sig):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + s + 0.08,
            f'{m:.3f} +/- {s:.3f}', ha='center', va='bottom', fontsize=9)

ax.set_xlabel('CNI Plugin', fontsize=12)
ax.set_ylabel('Pod Startup Time (s)', fontsize=12)
ax.set_title('Pod Network Reachability Time', fontsize=14, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
ax.set_ylim(0, 5.5)

plt.tight_layout()
plt.savefig('plots/1_pod_startup_time.png', dpi=150, bbox_inches='tight')
print("Saved: plots/1_pod_startup_time.png")
