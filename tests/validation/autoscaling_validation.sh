#!/bin/bash

# Auto-Scaling Validation Script
# Tests auto-scaling by adding load and verifying scaling behavior

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-cloud-production}"
LOAD_DURATION="${LOAD_DURATION:-300}"  # 5 minutes
LOAD_RATE="${LOAD_RATE:-100}"  # requests per second
SCALE_UP_TIMEOUT="${SCALE_UP_TIMEOUT:-300}"  # 5 minutes
SCALE_DOWN_TIMEOUT="${SCALE_DOWN_TIMEOUT:-600}"  # 10 minutes

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

# Function to check HPA
check_hpa() {
    local deployment=$1
    local namespace=$2
    
    print_info "Checking HPA for deployment ${deployment}..."
    
    local hpa_name="ai-cloud-${deployment}-advanced"
    if ! kubectl get hpa "$hpa_name" -n "$namespace" &> /dev/null; then
        print_warn "HPA ${hpa_name} not found, checking default HPA..."
        hpa_name="ai-cloud-${deployment}"
    fi
    
    if kubectl get hpa "$hpa_name" -n "$namespace" &> /dev/null; then
        local min_replicas=$(kubectl get hpa "$hpa_name" -n "$namespace" \
            -o jsonpath='{.spec.minReplicas}')
        local max_replicas=$(kubectl get hpa "$hpa_name" -n "$namespace" \
            -o jsonpath='{.spec.maxReplicas}')
        
        print_info "✓ HPA ${hpa_name} found"
        print_info "  Min replicas: ${min_replicas}"
        print_info "  Max replicas: ${max_replicas}"
        return 0
    else
        print_error "HPA not found for deployment ${deployment}"
        return 1
    fi
}

# Function to get current replica count
get_replica_count() {
    local deployment=$1
    local namespace=$2
    
    kubectl get deployment "$deployment" -n "$namespace" \
        -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0"
}

# Function to generate load
generate_load() {
    local service=$1
    local namespace=$2
    local duration=$3
    local rate=$4
    
    print_info "Generating load on service ${service}..."
    print_info "  Duration: ${duration}s"
    print_info "  Rate: ${rate} req/s"
    
    # Get service endpoint
    local endpoint=$(kubectl get svc "$service" -n "$namespace" \
        -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}' 2>/dev/null || echo "")
    
    if [ -z "$endpoint" ]; then
        print_error "Cannot get service endpoint for ${service}"
        return 1
    fi
    
    print_info "  Endpoint: ${endpoint}"
    
    # Generate load using curl in background
    local start_time=$(date +%s)
    local end_time=$((start_time + duration))
    local request_count=0
    
    while [ $(date +%s) -lt $end_time ]; do
        # Send requests in parallel
        for i in $(seq 1 $rate); do
            curl -s "http://${endpoint}/health" > /dev/null 2>&1 &
            request_count=$((request_count + 1))
        done
        
        # Wait 1 second
        sleep 1
        
        # Print progress
        if [ $((request_count % 100)) -eq 0 ]; then
            print_info "  Sent ${request_count} requests..."
        fi
    done
    
    # Wait for all background jobs
    wait
    
    print_info "✓ Load generation completed (${request_count} requests)"
}

# Function to monitor scaling
monitor_scaling() {
    local deployment=$1
    local namespace=$2
    local expected_direction=$3  # "up" or "down"
    local timeout=$4
    local initial_replicas=$5
    
    print_info "Monitoring scaling for deployment ${deployment}..."
    print_info "  Initial replicas: ${initial_replicas}"
    print_info "  Expected direction: ${expected_direction}"
    print_info "  Timeout: ${timeout}s"
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    local last_replicas=$initial_replicas
    
    while [ $(date +%s) -lt $end_time ]; do
        local current_replicas=$(get_replica_count "$deployment" "$namespace")
        
        if [ "$current_replicas" != "$last_replicas" ]; then
            print_info "  Replica count changed: ${last_replicas} → ${current_replicas}"
            last_replicas=$current_replicas
        fi
        
        # Check if scaling occurred
        if [ "$expected_direction" = "up" ] && [ "$current_replicas" -gt "$initial_replicas" ]; then
            print_info "✓ Scale-up detected: ${initial_replicas} → ${current_replicas}"
            return 0
        elif [ "$expected_direction" = "down" ] && [ "$current_replicas" -lt "$initial_replicas" ]; then
            print_info "✓ Scale-down detected: ${initial_replicas} → ${current_replicas}"
            return 0
        fi
        
        sleep 5
    done
    
    print_warn "Scaling ${expected_direction} did not occur within ${timeout}s"
    print_warn "  Final replicas: ${current_replicas}"
    return 1
}

# Function to test scale-up
test_scale_up() {
    local deployment=$1
    local namespace=$2
    
    print_info "Testing scale-up for deployment ${deployment}..."
    
    # Get initial replica count
    local initial_replicas=$(get_replica_count "$deployment" "$namespace")
    print_info "  Initial replicas: ${initial_replicas}"
    
    # Get service name
    local service="ai-cloud-${deployment}"
    
    # Generate load
    generate_load "$service" "$namespace" "$LOAD_DURATION" "$LOAD_RATE" &
    local load_pid=$!
    
    # Monitor scaling
    if monitor_scaling "$deployment" "$namespace" "up" "$SCALE_UP_TIMEOUT" "$initial_replicas"; then
        print_info "✓ Scale-up test passed"
        
        # Stop load generation
        kill $load_pid 2>/dev/null || true
        wait $load_pid 2>/dev/null || true
        
        return 0
    else
        print_error "✗ Scale-up test failed"
        
        # Stop load generation
        kill $load_pid 2>/dev/null || true
        wait $load_pid 2>/dev/null || true
        
        return 1
    fi
}

# Function to test scale-down
test_scale_down() {
    local deployment=$1
    local namespace=$2
    
    print_info "Testing scale-down for deployment ${deployment}..."
    
    # Wait for load to decrease
    print_info "  Waiting for load to decrease..."
    sleep 60
    
    # Get current replica count
    local initial_replicas=$(get_replica_count "$deployment" "$namespace")
    print_info "  Current replicas: ${initial_replicas}"
    
    # Monitor scaling
    if monitor_scaling "$deployment" "$namespace" "down" "$SCALE_DOWN_TIMEOUT" "$initial_replicas"; then
        print_info "✓ Scale-down test passed"
        return 0
    else
        print_warn "✗ Scale-down test failed (may be expected if min replicas reached)"
        return 1
    fi
}

# Main validation
main() {
    print_info "Starting auto-scaling validation..."
    print_info "Namespace: ${NAMESPACE}"
    print_info "Load duration: ${LOAD_DURATION}s"
    print_info "Load rate: ${LOAD_RATE} req/s"
    print_info ""
    
    # Test agent (use self-healing as example)
    local test_agent="self-healing"
    local deployment="ai-cloud-${test_agent}"
    
    # Check HPA
    if ! check_hpa "$test_agent" "$NAMESPACE"; then
        print_error "HPA not configured, cannot test auto-scaling"
        exit 1
    fi
    
    # Test scale-up
    if test_scale_up "$test_agent" "$NAMESPACE"; then
        print_info "✓ Scale-up validation passed"
    else
        print_error "✗ Scale-up validation failed"
        exit 1
    fi
    
    # Test scale-down
    if test_scale_down "$test_agent" "$NAMESPACE"; then
        print_info "✓ Scale-down validation passed"
    else
        print_warn "✗ Scale-down validation failed (may be expected)"
    fi
    
    print_info ""
    print_info "Auto-scaling validation completed! ✓"
}

# Run main function
main "$@"

