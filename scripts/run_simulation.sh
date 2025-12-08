#!/bin/bash

# Run Simulation Script
# This script starts the complete cloud simulation environment:
# - LocalStack (AWS simulation)
# - Minikube (Kubernetes simulation)
# - Mock microservices
# - Validates environment
# - Prints endpoints

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

echo -e "${BLUE}=========================================="
echo "Cloud Simulation Environment Setup"
echo "==========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is available
port_available() {
    local port=$1
    if command_exists netstat; then
        ! netstat -an | grep -q ":$port "
    elif command_exists lsof; then
        ! lsof -i ":$port" >/dev/null 2>&1
    else
        echo -e "${YELLOW}Warning: Cannot check port availability${NC}"
        return 0
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    echo -n "Waiting for $name to be ready"
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

# Validate prerequisites
echo -e "${BLUE}Step 1: Validating Prerequisites${NC}"
echo ""

missing_deps=()

if ! command_exists docker; then
    missing_deps+=("docker")
fi

if ! command_exists docker-compose; then
    missing_deps+=("docker-compose")
fi

if ! command_exists minikube; then
    missing_deps+=("minikube")
fi

if ! command_exists kubectl; then
    missing_deps+=("kubectl")
fi

if ! command_exists curl; then
    missing_deps+=("curl")
fi

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo -e "${RED}Error: Missing dependencies: ${missing_deps[*]}${NC}"
    echo "Please install the missing dependencies and try again."
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Check Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker and try again."
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Start LocalStack
echo -e "${BLUE}Step 2: Starting LocalStack${NC}"
echo ""

if [ ! -d "$LOCALSTACK_DIR" ]; then
    echo -e "${RED}Error: LocalStack directory not found: $LOCALSTACK_DIR${NC}"
    exit 1
fi

cd "$LOCALSTACK_DIR"

# Check if LocalStack is already running
if docker ps | grep -q "localstack"; then
    echo -e "${YELLOW}LocalStack is already running${NC}"
else
    echo "Starting LocalStack..."
    docker-compose up -d
    
    if wait_for_service "http://localhost:4566/_localstack/health" "LocalStack"; then
        echo -e "${GREEN}✓ LocalStack started successfully${NC}"
    else
        echo -e "${RED}✗ LocalStack failed to start${NC}"
        echo "Check logs: docker-compose logs localstack"
        exit 1
    fi
fi

# Bootstrap LocalStack resources
if [ -f "bootstrap.sh" ]; then
    echo ""
    echo "Bootstrapping LocalStack resources..."
    chmod +x bootstrap.sh
    ./bootstrap.sh || echo -e "${YELLOW}Warning: Bootstrap script had issues (this may be normal)${NC}"
fi

echo ""

# Step 3: Start Minikube
echo -e "${BLUE}Step 3: Starting Minikube${NC}"
echo ""

if [ ! -d "$MINIKUBE_DIR" ]; then
    echo -e "${RED}Error: Minikube directory not found: $MINIKUBE_DIR${NC}"
    exit 1
fi

cd "$MINIKUBE_DIR"

# Check if Minikube is already running
if minikube status >/dev/null 2>&1; then
    echo -e "${YELLOW}Minikube is already running${NC}"
    minikube status
else
    echo "Starting Minikube..."
    if [ -f "start_minikube.sh" ]; then
        chmod +x start_minikube.sh
        ./start_minikube.sh
    else
        minikube start
    fi
fi

# Wait for Minikube to be ready
echo ""
echo "Waiting for Minikube to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if kubectl get nodes >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Minikube is ready${NC}"
        break
    fi
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ Minikube failed to start${NC}"
    exit 1
fi

echo ""

# Step 4: Create namespace
echo -e "${BLUE}Step 4: Creating Kubernetes Namespace${NC}"
echo ""

if [ -f "namespace.yaml" ]; then
    kubectl apply -f namespace.yaml
    echo -e "${GREEN}✓ Namespace created${NC}"
else
    kubectl create namespace self-healing-cloud --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}✓ Namespace created${NC}"
fi

echo ""

# Step 5: Deploy mock microservices
echo -e "${BLUE}Step 5: Deploying Mock Microservices${NC}"
echo ""

if [ -d "deployments" ]; then
    echo "Deploying compute-service..."
    kubectl apply -f deployments/compute-service/ 2>/dev/null || echo -e "${YELLOW}Warning: compute-service deployment had issues${NC}"
    
    echo "Deploying storage-service..."
    kubectl apply -f deployments/storage-service/ 2>/dev/null || echo -e "${YELLOW}Warning: storage-service deployment had issues${NC}"
    
    echo "Deploying logging-service..."
    kubectl apply -f deployments/logging-service/ 2>/dev/null || echo -e "${YELLOW}Warning: logging-service deployment had issues${NC}"
    
    echo ""
    echo "Waiting for deployments to be ready..."
    sleep 10
    
    kubectl get deployments -n self-healing-cloud
    echo -e "${GREEN}✓ Mock services deployed${NC}"
else
    echo -e "${YELLOW}Warning: Deployments directory not found${NC}"
fi

echo ""

# Step 6: Start simulation services (optional)
echo -e "${BLUE}Step 6: Starting Simulation Services${NC}"
echo ""

if [ -f "$DOCKER_COMPOSE_DIR/docker-compose.simulation.yml" ]; then
    cd "$DOCKER_COMPOSE_DIR"
    echo "Starting Prometheus, MinIO, and other simulation services..."
    docker-compose -f docker-compose.simulation.yml up -d 2>/dev/null || echo -e "${YELLOW}Warning: Some simulation services failed to start${NC}"
    echo -e "${GREEN}✓ Simulation services started${NC}"
else
    echo -e "${YELLOW}Warning: Simulation docker-compose file not found${NC}"
fi

echo ""

# Step 7: Validate environment
echo -e "${BLUE}Step 7: Validating Environment${NC}"
echo ""

validation_passed=true

# Validate LocalStack
echo -n "Validating LocalStack connection... "
if curl -s -f "http://localhost:4566/_localstack/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    validation_passed=false
fi

# Validate Kubernetes
echo -n "Validating Kubernetes connection... "
if kubectl get nodes >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    validation_passed=false
fi

# Validate namespace
echo -n "Validating namespace exists... "
if kubectl get namespace self-healing-cloud >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    validation_passed=false
fi

# Validate deployments
echo -n "Validating deployments... "
deployments=$(kubectl get deployments -n self-healing-cloud --no-headers 2>/dev/null | wc -l)
if [ "$deployments" -gt 0 ]; then
    echo -e "${GREEN}✓ ($deployments deployments)${NC}"
else
    echo -e "${YELLOW}⚠ (no deployments found)${NC}"
fi

echo ""

# Step 8: Print endpoints
echo -e "${BLUE}=========================================="
echo "Environment Endpoints"
echo "==========================================${NC}"
echo ""
echo -e "${GREEN}LocalStack:${NC}"
echo "  - API Gateway:    http://localhost:4566"
echo "  - UI:             http://localhost:8080"
echo ""
echo -e "${GREEN}Kubernetes:${NC}"
echo "  - Cluster:        $(minikube ip 2>/dev/null || echo 'N/A')"
echo "  - Dashboard:      minikube dashboard"
echo "  - Namespace:      self-healing-cloud"
echo ""
echo -e "${GREEN}Simulation Services:${NC}"
echo "  - Prometheus:     http://localhost:9090"
echo "  - MinIO Console:  http://localhost:9001 (minioadmin/minioadmin)"
echo "  - MinIO API:      http://localhost:9000"
echo "  - cAdvisor:       http://localhost:8084"
echo ""
echo -e "${GREEN}Environment Variables:${NC}"
echo "  export AWS_ENDPOINT_URL=http://localhost:4566"
echo "  export AWS_ACCESS_KEY_ID=test"
echo "  export AWS_SECRET_ACCESS_KEY=test"
echo "  export AWS_DEFAULT_REGION=us-east-1"
echo "  export KUBECONFIG=~/.kube/config"
echo "  export KUBERNETES_NAMESPACE=self-healing-cloud"
echo "  export PROMETHEUS_URL=http://localhost:9090"
echo ""

# Final status
if [ "$validation_passed" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "✓ Cloud Simulation Environment Ready!"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Set environment variables (see above)"
    echo "  2. Run agents: cd agents && go run ..."
    echo "  3. Run tests: cd tests/cloud && go test -v"
    echo "  4. Reset environment: ./scripts/reset_simulation.sh"
    echo ""
    exit 0
else
    echo -e "${YELLOW}=========================================="
    echo "⚠ Environment started with warnings"
    echo "==========================================${NC}"
    echo ""
    echo "Some validations failed. Check the output above for details."
    echo ""
    exit 1
fi

