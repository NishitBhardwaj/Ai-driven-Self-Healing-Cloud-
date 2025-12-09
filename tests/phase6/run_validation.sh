#!/bin/bash

# Phase 6 Full System Validation Script
# This script runs all validation tests for Phase 6

echo "=========================================="
echo "Phase 6 - Full System Validation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    if eval "$test_command"; then
        echo -e "${GREEN}✓ ${test_name}: PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ ${test_name}: FAILED${NC}"
        ((FAILED++))
        return 1
    fi
    echo ""
}

# 1. Test Go validation tests
echo "1. Running Go Validation Tests"
echo "-------------------------------"
if command -v go &> /dev/null; then
    run_test "Auto Mode Validation" "cd tests/phase6 && go test -v -run TestAutoModeValidation"
    run_test "Manual Mode Validation" "cd tests/phase6 && go test -v -run TestManualModeValidation"
    run_test "Explanation Human-Readable" "cd tests/phase6 && go test -v -run TestExplanationHumanReadable"
    run_test "Logging Validation" "cd tests/phase6 && go test -v -run TestLoggingValidation"
    run_test "UI Dynamic Updates" "cd tests/phase6 && go test -v -run TestUIDynamicUpdates"
    run_test "Full System Integration" "cd tests/phase6 && go test -v -run TestFullSystemIntegration"
else
    echo -e "${YELLOW}⚠ Go not found, skipping Go tests${NC}"
fi
echo ""

# 2. Test JavaScript UI validation
echo "2. Running JavaScript UI Validation Tests"
echo "-----------------------------------------"
if command -v node &> /dev/null; then
    run_test "UI Validation Tests" "node tests/phase6/ui_validation_test.js"
else
    echo -e "${YELLOW}⚠ Node.js not found, skipping JavaScript tests${NC}"
fi
echo ""

# 3. Check file structure
echo "3. Checking File Structure"
echo "--------------------------"
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 missing${NC}"
        return 1
    fi
}

check_file "agents/core/decision_mode.go"
check_file "agents/core/xai.go"
check_file "agents/core/xai_logger.go"
check_file "agents/core/xai_llm_integration.go"
check_file "ui/decision-ui/index.html"
check_file "ui/decision-ui/decision-ui.js"
check_file "ui/decision-ui/decision-api.js"
check_file "ui/decision-ui/styles.css"
echo ""

# 4. Check log directory
echo "4. Checking Log Directory"
echo "-------------------------"
if [ -d "logs/xai" ]; then
    echo -e "${GREEN}✓ Log directory exists${NC}"
    LOG_COUNT=$(find logs/xai -name "*.log" 2>/dev/null | wc -l)
    echo "  Found $LOG_COUNT log file(s)"
else
    echo -e "${YELLOW}⚠ Log directory does not exist (will be created on first log)${NC}"
fi
echo ""

# 5. Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validation tests PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some validation tests FAILED${NC}"
    exit 1
fi

