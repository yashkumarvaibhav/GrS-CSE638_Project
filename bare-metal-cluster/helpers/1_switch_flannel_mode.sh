#!/bin/bash
set -euo pipefail

# Usage:
#   bash helpers/1_switch_flannel_mode.sh vxlan
#   bash helpers/1_switch_flannel_mode.sh host-gw

MODE="${1:-}"
if [[ "$MODE" != "vxlan" && "$MODE" != "host-gw" ]]; then
  echo "Usage: bash helpers/1_switch_flannel_mode.sh [vxlan|host-gw]"
  exit 1
fi

if [[ "$MODE" == "vxlan" ]]; then
  BACKEND="vxlan"
else
  BACKEND="host-gw"
fi

echo ">>> [1/3] Reading kube-flannel ConfigMap..."
NET_CONF=$(kubectl -n kube-flannel get cm kube-flannel-cfg -o jsonpath='{.data.net-conf\.json}')
if [[ -z "$NET_CONF" ]]; then
  echo "FAIL: unable to read kube-flannel-cfg net-conf.json"
  exit 2
fi

echo ">>> [2/3] Updating backend Type to ${BACKEND}..."
UPDATED=$(echo "$NET_CONF" | sed -E "s/\"Type\"[[:space:]]*:[[:space:]]*\"[^\"]+\"/\"Type\": \"${BACKEND}\"/")
kubectl -n kube-flannel patch cm kube-flannel-cfg --type merge -p "{\"data\":{\"net-conf.json\":$(printf '%s' "$UPDATED" | jq -Rs .)}}"

echo ">>> [3/3] Restarting flannel daemonset..."
kubectl -n kube-flannel rollout restart ds/kube-flannel-ds
kubectl -n kube-flannel rollout status ds/kube-flannel-ds --timeout=300s

echo "============================================="
echo "Flannel mode switch complete: ${MODE}"
echo "============================================="
kubectl -n kube-flannel get cm kube-flannel-cfg -o jsonpath='{.data.net-conf\.json}' | jq -r '.Backend.Type'
