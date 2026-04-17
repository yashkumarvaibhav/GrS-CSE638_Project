# Performance Comparison of Kubernetes CNI Plugins — Bare-Metal Cluster

**Project P1 (Part B) — CSE638: Graduate Systems (GRS), Winter 2026**
**Indraprastha Institute of Information Technology, Delhi (IIIT-Delhi)**
**Instructor: Dr. Rinku Shah**

---

## Overview

This directory contains the **bare-metal multi-node** benchmarking component of the CNI performance comparison project. Experiments run on a physical 3-node Kubernetes cluster (1 control-plane + 2 workers) provisioned with `kubeadm`.

Six CNI configurations are benchmarked — **Flannel (VXLAN / Host-GW)**, **Calico (VXLAN / BGP)**, and **Cilium (VXLAN / Native Routing)** — comparing overlay vs. native routing performance on real network hardware.

Benchmarks are executed using **iperf3** (throughput), **netperf** (latency by payload size), and **Fortio** (HTTP load testing) across 5 runs per configuration.

**Group 1 members:**

| Name | Roll Number |
|---|---|
| Yash Kumar Vaibhav | MT25091 |
| Nishit Jain | MT25004 |
| Prakhar Agarwal | MT25005 |
| Reehan Sarmah | MT25036 |
| Samyak Kr. Sharma | MT25039 |

**GitHub:** [https://github.com/yashkumarvaibhav/GrS-CSE638_Project](https://github.com/yashkumarvaibhav/GrS-CSE638_Project)

---

## Repository Structure

```
bare-metal-cluster/
├── 1_Report.pdf                         # Final report (Part B)
├── 1_README.md                          # This file
├── 1_reproduce.sh                       # End-to-end reproduction guide
│
├── configs/                             # Cluster setup & node configuration
│   ├── 1_install_containerd.sh          #   Install containerd runtime
│   ├── 1_install_k8s.sh                 #   Install kubeadm/kubelet/kubectl v1.31
│   ├── 1_install_network_dependencies.sh #   conntrack, iptables legacy mode
│   ├── 1_init_control_plane.sh          #   kubeadm init (CIDR 10.244.0.0/16)
│   ├── 1_join_worker_nodes.sh           #   kubeadm join (placeholder tokens)
│   ├── 1_reset_node.sh                  #   Tear down / reset a node
│   ├── 1_semi_automation_setup.sh       #   Semi-automated cluster bootstrap
│   ├── 1_create_control_plane_team.sh   #   Control-plane init shortcut
│   ├── 1_delete_cluster.sh              #   Destroy cluster
│   ├── 1_node_reset_team.sh             #   Full node cleanup
│   └── 1_worker_join_placeholder.sh     #   Worker join helper
│
├── install-cni-plugins/                 # CNI plugin installation
│   ├── 1_install_flannel.sh             #   Flannel (VXLAN mode)
│   ├── 1_install_flannel_team.sh        #   Flannel (alternative install)
│   ├── 1_install_calico.sh              #   Calico (VXLAN / can switch to BGP)
│   └── 1_install_cilium.sh              #   Cilium (VXLAN / can switch to Native)
│
├── helpers/                             # Utility & maintenance scripts
│   ├── 1_switch_calico_mode.sh          #   Toggle Calico VXLAN ↔ BGP
│   ├── 1_calico_verify_mode.sh          #   Verify Calico's active mode
│   ├── 1_cilium_native_routing.sh       #   Switch Cilium to native routing
│   ├── 1_cni_safety_check.sh            #   Pre-benchmark CNI health check
│   ├── 1_pre_flight_check.sh            #   Cluster readiness verification
│   ├── 1_wipe_cni.sh                    #   Remove all CNI state
│   ├── 1_flannel_cleanup.sh             #   Flannel-specific cleanup
│   ├── 1_delete_calico.sh               #   Calico removal
│   ├── 1_wakeup.sh                      #   Wake up idle nodes
│   ├── 1_intranode_benchmark.sh         #   Intra-node baseline test
│   ├── 1_switch_cilium_mode.sh           #   Toggle Cilium VXLAN ↔ Underlay
│   └── 1_switch_flannel_mode.sh         #   Toggle Flannel VXLAN ↔ Host-GW
│
├── scripts/                             # Benchmark automation
│   ├── 1_benchmark.sh                   #   Main benchmark orchestrator
│   ├── 1_deploy_pods.sh                 #   Deploy server/client pods
│   ├── 1_throughput.sh                  #   iperf3 throughput test
│   ├── 1_latency.sh                     #   netperf latency test (TCP_RR)
│   ├── 1_microservices.sh               #   Fortio HTTP load test
│   ├── 1_cpu_overhead.sh                #   Node CPU/memory sampling
│   └── 1_config.env                     #   Test configuration variables
│
├── benchmarks/                          # Kubernetes manifests
│   └── 1_benchmark-infrastructure.yaml  #   Server pods (iperf3/netperf/fortio)
│
├── data/                                # Raw benchmark results (36 CSVs)
│   ├── 1_flannel_vxlan_throughput.csv
│   ├── 1_flannel_vxlan_latency_sizes.csv
│   ├── 1_flannel_vxlan_fortio.csv
│   ├── 1_flannel_hostgw_throughput.csv
│   ├── 1_flannel_hostgw_latency_sizes.csv
│   ├── 1_flannel_hostgw_fortio.csv
│   ├── 1_calico_vxlan_throughput.csv
│   ├── 1_calico_vxlan_latency_sizes.csv
│   ├── 1_calico_vxlan_fortio.csv
│   ├── 1_calico_bgp_throughput.csv
│   ├── 1_calico_bgp_latency_sizes.csv
│   ├── 1_calico_bgp_fortio.csv
│   ├── 1_cilium_vxlan_throughput.csv
│   ├── 1_cilium_vxlan_latency_sizes.csv
│   ├── 1_cilium_vxlan_fortio.csv
│   ├── 1_cilium_native_throughput.csv
│   ├── 1_cilium_native_latency_sizes.csv
│   ├── 1_cilium_native_fortio.csv
│   └── 1_aggregated_results.json        #   Aggregated means ± stdev
│
└── plots/                               # Matplotlib scripts (.py) and figures (.png)
    ├── 1_throughput_comparison.py / .png
    ├── 1_latency_comparison.py / .png
    ├── 1_fortio_comparison.py / .png
    └── 1_encapsulation_comparison.py / .png
```

---

## Benchmarks

### Tools & Metrics

| Tool | Metric | Measurement |
|---|---|---|
| **iperf3** | Throughput | TCP bandwidth (Gbps), 30 s per run |
| **netperf** | Latency | TCP\_RR transactions/sec, 3 payload sizes (1 B, 64 B, 256 B) |
| **Fortio** | HTTP Latency | P50, P99, Max latency (ms), 15 s per run |

### CNI Configurations (6 total)

| CNI | Mode | Description |
|---|---|---|
| Flannel VXLAN | Overlay | Default Flannel VXLAN encapsulation |
| Flannel Host-GW | Native | Direct host routing (same L2 subnet) |
| Calico VXLAN | Overlay | Calico with VXLAN encapsulation |
| Calico BGP | Native | Calico with BGP peering |
| Cilium VXLAN | Overlay | Cilium with VXLAN encapsulation |
| Cilium Native | Native | Cilium with native routing |

### Test Matrix

- **6 CNI configurations** × **3 benchmark tools** × **5 runs** = **90 benchmark executions**
- Netperf additionally tests 3 payload sizes (1 B, 64 B, 256 B) per run
- All tests run cross-node (worker-01 → worker-02)

---

## Environment

| Component | Details |
|---|---|
| **Nodes** | 3 physical laptops (1 control-plane + 2 workers) |
| **Network** | WiFi (shared LAN) |
| **OS** | Ubuntu 22.04 / 24.04 LTS |
| **Kubernetes** | v1.31 (kubeadm) |
| **Container Runtime** | containerd |
| **Pod subnet** | 10.244.0.0/16 |

> **Note:** Since nodes communicate over WiFi, throughput values (~0.06–0.12 Gbps) are significantly lower than wired or kind-cluster benchmarks. This is expected and highlights the overhead of real network hardware + wireless medium.

---

## Key Findings

1. **Calico VXLAN achieves highest throughput** (0.119 ± 0.015 Gbps), closely followed by Flannel VXLAN (0.118 ± 0.006 Gbps)
2. **Cilium VXLAN is the slowest** at 0.058 ± 0.001 Gbps — eBPF's overhead outweighs benefits on low-bandwidth WiFi links
3. **Flannel delivers best TCP\_RR latency** — up to 214 trans/sec (256 B), benefiting from its lightweight implementation
4. **Cilium Native has highest latency** (~111 trans/sec, lowest transaction rate) — native routing does not help when the bottleneck is the wireless medium
5. **Cilium VXLAN achieves best Fortio P50** (6.56 ms) — eBPF fast-path shines for HTTP request handling despite low throughput
6. **Flannel Host-GW has high P99 variance** (90.33 ms) — possibly due to WiFi interference or ARP fluctuations
7. **VXLAN vs. native routing** shows mixed results: Flannel VXLAN > Host-GW, Calico VXLAN ≈ BGP, Cilium Native > VXLAN

---

## Quick Start

### Cluster Setup

```bash
# 1. On ALL nodes: install container runtime and Kubernetes
bash configs/1_install_containerd.sh
bash configs/1_install_k8s.sh
bash configs/1_install_network_dependencies.sh

# 2. On control-plane: initialize cluster
bash configs/1_init_control_plane.sh

# 3. On workers: join the cluster (use token from step 2)
sudo kubeadm join <CONTROL_PLANE_IP>:6443 --token <TOKEN> --discovery-token-ca-cert-hash sha256:<HASH>

# 4. On control-plane: install a CNI plugin
bash install-cni-plugins/1_install_flannel.sh   # or calico / cilium
```

### Run Benchmarks

```bash
# Edit config to set CNI name and node labels
vim scripts/1_config.env

# Deploy benchmark pods and run all tests
bash scripts/1_benchmark.sh
```

### Generate Plots

```bash
cd plots/
for f in 1_*.py; do python3 "$f"; done
```

---

## Output

- **CSV data** in `data/` — 36 raw benchmark CSV files across 6 CNI configurations
- **Aggregated JSON** in `data/1_aggregated_results.json` — means and standard deviations
- **Plots** in `plots/` — 4 matplotlib scripts + 4 PNG figures
- **Report** — `1_report-bare-metal-cluster.pdf`

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| kubeadm | v1.31+ | Cluster provisioning |
| kubectl | v1.31+ | Cluster interaction |
| containerd | 1.7+ | Container runtime |
| iperf3 | 3.x | Throughput measurement |
| netperf | 2.7+ | Latency measurement |
| Fortio | 1.x | HTTP load testing |
| Python 3 | 3.10+ | Plot generation |
| matplotlib | 3.5+ | Plotting library |
| numpy | — | Numerical computation |

---

## License

This repository is part of an academic course project for CSE638 at IIIT-Delhi. Please cite appropriately if referencing this work.
