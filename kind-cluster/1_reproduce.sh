#!/usr/bin/env bash
# 1_reproduce.sh
# end to end reproduction script for the CNI performance comparsion
# runs all benchmarks for all CNIs - takes like 8-10 hours total
#
# prereqs:
#   docker (user in docker group), ~/bin/{kind,kubectl,helm,tectonic}
#   ~/cni-plugins-linux-amd64-v1.9.0.tgz downloaded
#   python 3.10+ with matplotlib numpy pandas
#
# just run: export PATH="$HOME/bin:$PATH" && bash 1_reproduce.sh

set -euo pipefail

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJ_DIR"

###### PHASE 1 - FLANNEL ######
echo "=== Phase 1: Flannel ==="
bash scripts/1_setup_cluster.sh flannel
python3 scripts/1_fast_benchmark.py flannel baseline
bash scripts/1_teardown.sh

###### PHASE 2 - CALICO (baseline + extensions) ######
echo "=== Phase 2: Calico Baseline ==="
bash scripts/1_setup_cluster.sh calico
python3 scripts/1_fast_benchmark.py calico baseline

echo "=== Phase 2a: Calico E1 (NetworkPolicy) ==="
kubectl create namespace benchmark 2>/dev/null || true
kubectl apply -f configs/1_network-policy-allow-all.yaml
sleep 5
python3 scripts/1_fast_benchmark.py calico policy
kubectl delete -f configs/1_network-policy-allow-all.yaml 2>/dev/null || true

echo "=== Phase 2b: Calico E2 (WireGuard) ==="
# enable wireguard via felixconfiguration patch
kubectl patch felixconfiguration default --type='merge' \
  -p '{"spec":{"wireguardEnabled":true}}'
sleep 30
kubectl -n calico-system rollout status daemonset/calico-node --timeout=120s
python3 scripts/1_fast_benchmark.py calico wireguard

bash scripts/1_teardown.sh

###### PHASE 3 - CILIUM (baseline + extensions) ######
echo "=== Phase 3: Cilium Baseline ==="
bash scripts/1_setup_cluster.sh cilium
python3 scripts/1_fast_benchmark.py cilium baseline

echo "=== Phase 3a: Cilium E1 (NetworkPolicy) ==="
kubectl create namespace benchmark 2>/dev/null || true
kubectl apply -f configs/1_network-policy-allow-all.yaml
sleep 5
python3 scripts/1_fast_benchmark.py cilium policy
kubectl delete -f configs/1_network-policy-allow-all.yaml 2>/dev/null || true

echo "=== Phase 3b: Cilium E2 (WireGuard) ==="
# enable encryption on existing cilium install
helm upgrade cilium cilium/cilium \
  --namespace kube-system \
  --reuse-values \
  --set encryption.enabled=true \
  --set encryption.type=wireguard \
  --wait --timeout 120s
sleep 30
python3 scripts/1_fast_benchmark.py cilium wireguard

bash scripts/1_teardown.sh

echo "=== Phase 3c: Cilium E3 (KPR) ==="
bash scripts/1_setup_cluster.sh cilium-kpr
python3 scripts/1_fast_benchmark.py cilium kpr

bash scripts/1_teardown.sh

###### PHASE 4 - aggregate data and make plots ######
echo "=== Phase 4: Data Processing ==="
python3 scripts/1_aggregate_data.py
for f in plots/1_*.py; do python3 "$f"; done

echo "=== Done. Data in data/, plots in plots/ ==="
