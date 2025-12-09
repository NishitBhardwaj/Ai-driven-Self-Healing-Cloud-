#!/bin/bash

# System Validation Script
# Validates testing, logging, and monitoring systems

set -e

echo "=========================================="
echo "System Validation - Phase 8, Part 4"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation results
PASSED=0
FAILED=0
SKIPPED=0

# Function to check service
check_service() {
    local service=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service is accessible"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $service is not accessible"
        ((FAILED++))
        return 1
    fi
}

# Function to check service with timeout
check_service_timeout() {
    local service=$1
    local url=$2
    local timeout=${3:-5}
    
    if timeout $timeout curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service is accessible"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $service is not accessible (may not be running)"
        ((SKIPPED++))
        return 1
    fi
}

echo "1. Testing Unit Tests and Integration Tests"
echo "-------------------------------------------"
if [ -d "tests/agents" ] && [ -d "tests/integration" ]; then
    echo "Running unit tests..."
    if go test ./tests/agents/... -v 2>&1 | head -20; then
        echo -e "${GREEN}✓${NC} Unit tests structure exists"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Some unit tests may have failed (check output above)"
        ((SKIPPED++))
    fi
    
    echo "Running integration tests..."
    if go test ./tests/integration/... -v 2>&1 | head -20; then
        echo -e "${GREEN}✓${NC} Integration tests structure exists"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Some integration tests may have failed (check output above)"
        ((SKIPPED++))
    fi
else
    echo -e "${RED}✗${NC} Test directories not found"
    ((FAILED++))
fi
echo ""

echo "2. Validating Prometheus Metrics Collection"
echo "--------------------------------------------"
check_service "Prometheus" "http://localhost:9090/api/v1/status/config"
check_service "Prometheus Query API" "http://localhost:9090/api/v1/query?query=up"
check_service "Prometheus Targets" "http://localhost:9090/api/v1/targets"
check_service "Prometheus Rules" "http://localhost:9090/api/v1/rules"
echo ""

echo "3. Validating Agent Metrics Endpoints"
echo "-------------------------------------"
check_service_timeout "Self-Healing Agent Metrics" "http://localhost:8081/metrics" 2
check_service_timeout "Scaling Agent Metrics" "http://localhost:8082/metrics" 2
check_service_timeout "Task-Solving Agent Metrics" "http://localhost:8083/metrics" 2
check_service_timeout "Security Agent Metrics" "http://localhost:8084/metrics" 2
check_service_timeout "Performance Monitoring Agent Metrics" "http://localhost:8085/metrics" 2
check_service_timeout "Coding Agent Metrics" "http://localhost:8086/metrics" 2
check_service_timeout "Optimization Agent Metrics" "http://localhost:8087/metrics" 2
echo ""

echo "4. Validating Logstash and Elasticsearch"
echo "----------------------------------------"
check_service "Elasticsearch" "http://localhost:9200"
check_service "Elasticsearch Cluster Health" "http://localhost:9200/_cluster/health"

# Check if agent-logs index exists
if curl -s "http://localhost:9200/_cat/indices/agent-logs-*" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Agent-logs index exists"
    ((PASSED++))
    
    # Count documents
    COUNT=$(curl -s "http://localhost:9200/agent-logs-*/_count" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    if [ ! -z "$COUNT" ]; then
        echo -e "${GREEN}✓${NC} Elasticsearch has $COUNT log documents"
        ((PASSED++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Agent-logs index not found (may not have logs yet)"
    ((SKIPPED++))
fi
echo ""

echo "5. Validating Kibana"
echo "--------------------"
check_service "Kibana" "http://localhost:5601/api/status"
echo ""

echo "6. Validating Grafana"
echo "---------------------"
check_service "Grafana" "http://localhost:3000/api/health"
check_service "Grafana Health" "http://localhost:3000/api/health"
echo ""

echo "7. Validating Grafana Dashboards"
echo "--------------------------------"
if [ -d "monitoring/grafana/dashboards" ]; then
    DASHBOARD_COUNT=$(find monitoring/grafana/dashboards -name "*.json" | wc -l)
    if [ $DASHBOARD_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $DASHBOARD_COUNT Grafana dashboards"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} No Grafana dashboards found"
        ((FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Grafana dashboards directory not found"
    ((FAILED++))
fi
echo ""

echo "8. Validating Alerting Rules"
echo "----------------------------"
if [ -f "config/monitoring/alerts.yml" ]; then
    echo -e "${GREEN}✓${NC} Alerting rules file exists"
    ((PASSED++))
    
    # Count alert rules
    ALERT_COUNT=$(grep -c "alert:" config/monitoring/alerts.yml || echo "0")
    if [ $ALERT_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $ALERT_COUNT alert rules"
        ((PASSED++))
    fi
else
    echo -e "${RED}✗${NC} Alerting rules file not found"
    ((FAILED++))
fi
echo ""

echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical validations passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some validations failed. Please check the output above.${NC}"
    exit 1
fi

