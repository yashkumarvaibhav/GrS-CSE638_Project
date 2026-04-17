# Performance Comparison of Kubernetes CNI Plugins

**Project P1 — CSE638: Graduate Systems (GRS), Winter 2026**
**Indraprastha Institute of Information Technology, Delhi (IIIT-Delhi)**
**Instructor: Dr. Rinku Shah**

---

## Overview

This project systematically benchmarks three major Kubernetes Container Network Interface (CNI) plugins — **Flannel**, **Calico**, and **Cilium** — to compare their networking performance, latency, CPU/memory overhead, and pod startup times under realistic microservice communication patterns. The observed behaviors are explained through the architectural differences of each CNI implementation.

We conduct benchmarks in **two independent environments** to provide a broader perspective:

| Environment | Setup | Team |
|---|---|---|
| **kind-cluster** (intra-node) | 3-node kind cluster on one AMD EPYC VM | Yash Kumar Vaibhav, Samyak Kr. Sharma |
| **bare-metal-cluster** (multi-machine) | 1 master + 2 worker bare-metal nodes (WiFi) | Nishit, Prakhar, Reehan |

Benchmarks use **iperf3** (throughput), **netperf** (latency), and **Fortio** (HTTP load testing) across multiple message sizes, concurrency levels, and scenarios including baseline, NetworkPolicy enforcement, WireGuard encryption, and Cilium's kube-proxy replacement (KPR) mode.

---

## Group Information

| Name | Roll No. | Email |
|---|---|---|
| Yash Kumar Vaibhav | MT25091 | yash25091@iiitd.ac.in |
| Nishit Jain | MT25004 | nishit25004@iiitd.ac.in |
| Prakhar Agarwal | MT25005 | prakhar25005@iiitd.ac.in |
| Reehan Sarmah | MT25036 | reehan25036@iiitd.ac.in |
| Samyak Kr. Sharma | MT25039 | samyak25039@iiitd.ac.in |

**GitHub:** [https://github.com/yashkumarvaibhav/GrS-CSE638_Project](https://github.com/yashkumarvaibhav/GrS-CSE638_Project)

---

## Repository Structure

```
.
├── README.md                         # This file
├── 1_GroupInfo.txt                   # Group metadata
├── 1_Project.txt                    # Project description
│
├── kind-cluster/                    # Intra-node benchmarking (kind cluster)
│   ├── 1_README.md                  #   Detailed README for kind-cluster setup
│   ├── 1_report-kind-cluster.pdf    #   Kind-cluster benchmarking report (PDF)
│   ├── 1_reproduce.sh               #   End-to-end reproduction script
│   ├── configs/                     #   Cluster and CNI configuration files
│   ├── benchmarks/                  #   Kubernetes manifests for benchmark tools
│   ├── scripts/                     #   Automation scripts
│   ├── data/                        #   Raw benchmark results (280+ CSVs + logs)
│   └── plots/                       #   Matplotlib scripts (.py) and figures (.png)
│
└── bare-metal-cluster/              # Multi-machine benchmarking (1 master + 2 workers)
    ├── 1_README.md                  #   Detailed README for bare-metal setup
    ├── 1_Report.pdf                 #   Bare-metal benchmarking report (PDF)
    ├── 1_reproduce.sh               #   Reproduction guide
    ├── configs/                     #   Cluster setup & node configuration (11 scripts)
    ├── install-cni-plugins/         #   CNI installation scripts (4 scripts)
    ├── helpers/                     #   Utility & maintenance scripts (10 scripts)
    ├── scripts/                     #   Benchmark automation (6 scripts + config)
    ├── benchmarks/                  #   Kubernetes manifests
    ├── data/                        #   Raw benchmark results (36 CSVs + aggregated JSON)
    └── plots/                       #   Matplotlib scripts (.py) and figures (.png)
```

---

## Benchmarks

### Metrics

| Metric | Tool | Description |
|---|---|---|
| **Throughput** | iperf3 | TCP bandwidth (Gbps) across message sizes (64 B, 4 KB, 1 MB) and concurrency (1, 16, 64 streams) |
| **Latency** | netperf | TCP\_RR transaction rate and mean latency (μs) |
| **HTTP Performance** | Fortio | HTTP queries per second (QPS) and latency percentiles (p50, p90, p99) |
| **CPU & Memory** | docker stats | Per-container resource consumption during benchmark windows |
| **Pod Startup Time** | kubectl | Time from pod creation to network reachability |

### Scenarios

| ID | Description | Path | Applicable CNIs |
|---|---|---|---|
| T1 | Same-node pod-to-pod | worker → worker (Pod IP) | All |
| T2 | Cross-node pod-to-pod | worker → worker2 (Pod IP) | All |
| T3 | Cross-node via Service | worker → worker2 (ClusterIP) | All |

### Extension Experiments

| ID | Extension | CNIs | Configuration |
|---|---|---|---|
| E1 | NetworkPolicy | Calico, Cilium | allow-all policy applied |
| E2 | WireGuard encryption | Calico, Cilium | Node-to-node encryption enabled |
| E3 | Kube-proxy replacement | Cilium only | `kubeProxyReplacement=true` |

### Test Matrix

**Kind Cluster:**
- 3 topologies × 3 payload sizes × 3 concurrency levels × 3 repetitions = **81 configs per CNI per tool** (729 total across 3 CNIs × 3 tools)
- Extensions: 4 KB payload, concurrency 16, 5 repetitions per configuration

**Bare-Metal Cluster:**
- 6 CNI configurations (VXLAN + native mode per CNI) × 3 benchmark tools × 5 runs = **90 benchmark executions**
- Netperf tests 3 payload sizes (1 B, 64 B, 256 B) per run
- All tests run cross-node (worker → worker)

---

## Quick Start

See the README inside each environment directory for detailed setup and reproduction instructions:

- **kind-cluster:** [`kind-cluster/1_README.md`](kind-cluster/1_README.md)
- **bare-metal-cluster:** [`bare-metal-cluster/1_README.md`](bare-metal-cluster/1_README.md)

---

## Key Findings

### Kind Cluster (intra-node)

1. **Cilium leads in throughput** — up to 63.98 Gbps same-node (eBPF fast-path advantage)
2. **Flannel delivers lowest latency** — 24.18 μs for 64 B cross-node TCP\_RR
3. **Calico trails in raw performance** but offers the richest policy ecosystem
4. **Pod startup times are equivalent** across all three CNIs (~3.2 s mean)
5. **NetworkPolicy overhead is minimal** — <3% throughput reduction on Calico and Cilium
6. **WireGuard encryption costs 12–18%** throughput on Calico; negligible on Cilium
7. **Cilium KPR eliminates kube-proxy overhead** — 5–8% throughput improvement over iptables-based routing
8. **Memory footprint**: Calico and Cilium consume 2.4–2.6× more than Flannel due to richer control planes

### Bare-Metal Cluster (multi-node, WiFi)

1. **Calico VXLAN achieves highest throughput** (0.119 Gbps), closely followed by Flannel VXLAN (0.118 Gbps)
2. **Cilium VXLAN is the slowest** at 0.058 Gbps — eBPF overhead outweighs benefits on WiFi
3. **Flannel delivers best TCP\_RR latency** — up to 214 trans/sec (256 B payload)
4. **Cilium VXLAN achieves best Fortio P50** (6.56 ms) — eBPF fast-path helps HTTP handling
5. **VXLAN vs. native routing** shows mixed results depending on CNI and bottleneck
6. **WiFi medium is the dominant bottleneck** — all CNIs converge to 0.06–0.12 Gbps range

---

## Academic Context

This project was developed for **CSE638: Graduate Systems (GRS), Winter 2026** at **IIIT-Delhi**, under the supervision of **Dr. Rinku Shah**. It is an open-ended systems research project (Project P1) investigating the performance characteristics and architectural trade-offs of production Kubernetes CNI plugins.

---

## License

All rights reserved. See [LICENSE](LICENSE) for details.
