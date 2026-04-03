#!/bin/bash
set -euo pipefail

# Usage:
#   bash helpers/1_switch_cilium_mode.sh vxlan
#   bash helpers/1_switch_cilium_mode.sh native

MODE="${1:-}"
if [[ "$MODE" != "vxlan" && "$MODE" != "native" ]]; then
  echo "Usage: bash helpers/1_switch_cilium_mode.sh [vxlan|native]"
  exit 1
fi

if ! command -v cilium >/dev/null 2>&1; then
  echo "FAIL: cilium CLI not found in PATH"
  exit 2
fi

echo ">>> [1/3] Applying Cilium mode ${MODE} via Helm values (cilium upgrade)..."
if [[ "$MODE" == "native" ]]; then
  cilium upgrade \
    --set routingMode=native \
    --set tunnelProtocol=none \
    --set autoDirectNodeRoutes=true \
    --set ipv4NativeRoutingCIDR=10.244.0.0/16
else
  cilium upgrade \
    --set routingMode=tunnel \
    --set tunnelProtocol=vxlan \
    --set autoDirectNodeRoutes=false
fi

echo ">>> [2/3] Restarting cilium daemonset..."
kubectl -n kube-system rollout restart ds/cilium
kubectl -n kube-system rollout status ds/cilium --timeout=300s

echo ">>> [3/3] Verifying mode from cilium-config ConfigMap..."
ROUTING_MODE=$(kubectl get cm cilium-config -n kube-system -o jsonpath='{.data.routing-mode}')
TUNNEL_PROTOCOL=$(kubectl get cm cilium-config -n kube-system -o jsonpath='{.data.tunnel-protocol}')

echo "Configured routing-mode: ${ROUTING_MODE:-<empty>}"
echo "Configured tunnel-protocol: ${TUNNEL_PROTOCOL:-<empty>}"

echo "============================================="
echo "Cilium mode switch complete: ${MODE}"
echo "============================================="
