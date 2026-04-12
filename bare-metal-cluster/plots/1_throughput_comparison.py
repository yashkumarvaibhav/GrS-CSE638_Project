#!/usr/bin/env python3
"""Throughput comparison across CNI plugins (bare-metal, cross-node)."""
import matplotlib.pyplot as plt
import numpy as np

# Hardcoded from data/1_*_throughput.csv (mean ± stdev, 4-5 runs each)
cnis = ['Flannel\nVXLAN', 'Flannel\nHost-GW', 'Calico\nVXLAN', 'Calico\nBGP', 'Cilium\nVXLAN', 'Cilium\nNative']
means = [0.1178, 0.0884, 0.1186, 0.1161, 0.0576, 0.1021]  # Gbps
stdevs = [0.0061, 0.0485, 0.0147, 0.0089, 0.0012, 0.0091]

colors = ['#4e79a7', '#59a14f', '#f28e2b', '#e15759', '#76b7b2', '#b07aa1']

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(cnis, means, yerr=stdevs, capsize=5, color=colors, edgecolor='black', linewidth=0.5)
ax.set_ylabel('Throughput (Gbps)')
ax.set_title('Cross-Node Throughput Comparison — Bare-Metal Cluster')
ax.set_ylim(0, max(means) * 1.35)

for bar, m in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
            f'{m:.3f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig('1_throughput_comparison.png', dpi=150)
print("Saved 1_throughput_comparison.png")
