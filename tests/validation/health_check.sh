#!/bin/bash

# Health Check Validation Script
# Validates all agent health endpoints

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-ai-cloud-production}"
BASE_URL="${BASE_URL:-http://localhost}"
TIMEOUT="${TIMEOUT:-10}"

# Agents configuration
declare -A AGENTS=(
    ["self-healing"]="8080"
    ["scaling"]="8080"
    ["task-solving"]="8080"
    ["performance-monitoring"]="8080"
    ["coding"]="8080"
    ["security"]="8080"
    ["optimization"]="8080"
)

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

# Function to check health endpoint
check_health() {
    local agent=$1
    local port=$2
    local url="${BASE_URL}:${port}/health"
    
    print_info "Checking health for ${agent} agent at ${url}..."
    
    # Check if running in Kubernetes
    if command -v kubectl &> /dev/null; then
        # Get service URL
        local service_name="ai-cloud-${agent}"
        if kubectl get svc "$service_name" -n "$NAMESPACE" &> /dev/null; then
            # Port forward if needed
            local pod=$(kubectl get pod -n "$NAMESPACE" -l component="$agent" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
            if [ -n "$pod" ]; then
                url="http://localhost:${port}"
                kubectl port-forward -n "$NAMESPACE" "pod/${pod}" "${port}:${port}" > /dev/null 2>&1 &
                local pf_pid=$!
                sleep 2
            fi
        fi
    fi
    
    # Check health endpoint
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo -e "\n000")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    # Cleanup port forward
    if [ -n "$pf_pid" ]; then
        kill "$pf_pid" 2>/dev/null || true
    fi
    
    if [ "$http_code" = "200" ]; then
        print_info "✓ ${agent} agent is healthy (HTTP ${http_code})"
        
        # Parse health response
        if command -v jq &> /dev/null && [ -n "$body" ]; then
            local status=$(echo "$body" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
            if [ "$status" != "healthy" ] && [ "$status" != "ok" ]; then
                print_warn "  Status: ${status}"
            fi
        fi
        return 0
    else
        print_error "✗ ${agent} agent is unhealthy (HTTP ${http_code})"
        return 1
    fi
}

# Function to check readiness endpoint
check_readiness() {
    local agent=$1
    local port=$2
    local url="${BASE_URL}:${port}/ready"
    
    print_info "Checking readiness for ${agent} agent at ${url}..."
    
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo -e "\n000")
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        print_info "✓ ${agent} agent is ready (HTTP ${http_code})"
        return 0
    else
        print_warn "✗ ${agent} agent is not ready (HTTP ${http_code})"
        return 1
    fi
}

# Function to check metrics endpoint
check_metrics() {
    local agent=$1
    local port=$2
    local metrics_port=$((port + 1))
    local url="${BASE_URL}:${metrics_port}/metrics"
    
    print_info "Checking metrics for ${agent} agent at ${url}..."
    
    local response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo -e "\n000")
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        print_info "✓ ${agent} agent metrics available (HTTP ${http_code})"
        return 0
    else
        print_warn "✗ ${agent} agent metrics unavailable (HTTP ${http_code})"
        return 1
    fi
}

# Main validation
main() {
    print_info "Starting health check validation..."
    print_info "Namespace: ${NAMESPACE}"
    print_info "Base URL: ${BASE_URL}"
    print_info ""
    
    local total=0
    local passed=0
    local failed=0
    
    # Check all agents
    for agent in "${!AGENTS[@]}"; do
        local port="${AGENTS[$agent]}"
        total=$((total + 3))  # health, readiness, metrics
        
        # Health check
        if check_health "$agent" "$port"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        # Readiness check
        if check_readiness "$agent" "$port"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
        
        # Metrics check
        if check_metrics "$agent" "$port"; then
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
        print_info "All health checks passed! ✓"
        exit 0
    fi
}

# Run main function
main "$@"

