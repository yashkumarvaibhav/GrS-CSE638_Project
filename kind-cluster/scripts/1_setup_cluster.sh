#!/usr/bin/env bash
# 1_setup_cluster.sh
# sets up a kind cluster and installs one of the CNI plugins on it
# usage: ./1_setup_cluster.sh <flannel|calico|cilium|cilium-kpr>
#
# NOTE: needs kind, kubectl and helm in ~/bin
# also needs docker obvsiously
#
# tested on ubuntu 22.04 with docker 26.x

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
export PATH="$HOME/bin:$PATH"

clusterName="cni-bench"
CNI="${1:?Usage: $0 <flannel|calico|cilium|cilium-kpr>}"

echo "================================================================"
echo "  Setting up kind cluster with CNI: $CNI"
echo "================================================================"

## step 1 - clean up old cluster if it exsits
kind delete cluster --name "$clusterName" 2>/dev/null || true

## step 2 - create the kind cluster (cni disbaled so we install our own)
echo "[1/5] Creating kind cluster..."
kind create cluster --name "$clusterName" \
  --config "$PROJECT_DIR/configs/1_kind-cluster.yaml" \
  --wait 60s || true   # might timeout without CNI, thats ok

# step 3: install cni-plugins binary on every node
# without this some CNIs dont work properly in kind
echo "[2/5] Installing CNI plugins on kind nodes..."
CNI_PLUGINS_TGZ="$HOME/cni-plugins-linux-amd64-v1.9.0.tgz"
if [[ ! -f "$CNI_PLUGINS_TGZ" ]]; then
  echo "  Downloading CNI plugins v1.9.0..."
  curl -Lo "$CNI_PLUGINS_TGZ" \
    https://github.com/containernetworking/plugins/releases/download/v1.9.0/cni-plugins-linux-amd64-v1.9.0.tgz
fi
for node in $(kind get nodes --name "$clusterName"); do
  echo "  Installing on $node..."
  docker cp "$CNI_PLUGINS_TGZ" "$node:/root/cni-plugins.tgz"
  docker exec "$node" tar xzf /root/cni-plugins.tgz -C /opt/cni/bin/
done

# step 4 - wait for nodes (might already be ready but just incase)
echo "[3/5] Waiting for nodes..."
kubectl wait --for=condition=Ready node/"${clusterName}-control-plane" --timeout=120s 2>/dev/null || true

### step 5: install the actual CNI plugin
echo "[4/5] Installing CNI: $CNI"

case "$CNI" in
  flannel)
    # flannel is simple - just apply the manifest directly
    kubectl apply -f https://github.com/flannel-io/flannel/releases/download/v0.26.1/kube-flannel.yml
    echo "Waiting for Flannel daemonset to be ready..."
    kubectl -n kube-flannel rollout status daemonset/kube-flannel-ds --timeout=180s
    ;;

  calico)
    # calico needs the tigera operator first, then we apply a custom Installation CR
    kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/tigera-operator.yaml 2>/dev/null || true
    # give it some time to come up
    sleep 10
    kubectl wait --for=condition=Available deployment/tigera-operator -n tigera-operator --timeout=120s 2>/dev/null || sleep 20

    # now apply the installation with VXLAN encapsulation
    # we disable BGP since its not needed in a kind setup
    cat <<'EOF' | kubectl apply -f -
apiVersion: operator.tigera.io/v1
kind: Installation
metadata:
  name: default
spec:
  calicoNetwork:
    bgp: Disabled
    ipPools:
    - cidr: 10.244.0.0/16
      encapsulation: VXLAN
      natOutgoing: Enabled
      nodeSelector: all()
---
apiVersion: operator.tigera.io/v1
kind: APIServer
metadata:
  name: default
spec: {}
EOF
    echo "Waiting for Calico to be ready..."
    # poll until calico-node DS shows up then wait for rollout
    for i in $(seq 1 60); do
      if kubectl -n calico-system get daemonset calico-node &>/dev/null; then
        kubectl -n calico-system rollout status daemonset/calico-node --timeout=180s && break
      fi
      echo "  Waiting for calico-node daemonset to appear... ($i/60)"
      sleep 5
    done
    ;;

  cilium)
    helm repo add cilium https://helm.cilium.io/ 2>/dev/null || true
    helm repo update cilium 2>/dev/null || true
    helm install cilium cilium/cilium --version 1.16.5 \
      --namespace kube-system \
      --values "$PROJECT_DIR/configs/cilium/1_cilium-values.yaml"
    echo "Waiting for Cilium to be ready..."
    kubectl -n kube-system rollout status daemonset/cilium --timeout=300s
    ;;

  cilium-kpr)
    # cilium with kube proxy replacment mode
    helm repo add cilium https://helm.cilium.io/ 2>/dev/null || true
    helm repo update cilium 2>/dev/null || true
    # need to remove kube-proxy first since cilium replaces it
    echo "Deleting kube-proxy (Cilium KPR replaces it)..."
    kubectl -n kube-system delete daemonset kube-proxy 2>/dev/null || true
    kubectl -n kube-system delete configmap kube-proxy 2>/dev/null || true
    helm install cilium cilium/cilium --version 1.16.5 \
      --namespace kube-system \
      --values "$PROJECT_DIR/configs/cilium/1_cilium-values-kpr.yaml"
    echo "Waiting for Cilium (kube-proxy replacement) to be ready..."
    kubectl -n kube-system rollout status daemonset/cilium --timeout=300s
    ;;

  *)
    echo "ERROR: Unknown CNI '$CNI'. Use flannel|calico|cilium|cilium-kpr"
    exit 1
    ;;
esac

# step 6: make sure all nodes are ready before we move on
echo "[5/5] Waiting for all nodes to be Ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=180s

# create the namepsace for benchmarks
kubectl create namespace benchmark 2>/dev/null || true

# pre-pull and load benchmark images so the tests dont waste time downloading
echo "Loading benchmark images into cluster..."
IPERF3_IMG="networkstatic/iperf3@sha256:07dcca91c0e47d82d83d91de8c3d46b840eef4180499456b4fa8d6dadb46b6c8"
NETPERF_IMG="networkstatic/netperf@sha256:f42eb5f94f31db407dd02cc65a4467e462e75d2619f7c8aad74dfebbdfae1a62"
FORTIO_IMG="fortio/fortio@sha256:7cd60e11e59d2c109c360c1d63c76e48294ebccf1b147cd4c5c32fccdad02d46"
BUSYBOX_IMG="busybox@sha256:b3255e7dfbcd10cb367af0d409747d511aeb66dfac98cf30e97e87e4207dd76f"
for img in "$IPERF3_IMG" "$NETPERF_IMG" "$FORTIO_IMG" "$BUSYBOX_IMG"; do
  docker pull "$img" 2>/dev/null || true
  kind load docker-image "$img" --name "$clusterName" 2>/dev/null || true
done

echo ""
echo "================================================================"
echo "  Cluster ready with CNI: $CNI"
echo "  Nodes:"
kubectl get nodes -o wide
echo "==============================================================="
