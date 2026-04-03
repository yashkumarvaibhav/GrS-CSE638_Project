#!/bin/bash
set -euo pipefail
source 1_config.env

echo ">>> [1/5] Deploying Infrastructure for: $TEST_NAME"
echo ">>> Server Node: $SERVER_NODE | Client Node: $CLIENT_NODE"

cat <<YAML > benchmark-infrastructure.yaml
---
apiVersion: v1
kind: Pod
metadata: { name: iperf-server, labels: { app: throughput } }
spec:
  nodeName: ${SERVER_NODE}
  containers:
  - name: iperf
    image: networkstatic/iperf3
    command: ["iperf3", "-s"]
    ports: [{ containerPort: 5201 }]
---
apiVersion: v1
kind: Pod
metadata: { name: iperf-client, labels: { app: throughput } }
spec:
  nodeName: ${CLIENT_NODE}
  containers:
  - name: iperf
    image: networkstatic/iperf3
    command: ["sleep", "infinity"]
---
apiVersion: v1
kind: Pod
metadata: { name: netperf-server, labels: { app: latency } }
spec:
  nodeName: ${SERVER_NODE}
  containers:
  - name: netperf
    image: cilium/netperf
    command: ["netserver", "-D"]
    ports: [{ containerPort: 12865 }]
---
apiVersion: v1
kind: Pod
metadata: { name: netperf-client, labels: { app: latency } }
spec:
  nodeName: ${CLIENT_NODE}
  containers:
  - name: netperf
    image: cilium/netperf
    command: ["/bin/sh", "-c", "sleep infinity"]
---
apiVersion: v1
kind: Pod
metadata: { name: fortio-server, labels: { app: microservice } }
spec:
  nodeName: ${SERVER_NODE}
  containers:
  - name: fortio
    image: fortio/fortio
    command: ["fortio", "server"]
    ports: [{ containerPort: 8080 }]
---
apiVersion: v1
kind: Pod
metadata: { name: fortio-client, labels: { app: microservice } }
spec:
  nodeName: ${CLIENT_NODE}
  containers:
  - name: fortio
    image: fortio/fortio
    command: ["fortio", "server"]
YAML

kubectl delete -f benchmark-infrastructure.yaml --ignore-not-found=true 2>/dev/null || true

echo ">>> Waiting for old pods to terminate..."
kubectl wait --for=delete pod \
  -l 'app in (throughput,latency,microservice)' \
  --timeout=30s 2>/dev/null || true

kubectl apply -f benchmark-infrastructure.yaml

echo ">>> Waiting for all benchmark pods to be Ready..."
kubectl wait --for=condition=ready pod \
  -l 'app in (throughput,latency,microservice)' \
  --timeout=120s

echo ">>> Infrastructure Ready!"
echo ""
kubectl get pods -o wide | grep -E "iperf|netperf|fortio"