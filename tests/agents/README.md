# Agent Unit Tests

This directory contains unit tests for all agents in the system. Each agent has comprehensive tests covering core functionalities, error handling, and explanation generation.

## Test Files

### Go Agents

1. **Self-Healing Agent** (`self_healing_agent_test.go`)
   - Health check verification
   - Self-healing action triggering
   - Service restart simulation
   - Error handling
   - Explanation generation

2. **Scaling Agent** (`scaling_agent_test.go`)
   - Scaling logic verification
   - Scale up on high load
   - Scale down on low load
   - No scaling on normal load
   - Error handling
   - Explanation generation

3. **Task-Solving Agent** (`task_solving_agent_test.go`)
   - User request parsing
   - Task generation
   - Task delegation to correct agents
   - Error handling
   - Explanation generation

4. **Performance Monitoring Agent** (`monitoring_agent_test.go`)
   - Metrics fetching from Prometheus
   - Anomaly detection
   - Threshold violation detection
   - Metrics collection
   - Explanation generation

### Python Agents

5. **Coding Agent** (`coding_agent_test.py`)
   - Code generation
   - Code fixing with broken code
   - Stacktrace analysis
   - Multiple language support
   - Error handling
   - Explanation generation

6. **Security Agent** (`security_agent_test.py`)
   - Intrusion detection
   - Security breach blocking
   - Multiple failed login detection
   - Suspicious IP detection
   - Network traffic analysis
   - Dependency graph analysis
   - Explanation generation

7. **Optimization Agent** (`optimization_agent_test.py`)
   - Cost optimization recommendations
   - Underutilized resource detection
   - Rightsizing recommendations
   - Idle resource detection
   - Cost savings calculation
   - Multiple optimization strategies
   - Explanation generation

## Running Tests

### Run All Go Agent Tests

```bash
go test -v ./tests/agents/...
```

### Run Specific Agent Tests

```bash
# Self-Healing Agent
go test -v ./tests/agents -run TestSelfHealing

# Scaling Agent
go test -v ./tests/agents -run TestScaling

# Task-Solving Agent
go test -v ./tests/agents -run TestTaskSolving

# Monitoring Agent
go test -v ./tests/agents -run TestMonitoring
```

### Run Python Agent Tests

```bash
# Coding Agent
python -m pytest tests/agents/coding_agent_test.py -v

# Security Agent
python -m pytest tests/agents/security_agent_test.py -v

# Optimization Agent
python -m pytest tests/agents/optimization_agent_test.py -v

# All Python tests
python -m pytest tests/agents/*_test.py -v
```

### Run with Coverage

```bash
# Go tests
go test -v ./tests/agents/... -coverprofile=coverage.out
go tool cover -html=coverage.out

# Python tests
python -m pytest tests/agents/ --cov=agents --cov-report=html
```

## Test Coverage

### Self-Healing Agent
- ✅ Health check
- ✅ Self-healing action
- ✅ Service restart
- ✅ Error handling
- ✅ Explanation generation

### Scaling Agent
- ✅ Scaling logic
- ✅ Scale up
- ✅ Scale down
- ✅ No scaling
- ✅ Error handling
- ✅ Explanation generation

### Task-Solving Agent
- ✅ Request parsing
- ✅ Task generation
- ✅ Agent delegation
- ✅ Error handling
- ✅ Explanation generation

### Monitoring Agent
- ✅ Metrics fetching
- ✅ Anomaly detection
- ✅ Threshold violations
- ✅ Metrics collection
- ✅ Explanation generation

### Coding Agent
- ✅ Code generation
- ✅ Code fixing
- ✅ Stacktrace analysis
- ✅ Multiple languages
- ✅ Error handling
- ✅ Explanation generation

### Security Agent
- ✅ Intrusion detection
- ✅ Breach blocking
- ✅ Failed login detection
- ✅ Suspicious IP detection
- ✅ Network analysis
- ✅ Explanation generation

### Optimization Agent
- ✅ Cost optimization
- ✅ Underutilized resources
- ✅ Rightsizing
- ✅ Idle resources
- ✅ Savings calculation
- ✅ Explanation generation

## Expected Results

All tests should pass:
- ✅ Self-Healing Agent: 8/8 tests
- ✅ Scaling Agent: 7/7 tests
- ✅ Task-Solving Agent: 6/6 tests
- ✅ Monitoring Agent: 6/6 tests
- ✅ Coding Agent: 8/8 tests
- ✅ Security Agent: 9/9 tests
- ✅ Optimization Agent: 9/9 tests

**Total: 53/53 tests passing**

## Dependencies

### Go Tests
- `github.com/stretchr/testify/assert`
- `github.com/stretchr/testify/require`

### Python Tests
- `unittest` (built-in)
- `pytest` (optional, for better output)

## Test Structure

Each test file follows this structure:

1. **Setup/Teardown**: Initialize and clean up agent instances
2. **Health Check Tests**: Verify agent health status
3. **Core Functionality Tests**: Test main agent features
4. **Error Handling Tests**: Test error scenarios
5. **Explanation Tests**: Verify explanation generation

## Next Steps

1. Run all tests to verify functionality
2. Add integration tests for agent interactions
3. Add performance tests for load scenarios
4. Integrate with CI/CD pipeline

