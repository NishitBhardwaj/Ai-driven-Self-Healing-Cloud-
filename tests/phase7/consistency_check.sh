#!/bin/bash

# Phase 7 System Consistency Check
# Validates all Phase 7 components work together correctly

set -e

echo "=========================================="
echo "Phase 7 System Consistency Check"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

# Check 1: Auto Mode Execution
echo "✓ Checking Auto Mode execution..."
if go test -v ./tests/phase7 -run TestAutoModeExecution 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ Auto Mode executes automatically${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ Auto Mode execution failed${NC}"
    ((FAILED++))
fi
echo ""

# Check 2: Manual Mode User Input
echo "✓ Checking Manual Mode user input..."
if go test -v ./tests/phase7 -run TestManualModeUserInput 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ Manual Mode shows options and waits${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ Manual Mode user input failed${NC}"
    ((FAILED++))
fi
echo ""

# Check 3: Explainability Consistency
echo "✓ Checking Explainability Layer consistency..."
if go test -v ./tests/phase7 -run TestExplainabilityConsistency 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ Explainability Layer is consistent${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ Explainability consistency failed${NC}"
    ((FAILED++))
fi
echo ""

# Check 4: WebSocket Real-time Updates
echo "✓ Checking WebSocket real-time updates..."
if go test -v ./tests/phase7 -run TestWebSocketRealTimeUpdates 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ WebSocket pushes real-time updates${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ WebSocket updates failed${NC}"
    ((FAILED++))
fi
echo ""

# Check 5: Backend API Data
echo "✓ Checking Backend API data..."
if go test -v ./tests/phase7 -run TestBackendAPIData 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ Backend APIs return correct data${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ Backend API data failed${NC}"
    ((FAILED++))
fi
echo ""

# Check 6: Dashboard Interactivity
echo "✓ Checking Dashboard interactivity..."
if go test -v ./tests/phase7 -run TestDashboardInteractivity 2>&1 | grep -q "PASS"; then
    echo -e "${GREEN}  ✓ Dashboard updates dynamically${NC}"
    ((PASSED++))
else
    echo -e "${RED}  ✗ Dashboard interactivity failed${NC}"
    ((FAILED++))
fi
echo ""

# Summary
echo "=========================================="
echo "Consistency Check Summary"
echo "=========================================="
echo ""
echo "Passed: $PASSED/6"
echo "Failed: $FAILED/6"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All consistency checks passed!${NC}"
    echo ""
    echo "System is ready for production!"
    exit 0
else
    echo -e "${RED}✗ Some consistency checks failed${NC}"
    echo ""
    echo "Please review the test output above."
    exit 1
fi

