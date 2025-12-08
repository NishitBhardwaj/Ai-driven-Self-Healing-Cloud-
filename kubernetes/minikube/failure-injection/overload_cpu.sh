#!/bin/bash

# CPU Overload Script
# This script creates a pod that overloads CPU resources
# Used for chaos engineering and testing the Self-Healing Agent's response to resource pressure

set -e

NAMESPACE="${NAMESPACE:-self-healing-cloud}"
DURATION="${DURATION:-300}"  # Default 5 minutes
CPU_LOAD="${CPU_LOAD:-100}"  # Percentage of CPU to use
DEPLOYMENT="${DEPLOYMENT:-}"

echo "=========================================="
echo "CPU Overload - Chaos Engineering"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Duration: $DURATION seconds"
echo "CPU Load: $CPU_LOAD%"
echo "Target Deployment: ${DEPLOYMENT:-all pods in namespace}"
echo ""

# Function to create CPU stress pod
create_cpu_stress_pod() {
    local pod_name="cpu-stress-$(date +%s)"
    local cpu_cores="${CPU_LOAD}"
    
    echo "Creating CPU stress pod: $pod_name"
    
    # Create a pod that will consume CPU
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $pod_name
  namespace: $NAMESPACE
  labels:
    app: cpu-stress
    chaos-engineering: "true"
spec:
  restartPolicy: Never
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--cpu", "$cpu_cores", "--timeout", "${DURATION}s"]
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "2000m"
        memory: "512Mi"
EOF

    echo ""
    echo "✅ CPU stress pod created: $pod_name"
    echo ""
    echo "Monitoring CPU usage..."
    
    # Monitor for specified duration
    sleep 5
    
    # Show pod status
    kubectl get pod "$pod_name" -n "$NAMESPACE"
    
    echo ""
    echo "CPU stress will run for $DURATION seconds"
    echo "You can monitor CPU usage with:"
    echo "  kubectl top pods -n $NAMESPACE"
    echo "  kubectl top nodes"
    
    # Wait for pod to complete or timeout
    echo ""
    echo "Waiting for stress test to complete..."
    kubectl wait --for=condition=Ready pod/$pod_name -n "$NAMESPACE" --timeout=${DURATION}s 2>/dev/null || true
    
    # Check if pod is still running
    if kubectl get pod "$pod_name" -n "$NAMESPACE" &>/dev/null; then
        echo ""
        echo "Stress test completed. Pod will be cleaned up automatically."
        echo "To manually delete: kubectl delete pod $pod_name -n $NAMESPACE"
    fi
}

# Function to overload specific deployment
overload_deployment() {
    local deployment="$1"
    
    echo "Overloading CPU for deployment: $deployment"
    
    # Get pods from deployment
    PODS=$(kubectl get pods -n "$NAMESPACE" -l "app=$deployment" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    
    if [ -z "$PODS" ]; then
        echo "ERROR: No pods found for deployment: $deployment"
        return 1
    fi
    
    read -ra POD_ARRAY <<< "$PODS"
    
    echo "Found ${#POD_ARRAY[@]} pod(s) in deployment"
    echo ""
    
    for pod in "${POD_ARRAY[@]}"; do
        echo "Injecting CPU load into pod: $pod"
        
        # Create a sidecar container or exec stress command
        # Using kubectl exec to run stress in existing pod
        kubectl exec -n "$NAMESPACE" "$pod" -- sh -c "
            if command -v stress &> /dev/null; then
                stress --cpu 1 --timeout ${DURATION}s &
            elif command -v yes &> /dev/null; then
                timeout ${DURATION}s yes > /dev/null &
            else
                echo 'Stress tools not available in pod'
            fi
        " 2>/dev/null || echo "⚠️  Could not inject CPU load into $pod (may need stress tool installed)"
    done
    
    echo ""
    echo "CPU load injected into deployment pods"
    echo "Monitor with: kubectl top pods -n $NAMESPACE"
}

# Main logic
if [ -n "$DEPLOYMENT" ]; then
    overload_deployment "$DEPLOYMENT"
else
    create_cpu_stress_pod
fi

echo ""
echo "=========================================="
echo "CPU overload script completed"
echo "=========================================="
echo ""
echo "To clean up stress pods:"
echo "  kubectl delete pods -l app=cpu-stress -n $NAMESPACE"

