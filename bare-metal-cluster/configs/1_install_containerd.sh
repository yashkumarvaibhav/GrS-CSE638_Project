#!/bin/bash
# To be run on all nodes to install containerd.
set -e

sudo apt update

echo "Installing containerd"

sudo apt install -y containerd
sudo mkdir -p /etc/containerd

containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

sudo systemctl restart containerd
sudo systemctl enable containerd

echo "containerd installed"