#!/usr/bin/env bash
# teardown script - just deletes the kind cluster
# pretty straightforward honestly
set -euo pipefail
export PATH="$HOME/bin:$PATH"

clusterName="cni-bench"

echo "Tearing down kind cluster: $clusterName"
kind delete cluster --name "$clusterName"
echo "Done, cluster deleted."
