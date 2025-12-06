# Tests Directory

This folder contains test suites for the multi-agent system, including unit tests, integration tests, and end-to-end tests. Comprehensive testing ensures system reliability, correctness, and performance.

## Overview

The test suite is organized into:

- **`/tests/unit/`**: Unit tests for individual agents and components
- **`/tests/integration/`**: Integration tests for agent communication and interactions
- **`/tests/e2e/`**: End-to-end tests for complete system workflows

## Test Structure

```
tests/
├── unit/
│   ├── agents/
│   │   ├── test_self_healing_agent.py
│   │   ├── test_scaling_agent.py
│   │   └── ...
│   └── utils/
│       └── test_helpers.py
├── integration/
│   ├── test_agent_communication.py
│   ├── test_cloud_interactions.py
│   └── test_message_queue.py
└── e2e/
    ├── test_user_workflows.py
    ├── test_failure_recovery.py
    └── test_scaling_scenarios.py
```

## Unit Tests

Unit tests verify individual components and functions in isolation.

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/agents/test_self_healing_agent.py

# Run with coverage
pytest tests/unit/ --cov=agents --cov-report=html
```

### Example Unit Test

```python
import pytest
from agents.self_healing.self_healing_agent import SelfHealingAgent

def test_detect_failure():
    agent = SelfHealingAgent()
    result = agent.detect_failure({
        'cpu_usage': 95,
        'memory_usage': 90,
        'status': 'unhealthy'
    })
    assert result == True

def test_recover_from_failure():
    agent = SelfHealingAgent()
    result = agent.recover_from_failure('service-crash')
    assert result['status'] == 'recovered'
```

## Integration Tests

Integration tests verify that agents work together correctly.

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run with Docker Compose (for local services)
docker-compose -f docker/docker-compose/docker-compose.test.yml up -d
pytest tests/integration/
docker-compose -f docker/docker-compose/docker-compose.test.yml down
```

### Example Integration Test

```python
import pytest
from agents.task_solving.task_solving_agent import TaskSolvingAgent
from agents.scaling.scaling_agent import ScalingAgent

@pytest.fixture
def task_agent():
    return TaskSolvingAgent()

@pytest.fixture
def scaling_agent():
    return ScalingAgent()

def test_task_delegation(task_agent, scaling_agent):
    task = {'type': 'scale_up', 'resources': 2}
    result = task_agent.delegate_task(task, scaling_agent)
    assert result['status'] == 'completed'
    assert scaling_agent.get_resource_count() == 2
```

## End-to-End Tests

End-to-end tests verify complete system workflows from user request to completion.

### Running E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/

# Run with Kubernetes (for production-like environment)
pytest tests/e2e/ --kubernetes --namespace test
```

### Example E2E Test

```python
import pytest
import requests

def test_file_upload_workflow():
    # User uploads file
    response = requests.post(
        'http://localhost:8080/api/upload',
        files={'file': open('test.txt', 'rb')}
    )
    assert response.status_code == 200
    
    # Verify file in storage
    file_exists = check_file_in_storage('test.txt')
    assert file_exists == True
    
    # Verify task completion
    task_status = get_task_status(response.json()['task_id'])
    assert task_status == 'completed'
```

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=agents
    --cov-report=html
    --cov-report=term
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### conftest.py

Shared fixtures and configuration:

```python
import pytest
import docker

@pytest.fixture(scope='session')
def docker_client():
    return docker.from_env()

@pytest.fixture
def test_database():
    # Setup test database
    db = create_test_database()
    yield db
    # Teardown
    db.drop_all()
```

## Test Data

Test data and fixtures are managed separately:

- **`fixtures/`**: Test data files
- **`mocks/`**: Mock objects and services
- **`helpers/`**: Test helper functions

## Test Coverage

### Coverage Goals

- **Unit Tests**: >90% coverage
- **Integration Tests**: >70% coverage
- **E2E Tests**: Cover all critical workflows

### Generating Coverage Reports

```bash
# HTML report
pytest --cov=agents --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=agents --cov-report=term

# XML report (for CI/CD)
pytest --cov=agents --cov-report=xml
```

## Test Environments

### Local Testing

```bash
# Start test services
docker-compose -f docker/docker-compose/docker-compose.test.yml up -d

# Run tests
pytest tests/

# Stop test services
docker-compose -f docker/docker-compose/docker-compose.test.yml down
```

### CI/CD Testing

Tests run automatically in CI/CD pipeline:

```yaml
# .gitlab-ci.yml
test:
  stage: test
  script:
    - pytest tests/unit/
    - pytest tests/integration/
    - pytest tests/e2e/
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Performance Testing

### Load Tests

```bash
# Run load tests
pytest tests/performance/test_load.py --load --users 100 --duration 5m
```

### Stress Tests

```bash
# Run stress tests
pytest tests/performance/test_stress.py --stress --max-load 1000
```

## Test Best Practices

1. **Isolation**: Tests should be independent and not rely on each other
2. **Fast Execution**: Unit tests should run quickly (<1 second each)
3. **Deterministic**: Tests should produce consistent results
4. **Clear Names**: Test names should clearly describe what they test
5. **Arrange-Act-Assert**: Follow AAA pattern in test structure
6. **Mock External Services**: Don't rely on external services in unit tests
7. **Test Edge Cases**: Test both happy paths and error cases

## Continuous Testing

### Watch Mode

Run tests automatically on file changes:

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/
```

### Pre-commit Hooks

Run tests before committing:

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install
```

## Troubleshooting

### Tests Failing

- Check test logs: `pytest -v --tb=short`
- Verify test environment setup
- Check dependencies and fixtures
- Review test data and mocks

### Slow Tests

- Identify slow tests: `pytest --durations=10`
- Optimize database queries
- Use test doubles instead of real services
- Parallelize test execution: `pytest -n auto`

### Flaky Tests

- Add retries for flaky tests: `@pytest.mark.flaky(reruns=3)`
- Fix timing issues with proper waits
- Ensure test isolation

## Related Documentation

- Agent development: `/agents/README.md`
- CI/CD pipeline: `/ci-cd/README.md`
- Docker setup: `/docker/README.md`

