# Phase 7 Testing & Validation

This directory contains comprehensive tests for Phase 7 components including WebSocket real-time updates, Decision UI, API endpoints, and Explainability Layer.

## Test Files

### 0. System Consistency Tests (`system_consistency_test.go`)

**Comprehensive system validation** that ensures all Phase 7 components work together:

- `TestSystemConsistency`: Runs all consistency checks
- `TestAutoModeExecution`: Validates Auto Mode executes automatically with explanations
- `TestManualModeUserInput`: Validates Manual Mode shows options and waits for input
- `TestExplainabilityConsistency`: Validates Explainability Layer across all agents
- `TestWebSocketRealTimeUpdates`: Validates WebSocket pushes real-time updates
- `TestBackendAPIData`: Validates all backend APIs return correct data
- `TestDashboardInteractivity`: Validates Dashboard updates dynamically
- `TestFullSystemIntegration`: Tests complete system workflow

**Run:**
```bash
go test -v ./tests/phase7 -run TestSystemConsistency

# Or use the consistency check script
./tests/phase7/consistency_check.sh  # Linux/Mac
tests\phase7\consistency_check.bat    # Windows
```

### 1. WebSocket Tests (`websocket_test.go`)

Tests WebSocket functionality for real-time agent status updates:

- `TestWebSocketConnection`: Tests WebSocket connection establishment
- `TestWebSocketAgentStatusUpdate`: Tests real-time agent status updates
- `TestWebSocketSystemHealthUpdate`: Tests system health updates
- `TestWebSocketLogEntry`: Tests log entry updates
- `TestWebSocketMessageFormat`: Tests message format validation

**Run:**
```bash
go test -v ./tests/phase7 -run TestWebSocket
```

### 2. Decision UI Tests (`decision_ui_test.go`)

Tests Decision UI for Auto and Manual modes:

- `TestAutoModeDecision`: Tests Auto Mode decision execution
- `TestManualModeDecision`: Tests Manual Mode decision with user approval
- `TestDecisionUIExplanationFormat`: Tests explanation format in UI
- `TestAutoModeNoUserInput`: Tests that Auto Mode doesn't require user input
- `TestManualModeShowsOptions`: Tests that Manual Mode shows available options

**Run:**
```bash
go test -v ./tests/phase7 -run TestDecision
```

### 3. API Tests (`api_test.go`)

Tests REST API endpoints:

- `TestAgentStatusAPI`: Tests GET /api/agents/status
- `TestAgentStatusAPIWithExplanation`: Tests that explanations are included
- `TestLogsAPI`: Tests GET /api/agents/logs
- `TestLogsAPIWithFilters`: Tests logs API with query parameters
- `TestLogsAPIExplanationFormat`: Tests explanation format in logs
- `TestDecisionHistoryAPI`: Tests GET /api/agents/decision-history
- `TestDecisionHistoryAPIWithFilters`: Tests decision history with filters
- `TestDecisionHistoryExplanationFormat`: Tests explanation format in decision history
- `TestAPICORS`: Tests CORS headers
- `TestAPIHealthCheck`: Tests health check endpoint

**Run:**
```bash
go test -v ./tests/phase7 -run TestAPI
```

### 4. Explainability Tests (`explainability_test.go`)

Tests Explainability Layer for all agents:

- `TestSelfHealingAgentExplanation`: Tests Self-Healing Agent explanation
- `TestScalingAgentExplanation`: Tests Scaling Agent explanation
- `TestSecurityAgentExplanation`: Tests Security Agent explanation
- `TestMonitoringAgentExplanation`: Tests Performance Monitoring Agent explanation
- `TestExplanationFormatConsistency`: Tests that all explanations follow the same format
- `TestAutoModeMessage`: Tests auto mode message format
- `TestExplanationWithContext`: Tests explanation with context
- `TestExplanationHumanReadable`: Tests that explanations are human-readable
- `TestPythonAgentExplanationFormat`: Tests Python agent explanation format
- `TestExplanationReasoningChain`: Tests reasoning chain in explanations
- `TestExplanationConfidence`: Tests confidence levels in explanations

**Run:**
```bash
go test -v ./tests/phase7 -run TestExplanation
```

## Running All Tests

### Run all Phase 7 tests:
```bash
go test -v ./tests/phase7/...
```

### Run System Consistency Check:
```bash
# Linux/Mac
./tests/phase7/consistency_check.sh

# Windows
tests\phase7\consistency_check.bat

# Or directly
go test -v ./tests/phase7 -run TestSystemConsistency
```

### Run specific test suite:
```bash
# WebSocket tests
go test -v ./tests/phase7 -run TestWebSocket

# Decision UI tests
go test -v ./tests/phase7 -run TestDecision

# API tests
go test -v ./tests/phase7 -run TestAPI

# Explainability tests
go test -v ./tests/phase7 -run TestExplanation
```

### Run with coverage:
```bash
go test -v ./tests/phase7/... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

## Test Requirements

### Dependencies

Install required Go packages:
```bash
go get github.com/stretchr/testify/assert
go get github.com/stretchr/testify/require
go get github.com/gorilla/websocket
```

### Prerequisites

1. **API Server**: The API tests require the API server to be running or use test servers
2. **WebSocket Server**: WebSocket tests use test servers (no external server needed)
3. **Agent Registry**: Tests use mock registries for agent status tests

## Test Coverage

### WebSocket Tests
- ✅ Connection establishment
- ✅ Real-time updates
- ✅ Message format validation
- ✅ System health updates
- ✅ Log entry updates

### Decision UI Tests
- ✅ Auto Mode execution
- ✅ Manual Mode with user approval
- ✅ Explanation format
- ✅ Option display
- ✅ No user input required for Auto Mode

### API Tests
- ✅ Agent Status API
- ✅ Logs API
- ✅ Decision History API
- ✅ Query parameters and filters
- ✅ CORS headers
- ✅ Explanation format in responses

### Explainability Tests
- ✅ All agent explanations
- ✅ Format consistency
- ✅ Human-readable format
- ✅ Confidence levels
- ✅ Reasoning chains

## Expected Test Results

All tests should pass with:
- ✅ System Consistency: 8/8 tests passing
- ✅ WebSocket: 5/5 tests passing
- ✅ Decision UI: 5/5 tests passing
- ✅ API: 10/10 tests passing
- ✅ Explainability: 11/11 tests passing

**Total: 39/39 tests passing**

## Troubleshooting

### WebSocket Connection Errors
- Ensure test server is properly configured
- Check WebSocket URL format (ws:// vs http://)

### API Test Failures
- Verify API routes are properly registered
- Check that handlers are correctly initialized
- Ensure CORS middleware is applied

### Explanation Format Errors
- Verify all agents use `FormatExplanation` helper
- Check that explanations follow the standard format
- Ensure explanations end with a period

## Next Steps

After running tests:
1. Fix any failing tests
2. Review test coverage
3. Add additional edge case tests
4. Integrate with CI/CD pipeline

