#!/bin/bash

# CI/CD Pipeline Validation Script
# Validates that CI/CD pipeline correctly deploys updates to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-cloud-production}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
TIMEOUT="${TIMEOUT:-300}"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    print_info "✓ kubectl is available and connected to cluster"
}

# Function to check deployment status
check_deployment() {
    local deployment=$1
    local namespace=$2
    
    print_info "Checking deployment: ${deployment} in namespace ${namespace}..."
    
    # Check if deployment exists
    if ! kubectl get deployment "$deployment" -n "$namespace" &> /dev/null; then
        print_error "Deployment ${deployment} not found"
        return 1
    fi
    
    # Wait for deployment to be ready
    print_info "Waiting for deployment ${deployment} to be ready..."
    if kubectl wait --for=condition=available --timeout="${TIMEOUT}s" \
        deployment/"$deployment" -n "$namespace" &> /dev/null; then
        print_info "✓ Deployment ${deployment} is available"
        
        # Check replica status
        local desired=$(kubectl get deployment "$deployment" -n "$namespace" \
            -o jsonpath='{.spec.replicas}')
        local ready=$(kubectl get deployment "$deployment" -n "$namespace" \
            -o jsonpath='{.status.readyReplicas}')
        
        if [ "$desired" = "$ready" ]; then
            print_info "✓ All ${desired} replicas are ready"
            return 0
        else
            print_warn "Only ${ready}/${desired} replicas are ready"
            return 1
        fi
    else
        print_error "Deployment ${deployment} did not become available within ${TIMEOUT}s"
        return 1
    fi
}

# Function to check image version
check_image_version() {
    local deployment=$1
    local namespace=$2
    local expected_tag=$3
    
    print_info "Checking image version for deployment ${deployment}..."
    
    local image=$(kubectl get deployment "$deployment" -n "$namespace" \
        -o jsonpath='{.spec.template.spec.containers[0].image}')
    
    if [[ "$image" == *"$expected_tag"* ]]; then
        print_info "✓ Image version matches expected tag: ${expected_tag}"
        print_info "  Image: ${image}"
        return 0
    else
        print_warn "Image version does not match expected tag"
        print_warn "  Expected tag: ${expected_tag}"
        print_warn "  Actual image: ${image}"
        return 1
    fi
}

# Function to check service
check_service() {
    local service=$1
    local namespace=$2
    
    print_info "Checking service: ${service} in namespace ${namespace}..."
    
    if ! kubectl get svc "$service" -n "$namespace" &> /dev/null; then
        print_error "Service ${service} not found"
        return 1
    fi
    
    # Check endpoints
    local endpoints=$(kubectl get endpoints "$service" -n "$namespace" \
        -o jsonpath='{.subsets[*].addresses[*].ip}' 2>/dev/null || echo "")
    
    if [ -n "$endpoints" ]; then
        print_info "✓ Service ${service} has endpoints"
        return 0
    else
        print_warn "Service ${service} has no endpoints"
        return 1
    fi
}

# Function to check rolling update
check_rolling_update() {
    local deployment=$1
    local namespace=$2
    
    print_info "Checking rolling update for deployment ${deployment}..."
    
    # Check if deployment is updating
    local updating=$(kubectl get deployment "$deployment" -n "$namespace" \
        -o jsonpath='{.status.conditions[?(@.type=="Progressing")].status}' 2>/dev/null || echo "Unknown")
    
    if [ "$updating" = "True" ]; then
        print_info "Deployment is updating..."
        
        # Wait for update to complete
        local max_wait=300
        local waited=0
        while [ $waited -lt $max_wait ]; do
            local status=$(kubectl get deployment "$deployment" -n "$namespace" \
                -o jsonpath='{.status.conditions[?(@.type=="Progressing")].status}' 2>/dev/null || echo "Unknown")
            
            if [ "$status" != "True" ]; then
                print_info "✓ Rolling update completed"
                return 0
            fi
            
            sleep 5
            waited=$((waited + 5))
        done
        
        print_warn "Rolling update did not complete within ${max_wait}s"
        return 1
    else
        print_info "✓ Deployment is not updating (stable)"
        return 0
    fi
}

# Main validation
main() {
    print_info "Starting CI/CD pipeline validation..."
    print_info "Namespace: ${NAMESPACE}"
    print_info "Image Tag: ${IMAGE_TAG}"
    print_info ""
    
    # Check prerequisites
    check_kubectl
    
    local agents=(
        "self-healing"
        "scaling"
        "task-solving"
        "performance-monitoring"
        "coding"
        "security"
        "optimization"
    )
    
    local total=0
    local passed=0
    local failed=0
    
    # Validate each agent
    for agent in "${agents[@]}"; do
        local deployment="ai-cloud-${agent}"
        local service="ai-cloud-${agent}"
        
        total=$((total + 4))  # deployment, image, service, rolling update
        
        # Check deployment
        if check_deployment "$deployment" "$NAMESPACE"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        # Check image version
        if check_image_version "$deployment" "$NAMESPACE" "$IMAGE_TAG"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        # Check service
        if check_service "$service" "$NAMESPACE"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        # Check rolling update
        if check_rolling_update "$deployment" "$NAMESPACE"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        echo ""
    done
    
    # Summary
    print_info "Validation Summary:"
    print_info "  Total checks: ${total}"
    print_info "  Passed: ${passed}"
    if [ $failed -gt 0 ]; then
        print_error "  Failed: ${failed}"
        exit 1
    else
        print_info "  Failed: ${failed}"
        print_info "All CI/CD validations passed! ✓"
        exit 0
    fi
}

# Run main function
main "$@"

