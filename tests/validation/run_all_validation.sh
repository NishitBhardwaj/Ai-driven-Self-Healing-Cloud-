#!/bin/bash

# Complete System Validation Script
# Runs all validation tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAMESPACE="${NAMESPACE:-ai-cloud-production}"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_section() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run validation script
run_validation() {
    local script=$1
    local name=$2
    
    print_section "Running: $name"
    
    if [ -f "$script" ]; then
        chmod +x "$script"
        if "$script"; then
            print_info "✓ $name passed"
            return 0
        else
            print_error "✗ $name failed"
            return 1
        fi
    else
        print_error "Script not found: $script"
        return 1
    fi
}

# Main validation
main() {
    print_section "System Validation - Complete Test Suite"
    print_info "Namespace: ${NAMESPACE}"
    print_info "Starting at: $(date)"
    print_info ""
    
    local total=0
    local passed=0
    local failed=0
    
    # 1. Health Check Validation
    if run_validation "${SCRIPT_DIR}/health_check.sh" "Health Check Validation"; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    total=$((total + 1))
    echo ""
    
    # 2. CI/CD Validation
    if run_validation "${SCRIPT_DIR}/cicd_validation.sh" "CI/CD Pipeline Validation"; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    total=$((total + 1))
    echo ""
    
    # 3. Auto-Scaling Validation
    if run_validation "${SCRIPT_DIR}/autoscaling_validation.sh" "Auto-Scaling Validation"; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    total=$((total + 1))
    echo ""
    
    # 4. Load Balancer Validation
    if run_validation "${SCRIPT_DIR}/load_balancer_validation.sh" "Load Balancer Validation"; then
        passed=$((passed + 1))
    else
        failed=$((failed + 1))
    fi
    total=$((total + 1))
    echo ""
    
    # Summary
    print_section "Validation Summary"
    print_info "Total tests: ${total}"
    print_info "Passed: ${passed}"
    if [ $failed -gt 0 ]; then
        print_error "Failed: ${failed}"
        print_info "Completed at: $(date)"
        exit 1
    else
        print_info "Failed: ${failed}"
        print_info "All validations passed! ✓"
        print_info "Completed at: $(date)"
        exit 0
    fi
}

# Run main function
main "$@"

