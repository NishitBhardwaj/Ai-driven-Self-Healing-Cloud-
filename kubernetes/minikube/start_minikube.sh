#!/bin/bash

# Minikube Startup Script for Self-Healing Cloud
# This script starts a local Kubernetes cluster with all necessary addons
# for testing the Self-Healing Agent system

set -e

echo "=========================================="
echo "Starting Minikube Cluster"
echo "=========================================="

# Configuration
CLUSTER_NAME="self-healing-cloud"
MEMORY="4096"
CPUS="2"
DISK_SIZE="20g"
KUBERNETES_VERSION="v1.28.0"

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "ERROR: Minikube is not installed"
    echo "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

echo ""
echo "Checking existing Minikube cluster..."
if minikube status -p $CLUSTER_NAME &> /dev/null; then
    echo "Minikube cluster '$CLUSTER_NAME' already exists"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing cluster..."
        minikube delete -p $CLUSTER_NAME
    else
        echo "Starting existing cluster..."
        minikube start -p $CLUSTER_NAME
        minikube update-context -p $CLUSTER_NAME
        goto_addons
    fi
fi

echo ""
echo "Creating Minikube cluster..."
echo "  Name: $CLUSTER_NAME"
echo "  Memory: $MEMORY MB"
echo "  CPUs: $CPUS"
echo "  Disk Size: $DISK_SIZE"
echo "  Kubernetes Version: $KUBERNETES_VERSION"

minikube start -p $CLUSTER_NAME \
    --memory=$MEMORY \
    --cpus=$CPUS \
    --disk-size=$DISK_SIZE \
    --kubernetes-version=$KUBERNETES_VERSION \
    --driver=docker

echo ""
echo "Configuring kubectl context..."
minikube update-context -p $CLUSTER_NAME

# Wait for cluster to be ready
echo ""
echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

goto_addons() {
    echo ""
    echo "=========================================="
    echo "Enabling Minikube Addons"
    echo "=========================================="

    # Enable metrics server (required for HPA)
    echo ""
    echo "Enabling metrics-server..."
    minikube addons enable metrics-server -p $CLUSTER_NAME
    sleep 5

    # Enable ingress
    echo ""
    echo "Enabling ingress..."
    minikube addons enable ingress -p $CLUSTER_NAME
    sleep 5

    # Enable ingress-dns (optional, for local DNS)
    echo ""
    echo "Enabling ingress-dns..."
    minikube addons enable ingress-dns -p $CLUSTER_NAME || echo "ingress-dns not available, skipping..."
    sleep 3

    # Enable dashboard (optional, for monitoring)
    echo ""
    echo "Enabling dashboard..."
    minikube addons enable dashboard -p $CLUSTER_NAME
    sleep 3

    # Verify addons
    echo ""
    echo "Verifying addons..."
    minikube addons list -p $CLUSTER_NAME | grep -E "(metrics-server|ingress|dashboard)" || true

    echo ""
    echo "=========================================="
    echo "Setting up Load Balancer Emulation"
    echo "=========================================="

    # Enable metallb for LoadBalancer services (if available)
    echo ""
    echo "Checking for MetalLB support..."
    if minikube addons list -p $CLUSTER_NAME | grep -q "metallb"; then
        echo "Enabling MetalLB for LoadBalancer emulation..."
        minikube addons enable metallb -p $CLUSTER_NAME
        sleep 5
        
        # Get Minikube IP
        MINIKUBE_IP=$(minikube ip -p $CLUSTER_NAME)
        echo "Minikube IP: $MINIKUBE_IP"
        
        # Configure MetalLB IP range (using Minikube IP range)
        echo "Configuring MetalLB IP pool..."
        # Note: User may need to configure this manually based on their network
        echo "MetalLB enabled. Configure IP pool if needed."
    else
        echo "MetalLB not available. Using NodePort for LoadBalancer services."
        echo "To access services, use: minikube service <service-name> -p $CLUSTER_NAME"
    fi

    echo ""
    echo "=========================================="
    echo "Verifying Cluster Status"
    echo "=========================================="

    # Wait for metrics server to be ready
    echo ""
    echo "Waiting for metrics-server to be ready..."
    kubectl wait --for=condition=ready pod \
        -l k8s-app=metrics-server \
        -n kube-system \
        --timeout=120s || echo "Warning: metrics-server may not be ready yet"

    # Check node status
    echo ""
    echo "Node Status:"
    kubectl get nodes

    # Check system pods
    echo ""
    echo "System Pods:"
    kubectl get pods -n kube-system | grep -E "(metrics-server|ingress|dashboard)" || true

    # Verify metrics server
    echo ""
    echo "Testing metrics-server..."
    sleep 10
    if kubectl top nodes &> /dev/null; then
        echo "✅ Metrics server is working!"
        kubectl top nodes
    else
        echo "⚠️  Metrics server may need more time to initialize"
    fi

    echo ""
    echo "=========================================="
    echo "Cluster Information"
    echo "=========================================="
    echo ""
    echo "Cluster Name: $CLUSTER_NAME"
    echo "Minikube IP: $(minikube ip -p $CLUSTER_NAME)"
    echo ""
    echo "Useful Commands:"
    echo "  kubectl get nodes          - View cluster nodes"
    echo "  kubectl get pods -A        - View all pods"
    echo "  minikube dashboard -p $CLUSTER_NAME  - Open Kubernetes dashboard"
    echo "  minikube service <svc> -p $CLUSTER_NAME  - Access a service"
    echo "  minikube stop -p $CLUSTER_NAME       - Stop cluster"
    echo "  minikube delete -p $CLUSTER_NAME    - Delete cluster"
    echo ""
    echo "To access dashboard:"
    echo "  minikube dashboard -p $CLUSTER_NAME --url"
    echo ""
    echo "=========================================="
    echo "Minikube cluster is ready!"
    echo "=========================================="
}

goto_addons

