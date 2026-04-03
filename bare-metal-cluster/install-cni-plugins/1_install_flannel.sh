#!/bin/bash
# To be done after initializing the control plane and joining worker nodes, this script installs the Flannel CNI plugin for networking.
set -e

echo "Installing Flannel CNI plugin..."

kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
echo "Flannel CNI plugin installation initiated. Waiting for pods to be ready..."
sleep 10

# This will show whether the nodes are ready or not.
kubectl get nodes

echo "Flannel installation complete"