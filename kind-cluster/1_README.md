# Performance Comparison of Kubernetes CNI Plugins — Kind Cluster (Intra-Node)

**Project P1 — CSE638: Graduate Systems (GRS), Winter 2026**
**Indraprastha Institute of Information Technology, Delhi (IIIT-Delhi)**
**Instructor: Dr. Rinku Shah**

---

## Overview

This directory contains the **kind cluster (intra-node)** benchmarking component of the CNI performance comparison project. All experiments here run on a single machine using `kind` (Kubernetes IN Docker) to emulate a multi-node cluster.

Three CNI plugins are benchmarked — **Flannel**, **Calico**, and **Cilium** — comparing networking performance, latency, CPU/memory overhead, and pod startup times under realistic microservice communication patterns.

Benchmarks are executed using **iperf3** (throughput), **netperf** (latency), and **Fortio** (HTTP load testing) across multiple message sizes, concurrency levels, and scenarios including baseline, NetworkPolicy enforcement, WireGuard encryption, and Cilium's kube-proxy replacement (KPR) mode.

**Author:** Yash Kumar Vaibhav (MT25091, yash25091@iiitd.ac.in)
**GitHub:** [https://github.com/yashkumarvaibhav/GrS-CSE638_Project](https://github.com/yashkumarvaibhav/GrS-CSE638_Project)

---

## Repository Structure

```
.
├── 1_report-kind-cluster.pdf     # Kind cluster benchmarking report (PDF)
├── 1_reproduce.sh                # End-to-end reproduction script (all CNIs)
├── 1_README.md                   # This file
│
├── configs/                      # Cluster and CNI configuration files
│   ├── 1_kind-cluster.yaml       #   kind cluster spec (1 control-plane + 2 workers)
│   ├── 1_network-policy-allow-all.yaml  #   NetworkPolicy for extension experiments
│   └── cilium/                   #   Helm values for Cilium (baseline + KPR)
│       ├── 1_cilium-values.yaml
│       └── 1_cilium-values-kpr.yaml
│
├── benchmarks/                   # Kubernetes manifests for benchmark tools
│   ├── iperf3/                   #   iperf3 server pod + ClusterIP service
│   │   ├── 1_iperf3-server.yaml
│   │   └── 1_iperf3-service.yaml
│   ├── netperf/                  #   netperf server pod + ClusterIP service
│   │   ├── 1_netperf-server.yaml
│   │   └── 1_netperf-service.yaml
│   └── fortio/                   #   Fortio server pod + ClusterIP service
│       ├── 1_fortio-server.yaml
│       └── 1_fortio-service.yaml
│
├── scripts/                      # Automation scripts
│   ├── 1_setup_cluster.sh        #   Create kind cluster + install CNI
│   ├── 1_teardown.sh             #   Delete kind cluster
│   ├── 1_fast_benchmark.py       #   Benchmark runner (full test matrix)
│   └── 1_aggregate_data.py       #   Aggregate CSVs, compute means/stdev
│
├── data/                         # Raw benchmark results
│   ├── 1_<cni>_iperf3.csv        #   iperf3 throughput results per CNI
│   ├── 1_<cni>_netperf.csv       #   netperf latency results per CNI
│   ├── 1_<cni>_fortio.csv        #   Fortio HTTP QPS results per CNI
│   ├── 1_<cni>_pod_startup.csv   #   Pod network reachability times
│   ├── 1_<cni>_stats_*.csv       #   Per-run resource utilization snapshots
│   ├── 1_<cni>_e{1,2,3}.log      #   Extension experiment run logs
│   └── 1_aggregated_results.json  #   Aggregated summary (mean ± stdev)
│
└── plots/                        # Matplotlib scripts (.py) and generated figures (.png)
    ├── 1_throughput_comparison.py / .png
    ├── 1_latency_comparison.py / .png
    ├── 1_latency_vs_msgsize.py / .png
    ├── 1_throughput_vs_concurrency.py / .png
    ├── 1_cpu_overhead.py / .png
    ├── 1_cpu_overhead_baseline.py / .png
    ├── 1_memory_overhead.py / .png
    ├── 1_memory_overhead_baseline.py / .png
    ├── 1_pod_startup_time.py / .png
    └── 1_network_policy_overhead.py / .png
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

- **Baseline:** 3 topologies × 3 payload sizes × 3 concurrency levels × 3 repetitions = **81 configs per CNI per tool** (729 total across 3 CNIs × 3 tools)
- **Extensions:** 4 KB payload, concurrency 16, 5 repetitions per configuration

---

## Environment

All benchmarks ran on a **single VM** using `kind` to simulate a 3-node Kubernetes cluster (intra-node):

| Component | Details |
|---|---|
| **CPU** | AMD EPYC 7713 (shared VM) |
| **OS** | Ubuntu 22.04 LTS |
| **Docker** | 26.1.3 |
| **Kubernetes** | v1.31.2 (via kind) |
| **Cluster** | 1 control-plane + 2 workers |
| **Pod subnet** | 10.244.0.0/16 |
| **Service subnet** | 10.96.0.0/16 |

Since all kind nodes are Docker containers on the same host, "cross-node" traffic (T2/T3) traverses Docker's bridge network rather than a physical NIC. This is an important caveat vs. bare-metal multi-node benchmarks.

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker | 20.10+ | Container runtime for kind nodes |
| kind | v0.20+ | Local Kubernetes cluster provisioning |
| kubectl | v1.31+ | Cluster interaction |
| Helm | v3.x | Cilium/Calico installation |
| Python 3 | 3.10+ | Benchmark automation and plotting |
| matplotlib | 3.5+ | Plot generation |
| numpy | — | Numerical computation |
| pandas | — | Data manipulation |

Additionally, download the CNI reference plugins tarball:

```bash
curl -Lo ~/cni-plugins-linux-amd64-v1.9.0.tgz \
  https://github.com/containernetworking/plugins/releases/download/v1.9.0/cni-plugins-linux-amd64-v1.9.0.tgz
```

Ensure `kind`, `kubectl`, `helm` are on your `PATH` (e.g., in `~/bin/`).

---

## Quick Start

### Full Reproduction (~8–10 hours)

```bash
export PATH="$HOME/bin:$PATH"
bash 1_reproduce.sh
```

This runs all benchmarks for Flannel, Calico, and Cilium (including extensions), aggregates data, and generates all plots.

### Step-by-Step (single CNI)

```bash
# 1. Create cluster with a specific CNI (flannel | calico | cilium | cilium-kpr)
bash scripts/1_setup_cluster.sh flannel

# 2. Run benchmarks
python3 scripts/1_fast_benchmark.py flannel baseline

# 3. Tear down cluster
bash scripts/1_teardown.sh

# 4. Aggregate data and generate plots
python3 scripts/1_aggregate_data.py
for f in plots/1_*.py; do python3 "$f"; done
```

---

## Key Findings (Kind Cluster)

1. **Cilium leads in throughput** — up to 63.98 Gbps same-node (eBPF fast-path advantage)
2. **Flannel delivers lowest latency** — 24.18 μs for 64 B cross-node TCP\_RR
3. **Calico trails in raw performance** but offers the richest policy ecosystem
4. **Pod startup times are equivalent** across all three CNIs (~3.2 s mean)
5. **NetworkPolicy overhead varies by metric** — <3% Fortio QPS reduction, but Calico iperf3 throughput dropped ~45% (high variability, CV>55%); Cilium showed anomalous gains
6. **WireGuard encryption costs 12–18%** throughput on Calico; negligible on Cilium
7. **Cilium KPR eliminates kube-proxy overhead** — 5–8% throughput improvement over iptables-based routing
8. **Memory footprint**: Calico and Cilium consume 2.4–2.6× more than Flannel due to richer control planes

> **Note:** These results are specific to a kind (intra-node) environment. Performance characteristics may differ on bare-metal multi-node clusters with real network hardware.

---

## Output

- **CSV data** in `data/` — 280 raw per-run CSV files across all CNIs and scenarios
- **Aggregated JSON** in `data/1_aggregated_results.json` — means and standard deviations
- **Plots** in `plots/` — 10 matplotlib scripts + 10 PNG figures
- **Report** — `1_report-kind-cluster.pdf`

---

## License

This repository is part of an academic course project for CSE638 at IIIT-Delhi. Please cite appropriately if referencing this work.
