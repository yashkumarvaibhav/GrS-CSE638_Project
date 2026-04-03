#!/bin/bash
# Note: This script should be run on the control plane node to initialize it.
set -e

echo "Initializing control plane"

sudo kubeadm init \
--pod-network-cidr=10.244.0.0/16

echo "Setting up kubectl"

mkdir -p $HOME/.kube

sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config

sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo "Control plane initialized"