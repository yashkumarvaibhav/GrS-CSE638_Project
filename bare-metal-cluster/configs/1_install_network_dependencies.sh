#!/bin/bash

# To be run on all nodes to install Kubernetes networking dependencies.
set -e

echo "Installing Kubernetes networking dependencies..."

sudo apt update

sudo apt install -y \
conntrack \
iptables \
arptables \
ebtables

echo "Switching iptables to legacy mode (recommended for Kubernetes)"

sudo update-alternatives --set iptables /usr/sbin/iptables-legacy
sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-legacy

echo "Networking dependencies installed successfully"