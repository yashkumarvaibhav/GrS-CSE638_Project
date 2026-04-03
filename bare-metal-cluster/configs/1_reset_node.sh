#!/bin/bash

set -e

echo "Resetting Kubernetes node"

sudo kubeadm reset -f || true

sudo systemctl stop kubelet || true

sudo apt-get purge -y kubeadm kubectl kubelet kubernetes-cni || true

sudo apt-get autoremove -y

sudo rm -rf ~/.kube
sudo rm -rf /etc/kubernetes
sudo rm -rf /var/lib/etcd

echo "Node reset complete"