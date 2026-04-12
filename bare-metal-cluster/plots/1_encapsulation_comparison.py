#!/usr/bin/env python3
"""Encapsulation mode comparison: VXLAN vs native routing (HostGW/BGP/Native)."""
import matplotlib.pyplot as plt
import numpy as np

cnis      = ['Flannel', 'Calico', 'Cilium']
vxlan     = [0.1178, 0.1186, 0.0576]  # Gbps
native    = [0.0884, 0.1161, 0.1021]  # Host-GW / BGP / Native
vxlan_err = [0.0061, 0.0147, 0.0012]
native_err= [0.0485, 0.0089, 0.0091]

x = np.arange(len(cnis))
width = 0.30
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x - width/2, vxlan, width, yerr=vxlan_err, capsize=5,
       label='VXLAN (Overlay)', color='#4e79a7', edgecolor='black', linewidth=0.5)
ax.bar(x + width/2, native, width, yerr=native_err, capsize=5,
       label='Native Routing', color='#f28e2b', edgecolor='black', linewidth=0.5)

ax.set_ylabel('Throughput (Gbps)')
ax.set_title('VXLAN vs Native Routing — Bare-Metal Cluster')
ax.set_xticks(x)
ax.set_xticklabels(cnis)
ax.set_ylim(0, 0.18)
ax.legend()
plt.tight_layout()
plt.savefig('1_encapsulation_comparison.png', dpi=150)
print("Saved 1_encapsulation_comparison.png")
