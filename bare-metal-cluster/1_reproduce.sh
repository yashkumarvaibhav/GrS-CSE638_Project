#!/usr/bin/env bash
#
# 1_reproduce.sh — Bare-Metal CNI Benchmarking Reproduction Guide
# Group 1, CSE638, IIIT-Delhi
#
# This script documents the steps to reproduce the bare-metal benchmarking
# results. Because it requires a physical 3-node cluster, it cannot be run
# fully automatically on a single machine. Each section can be run
# independently on the appropriate node.
#
set -euo pipefail

cat <<'EOF'
==============================================================
  Bare-Metal CNI Benchmark — Reproduction Steps
  Group 1  |  CSE638: Graduate Systems  |  IIIT-Delhi
==============================================================

PREREQUISITES
  • 3 Linux machines (Ubuntu 22.04/24.04) on the same LAN
  • sudo access on all nodes
  • kubeadm, kubelet, kubectl v1.31+
  • containerd 1.7+
  • iperf3, netperf, fortio installed on worker nodes
  • Python 3.10+ with matplotlib, numpy for plot generation

--------------------------------------------------------------
STEP 1: NODE SETUP (run on ALL 3 nodes)
--------------------------------------------------------------
  bash configs/1_install_containerd.sh
  bash configs/1_install_k8s.sh
  bash configs/1_install_network_dependencies.sh

--------------------------------------------------------------
STEP 2: CONTROL PLANE (run on control-plane node)
--------------------------------------------------------------
  bash configs/1_init_control_plane.sh
  # Note the 'kubeadm join' command printed at the end

--------------------------------------------------------------
STEP 3: JOIN WORKERS (run on each worker node)
--------------------------------------------------------------
  sudo kubeadm join <CONTROL_PLANE_IP>:6443 \
    --token <TOKEN> \
    --discovery-token-ca-cert-hash sha256:<HASH>

--------------------------------------------------------------
STEP 4: INSTALL CNI & RUN BENCHMARKS
--------------------------------------------------------------
For each of the 6 configurations:

  a) Flannel VXLAN
     bash install-cni-plugins/1_install_flannel.sh
     # Edit scripts/1_config.env: TEST_NAME="flannel_vxlan"
     bash scripts/1_benchmark.sh

  b) Flannel Host-GW
     # Modify Flannel configmap: Type → host-gw
     # Edit scripts/1_config.env: TEST_NAME="flannel_hostgw"
     bash scripts/1_benchmark.sh

  c) Calico VXLAN
     bash helpers/1_wipe_cni.sh
     bash install-cni-plugins/1_install_calico.sh
     # Edit scripts/1_config.env: TEST_NAME="calico_vxlan"
     bash scripts/1_benchmark.sh

  d) Calico BGP
     bash helpers/1_switch_calico_mode.sh
     # Edit scripts/1_config.env: TEST_NAME="calico_bgp"
     bash scripts/1_benchmark.sh

  e) Cilium VXLAN
     bash helpers/1_wipe_cni.sh
     bash install-cni-plugins/1_install_cilium.sh
     # Edit scripts/1_config.env: TEST_NAME="cilium_vxlan"
     bash scripts/1_benchmark.sh

  f) Cilium Native
     bash helpers/1_cilium_native_routing.sh
     # Edit scripts/1_config.env: TEST_NAME="cilium_native"
     bash scripts/1_benchmark.sh

--------------------------------------------------------------
STEP 5: GENERATE PLOTS
--------------------------------------------------------------
  cd plots/
  for f in 1_*.py; do python3 "$f"; done

  Output: 4 PNG figures in plots/

--------------------------------------------------------------
STEP 6: CLUSTER TEARDOWN
--------------------------------------------------------------
  bash configs/1_delete_cluster.sh
  # Or on each node: bash configs/1_reset_node.sh

==============================================================
EOF
