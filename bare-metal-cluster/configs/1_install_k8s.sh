#!/bin/bash
# To be run on all nodes to install Kubernetes tools and dependencies.
set -e

echo "Disabling swap"

sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

echo "Loading kernel modules"

sudo modprobe overlay
sudo modprobe br_netfilter

echo "Setting sysctl params"

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system

echo "Installing Kubernetes repository"

sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | \
sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /" | \
sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update

sudo apt install -y kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl

echo "Kubernetes tools installed"