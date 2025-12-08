#!/bin/bash

# Reset Simulation Script
# This script resets the entire cloud simulation environment:
# - Stops and removes LocalStack containers
# - Stops and removes Minikube cluster
# - Cleans up Kubernetes resources
# - Removes Docker volumes
# - Cleans up simulation services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOCALSTACK_DIR="$PROJECT_ROOT/cloud-simulation/localstack"
MINIKUBE_DIR="$PROJECT_ROOT/kubernetes/minikube"
DOCKER_COMPOSE_DIR="$PROJECT_ROOT/docker"

echo -e "${RED}=========================================="
echo "Cloud Simulation Environment Reset"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}This will:${NC}"
echo "  - Stop and remove LocalStack containers"
echo "  - Stop and remove Minikube cluster"
echo "  - Delete all Kubernetes resources in self-healing-cloud namespace"
echo "  - Remove Docker volumes (LocalStack, MinIO, Prometheus data)"
echo "  - Stop simulation services"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reset cancelled."
    exit 0
fi

echo ""

# Step 1: Stop and remove LocalStack
echo -e "${BLUE}Step 1: Stopping LocalStack${NC}"
echo ""

if [ -d "$LOCALSTACK_DIR" ]; then
    cd "$LOCALSTACK_DIR"
    
    if docker ps | grep -q "localstack"; then
        echo "Stopping LocalStack containers..."
        docker-compose down -v 2>/dev/null || true
        echo -e "${GREEN}✓ LocalStack stopped${NC}"
    else
        echo -e "${YELLOW}LocalStack is not running${NC}"
    fi
    
    # Remove LocalStack data directory
    if [ -d ".localstack" ]; then
        echo "Removing LocalStack data..."
        rm -rf .localstack
        echo -e "${GREEN}✓ LocalStack data removed${NC}"
    fi
else
    echo -e "${YELLOW}LocalStack directory not found${NC}"
fi

echo ""

# Step 2: Stop and remove Minikube
echo -e "${BLUE}Step 2: Stopping Minikube${NC}"
echo ""

if command -v minikube >/dev/null 2>&1; then
    if minikube status >/dev/null 2>&1; then
        echo "Stopping Minikube cluster..."
        minikube stop 2>/dev/null || true
        
        read -p "Delete Minikube cluster completely? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Deleting Minikube cluster..."
            minikube delete 2>/dev/null || true
            echo -e "${GREEN}✓ Minikube cluster deleted${NC}"
        else
            echo -e "${GREEN}✓ Minikube stopped (cluster preserved)${NC}"
        fi
    else
        echo -e "${YELLOW}Minikube is not running${NC}"
    fi
else
    echo -e "${YELLOW}Minikube not found${NC}"
fi

echo ""

# Step 3: Clean up Kubernetes resources
echo -e "${BLUE}Step 3: Cleaning Up Kubernetes Resources${NC}"
echo ""

if command -v kubectl >/dev/null 2>&1; then
    # Check if namespace exists
    if kubectl get namespace self-healing-cloud >/dev/null 2>&1; then
        echo "Deleting all resources in self-healing-cloud namespace..."
        kubectl delete all --all -n self-healing-cloud 2>/dev/null || true
        kubectl delete hpa --all -n self-healing-cloud 2>/dev/null || true
        kubectl delete configmap --all -n self-healing-cloud 2>/dev/null || true
        kubectl delete secret --all -n self-healing-cloud 2>/dev/null || true
        
        read -p "Delete self-healing-cloud namespace? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete namespace self-healing-cloud 2>/dev/null || true
            echo -e "${GREEN}✓ Namespace deleted${NC}"
        else
            echo -e "${GREEN}✓ Resources cleaned (namespace preserved)${NC}"
        fi
    else
        echo -e "${YELLOW}Namespace self-healing-cloud does not exist${NC}"
    fi
else
    echo -e "${YELLOW}kubectl not found${NC}"
fi

echo ""

# Step 4: Stop simulation services
echo -e "${BLUE}Step 4: Stopping Simulation Services${NC}"
echo ""

if [ -f "$DOCKER_COMPOSE_DIR/docker-compose.simulation.yml" ]; then
    cd "$DOCKER_COMPOSE_DIR"
    
    if docker ps | grep -qE "(prometheus|minio|cadvisor|node-exporter)"; then
        echo "Stopping simulation services..."
        docker-compose -f docker-compose.simulation.yml down -v 2>/dev/null || true
        echo -e "${GREEN}✓ Simulation services stopped${NC}"
    else
        echo -e "${YELLOW}Simulation services are not running${NC}"
    fi
else
    echo -e "${YELLOW}Simulation docker-compose file not found${NC}"
fi

echo ""

# Step 5: Clean up Docker volumes
echo -e "${BLUE}Step 5: Cleaning Up Docker Volumes${NC}"
echo ""

read -p "Remove Docker volumes (LocalStack, MinIO, Prometheus data)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing Docker volumes..."
    
    # Remove LocalStack volumes
    docker volume rm localstack-data 2>/dev/null || true
    docker volume rm "$(basename "$LOCALSTACK_DIR")_localstack-data" 2>/dev/null || true
    
    # Remove MinIO volumes
    docker volume rm minio-data 2>/dev/null || true
    docker volume rm "$(basename "$DOCKER_COMPOSE_DIR")_minio-data" 2>/dev/null || true
    
    # Remove Prometheus volumes
    docker volume rm prometheus-data 2>/dev/null || true
    docker volume rm "$(basename "$DOCKER_COMPOSE_DIR")_prometheus-data" 2>/dev/null || true
    
    echo -e "${GREEN}✓ Docker volumes removed${NC}"
else
    echo -e "${YELLOW}Docker volumes preserved${NC}"
fi

echo ""

# Step 6: Clean up orphaned containers
echo -e "${BLUE}Step 6: Cleaning Up Orphaned Containers${NC}"
echo ""

read -p "Remove orphaned containers? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing stopped containers..."
    docker container prune -f
    echo -e "${GREEN}✓ Orphaned containers removed${NC}"
else
    echo -e "${YELLOW}Orphaned containers preserved${NC}"
fi

echo ""

# Step 7: Clean up networks
echo -e "${BLUE}Step 7: Cleaning Up Networks${NC}"
echo ""

read -p "Remove unused Docker networks? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing unused networks..."
    docker network prune -f
    echo -e "${GREEN}✓ Unused networks removed${NC}"
else
    echo -e "${YELLOW}Unused networks preserved${NC}"
fi

echo ""

# Final summary
echo -e "${GREEN}=========================================="
echo "✓ Reset Complete!"
echo "==========================================${NC}"
echo ""
echo "The cloud simulation environment has been reset."
echo ""
echo "To start fresh, run:"
echo "  ./scripts/run_simulation.sh"
echo ""
echo "Note: Some resources may require manual cleanup:"
echo "  - Check for remaining Docker containers: docker ps -a"
echo "  - Check for remaining Docker volumes: docker volume ls"
echo "  - Check for remaining Docker networks: docker network ls"
echo ""

