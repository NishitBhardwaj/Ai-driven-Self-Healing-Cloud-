#!/bin/bash

# Phase 7 Test Runner
# Runs all Phase 7 tests and generates a summary report

set -e

echo "=========================================="
echo "Phase 7 Testing & Validation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
WEBSOCKET_PASSED=0
WEBSOCKET_FAILED=0
DECISION_PASSED=0
DECISION_FAILED=0
API_PASSED=0
API_FAILED=0
EXPLAINABILITY_PASSED=0
EXPLAINABILITY_FAILED=0

# Run WebSocket tests
echo "Running WebSocket tests..."
if go test -v ./tests/phase7 -run TestWebSocket 2>&1 | tee websocket_test.log; then
    WEBSOCKET_PASSED=$(grep -c "PASS:" websocket_test.log || echo "0")
    echo -e "${GREEN}✓ WebSocket tests passed${NC}"
else
    WEBSOCKET_FAILED=$(grep -c "FAIL:" websocket_test.log || echo "0")
    echo -e "${RED}✗ WebSocket tests failed${NC}"
fi
echo ""

# Run Decision UI tests
echo "Running Decision UI tests..."
if go test -v ./tests/phase7 -run TestDecision 2>&1 | tee decision_test.log; then
    DECISION_PASSED=$(grep -c "PASS:" decision_test.log || echo "0")
    echo -e "${GREEN}✓ Decision UI tests passed${NC}"
else
    DECISION_FAILED=$(grep -c "FAIL:" decision_test.log || echo "0")
    echo -e "${RED}✗ Decision UI tests failed${NC}"
fi
echo ""

# Run API tests
echo "Running API tests..."
if go test -v ./tests/phase7 -run TestAPI 2>&1 | tee api_test.log; then
    API_PASSED=$(grep -c "PASS:" api_test.log || echo "0")
    echo -e "${GREEN}✓ API tests passed${NC}"
else
    API_FAILED=$(grep -c "FAIL:" api_test.log || echo "0")
    echo -e "${RED}✗ API tests failed${NC}"
fi
echo ""

# Run Explainability tests
echo "Running Explainability tests..."
if go test -v ./tests/phase7 -run TestExplanation 2>&1 | tee explainability_test.log; then
    EXPLAINABILITY_PASSED=$(grep -c "PASS:" explainability_test.log || echo "0")
    echo -e "${GREEN}✓ Explainability tests passed${NC}"
else
    EXPLAINABILITY_FAILED=$(grep -c "FAIL:" explainability_test.log || echo "0")
    echo -e "${RED}✗ Explainability tests failed${NC}"
fi
echo ""

# Generate summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "WebSocket Tests:"
echo "  Passed: $WEBSOCKET_PASSED"
echo "  Failed: $WEBSOCKET_FAILED"
echo ""
echo "Decision UI Tests:"
echo "  Passed: $DECISION_PASSED"
echo "  Failed: $DECISION_FAILED"
echo ""
echo "API Tests:"
echo "  Passed: $API_PASSED"
echo "  Failed: $API_FAILED"
echo ""
echo "Explainability Tests:"
echo "  Passed: $EXPLAINABILITY_PASSED"
echo "  Failed: $EXPLAINABILITY_FAILED"
echo ""

TOTAL_PASSED=$((WEBSOCKET_PASSED + DECISION_PASSED + API_PASSED + EXPLAINABILITY_PASSED))
TOTAL_FAILED=$((WEBSOCKET_FAILED + DECISION_FAILED + API_FAILED + EXPLAINABILITY_FAILED))

echo "Total:"
echo "  Passed: $TOTAL_PASSED"
echo "  Failed: $TOTAL_FAILED"
echo ""

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the logs.${NC}"
    exit 1
fi

