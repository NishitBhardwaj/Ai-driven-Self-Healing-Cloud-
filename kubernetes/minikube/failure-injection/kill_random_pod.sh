#!/bin/bash

# Kill Random Pod Script
# This script randomly kills a pod from a specified deployment or namespace
# Used for chaos engineering and testing the Self-Healing Agent

set -e

NAMESPACE="${NAMESPACE:-self-healing-cloud}"
DEPLOYMENT="${DEPLOYMENT:-}"
SERVICE="${SERVICE:-}"

echo "=========================================="
echo "Kill Random Pod - Chaos Engineering"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Deployment: ${DEPLOYMENT:-all}"
echo "Service: ${SERVICE:-all}"
echo ""

# Function to kill a random pod
kill_random_pod() {
    local selector="$1"
    local label="$2"
    
    echo "Finding pods with selector: $selector"
    
    # Get list of pods
    if [ -n "$selector" ]; then
        PODS=$(kubectl get pods -n "$NAMESPACE" -l "$selector" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    else
        PODS=$(kubectl get pods -n "$NAMESPACE" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
    fi
    
    if [ -z "$PODS" ]; then
        echo "ERROR: No pods found with selector: $selector"
        return 1
    fi
    
    # Convert to array
    read -ra POD_ARRAY <<< "$PODS"
    
    if [ ${#POD_ARRAY[@]} -eq 0 ]; then
        echo "ERROR: No pods available to kill"
        return 1
    fi
    
    # Select random pod
    RANDOM_INDEX=$((RANDOM % ${#POD_ARRAY[@]}))
    SELECTED_POD="${POD_ARRAY[$RANDOM_INDEX]}"
    
    echo ""
    echo "Selected pod to kill: $SELECTED_POD"
    echo "Pod details:"
    kubectl get pod "$SELECTED_POD" -n "$NAMESPACE" -o wide
    
    echo ""
    read -p "Are you sure you want to kill this pod? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        return 0
    fi
    
    echo ""
    echo "Killing pod: $SELECTED_POD"
    kubectl delete pod "$SELECTED_POD" -n "$NAMESPACE" --grace-period=0 --force || {
        echo "ERROR: Failed to kill pod"
        return 1
    }
    
    echo ""
    echo "✅ Pod $SELECTED_POD has been killed"
    echo ""
    echo "Monitoring pod recreation..."
    sleep 2
    
    # Wait for new pod to be created
    echo "Waiting for new pod to be created..."
    timeout=60
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        NEW_PODS=$(kubectl get pods -n "$NAMESPACE" -l "$selector" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$NEW_PODS" ] && [[ ! "$NEW_PODS" =~ "$SELECTED_POD" ]]; then
            echo "✅ New pod(s) created: $NEW_PODS"
            break
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    
    if [ $elapsed -ge $timeout ]; then
        echo "⚠️  Warning: No new pod created within $timeout seconds"
    fi
    
    echo ""
    echo "Current pod status:"
    kubectl get pods -n "$NAMESPACE" -l "$selector" || kubectl get pods -n "$NAMESPACE"
}

# Main logic
if [ -n "$DEPLOYMENT" ]; then
    # Kill pod from specific deployment
    SELECTOR="app=$DEPLOYMENT"
    kill_random_pod "$SELECTOR" "deployment=$DEPLOYMENT"
elif [ -n "$SERVICE" ]; then
    # Kill pod from specific service
    SELECTOR="app=$SERVICE"
    kill_random_pod "$SELECTOR" "service=$SERVICE"
else
    # Kill random pod from namespace
    echo "No deployment or service specified. Killing random pod from namespace..."
    kill_random_pod "" "namespace=$NAMESPACE"
fi

echo ""
echo "=========================================="
echo "Script completed"
echo "=========================================="

