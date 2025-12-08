#!/bin/bash

# Network Latency Injection Script
# This script injects network latency between pods or services
# Used for chaos engineering and testing the Self-Healing Agent's response to network issues

set -e

NAMESPACE="${NAMESPACE:-self-healing-cloud}"
LATENCY="${LATENCY:-100ms}"  # Default 100ms latency
DURATION="${DURATION:-300}"  # Default 5 minutes
SOURCE_SERVICE="${SOURCE_SERVICE:-}"
TARGET_SERVICE="${TARGET_SERVICE:-}"

echo "=========================================="
echo "Network Latency Injection - Chaos Engineering"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Latency: $LATENCY"
echo "Duration: $DURATION seconds"
echo "Source Service: ${SOURCE_SERVICE:-all}"
echo "Target Service: ${TARGET_SERVICE:-all}"
echo ""

# Check if chaos-mesh or similar tool is available
check_chaos_tools() {
    if kubectl get crd networkchaos.chaos-mesh.org &>/dev/null; then
        echo "✅ Chaos Mesh detected - using NetworkChaos CRD"
        return 0
    elif kubectl get crd networkpolicies.networking.k8s.io &>/dev/null; then
        echo "⚠️  Using basic network policies (limited functionality)"
        return 1
    else
        echo "⚠️  No chaos engineering tools detected"
        echo "   This script will use basic iptables manipulation (requires privileged access)"
        return 2
    fi
}

# Function to inject latency using Chaos Mesh
inject_latency_chaos_mesh() {
    local chaos_name="network-latency-$(date +%s)"
    
    echo "Creating NetworkChaos resource..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: $chaos_name
  namespace: $NAMESPACE
spec:
  action: delay
  mode: all
  selector:
    namespaces:
      - $NAMESPACE
    labelSelectors:
      ${SOURCE_SERVICE:+app: $SOURCE_SERVICE}
  delay:
    latency: "$LATENCY"
    correlation: "100"
    jitter: "0ms"
  duration: "${DURATION}s"
EOF

    echo ""
    echo "✅ NetworkChaos created: $chaos_name"
    echo ""
    echo "Latency injection active for $DURATION seconds"
    echo "To remove early: kubectl delete networkchaos $chaos_name -n $NAMESPACE"
}

# Function to inject latency using iptables (requires privileged pod)
inject_latency_iptables() {
    local pod_name="network-latency-$(date +%s)"
    
    echo "Creating privileged pod for iptables manipulation..."
    echo "⚠️  This requires cluster admin privileges"
    
    # This is a simplified approach - in practice, you'd use a tool like tc (traffic control)
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $pod_name
  namespace: $NAMESPACE
  labels:
    app: network-latency-injector
    chaos-engineering: "true"
spec:
  restartPolicy: Never
  containers:
  - name: latency-injector
    image: nicolaka/netshoot
    command: ["/bin/sh"]
    args: ["-c", "echo 'Network latency injection requires tc (traffic control) tool. Install chaos-mesh for better results.' && sleep ${DURATION}"]
    securityContext:
      privileged: true
    resources:
      requests:
        cpu: "50m"
        memory: "64Mi"
      limits:
        cpu: "100m"
        memory: "128Mi"
EOF

    echo ""
    echo "⚠️  Basic latency injector pod created"
    echo "   For proper network latency injection, install Chaos Mesh or use tc directly"
}

# Function to create network policy that simulates latency
create_latency_simulation() {
    echo "Creating network policy to simulate network issues..."
    
    # This is a workaround - network policies don't add latency but can block traffic
    # For actual latency, use Chaos Mesh or tc
    
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: latency-simulation-$(date +%s)
  namespace: $NAMESPACE
spec:
  podSelector:
    matchLabels:
      ${SOURCE_SERVICE:+app: $SOURCE_SERVICE}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          ${TARGET_SERVICE:+app: $TARGET_SERVICE}
  egress:
  - to:
    - podSelector:
        matchLabels:
          ${TARGET_SERVICE:+app: $TARGET_SERVICE}
EOF

    echo "⚠️  Network policy created (blocks traffic, doesn't add latency)"
    echo "   For actual latency injection, use Chaos Mesh"
}

# Main logic
TOOL_STATUS=$(check_chaos_tools)
case $? in
    0)
        inject_latency_chaos_mesh
        ;;
    1)
        echo "Using basic network policies..."
        create_latency_simulation
        ;;
    2)
        echo "Using iptables approach..."
        inject_latency_iptables
        ;;
esac

echo ""
echo "=========================================="
echo "Network latency injection setup completed"
echo "=========================================="
echo ""
echo "To test latency:"
echo "  kubectl exec -it <pod-name> -n $NAMESPACE -- ping <target-service>"
echo ""
echo "To remove latency injection:"
if [ "$TOOL_STATUS" -eq 0 ]; then
    echo "  kubectl delete networkchaos -l app=network-latency -n $NAMESPACE"
else
    echo "  kubectl delete pods -l app=network-latency-injector -n $NAMESPACE"
    echo "  kubectl delete networkpolicies -n $NAMESPACE --all"
fi

