#!/bin/bash
# This script should be run on the worker node to join it to the cluster.
set -e

echo "Joining worker node to Kubernetes cluster..."

# Note: The token and discovery-token-ca-cert-hash values should be the ones that are printed after the control plane initialization.
# Run `kubeadm token create --print-join-command` on the control-plane node to generate fresh values.
sudo kubeadm join <CONTROL_PLANE_IP>:6443 \
--token <TOKEN> \
--discovery-token-ca-cert-hash sha256:<HASH>

echo "Worker node successfully joined the cluster."