# Cloud Simulation Test Suite

This directory contains integration tests for cloud simulation services (LocalStack and Minikube).

## Overview

The test suite verifies:
- **LocalStack Integration**: S3 bucket operations and Lambda function invocations
- **Kubernetes Scaling**: Deployment creation, HPA configuration, and autoscaling events
- **Failure Injection**: Service crash simulation and self-healing agent reactions

## Prerequisites

### LocalStack
- LocalStack must be running on `http://localhost:4566`
- Lambda function `self-healing-test-lambda` must be deployed (run bootstrap script)

### Kubernetes/Minikube
- Minikube cluster must be running
- `kubectl` must be configured to access the cluster
- Namespace `self-healing-cloud` should exist (created by minikube setup)

### Environment Variables

```bash
# LocalStack
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

# Kubernetes
export KUBECONFIG=~/.kube/config
export KUBERNETES_NAMESPACE=self-healing-cloud
```

## Test Files

### 1. `localstack_connect_test.go`

Tests LocalStack connectivity and AWS service operations.

**Tests:**
- `TestLocalStackConnection` - Verifies LocalStack is accessible
- `TestS3BucketCreation` - Tests S3 bucket creation, listing, and object operations
- `TestLambdaInvocation` - Tests Lambda function invocation
- `TestS3OperationsComprehensive` - Comprehensive S3 operations test

**Run:**
```bash
go test -v ./tests/cloud -run TestLocalStack
```

### 2. `minikube_scaling_test.go`

Tests Kubernetes deployment and autoscaling operations.

**Tests:**
- `TestKubernetesConnection` - Verifies Kubernetes cluster is accessible
- `TestDeploymentCreation` - Tests deployment creation and readiness
- `TestHPACreation` - Tests HPA creation and configuration
- `TestAutoscalingEvent` - Tests scaling up and down
- `TestHPAStatus` - Verifies HPA status and metrics

**Run:**
```bash
go test -v ./tests/cloud -run TestMinikube
```

### 3. `failure_injection_test.go`

Tests failure injection and self-healing capabilities.

**Tests:**
- `TestServiceCrashSimulation` - Simulates pod crash and verifies recovery
- `TestSelfHealingAgentReaction` - Tests Self-Healing Agent response to failures
- `TestMultipleFailureScenarios` - Tests various failure scenarios

**Run:**
```bash
go test -v ./tests/cloud -run TestFailure
```

## Running Tests

### Run All Cloud Tests

```bash
cd tests/cloud
go test -v
```

### Run Specific Test Suite

```bash
# LocalStack tests only
go test -v -run TestLocalStack

# Kubernetes tests only
go test -v -run TestKubernetes

# Failure injection tests only
go test -v -run TestServiceCrash
```

### Run with Coverage

```bash
go test -v -cover ./tests/cloud
go test -v -coverprofile=coverage.out ./tests/cloud
go tool cover -html=coverage.out
```

### Skip Integration Tests

```bash
# Run only unit tests (skip integration tests)
go test -v -short ./tests/cloud
```

## Test Setup

### 1. Start LocalStack

```bash
cd cloud-simulation/localstack
docker-compose up -d
./bootstrap.sh
```

### 2. Start Minikube

```bash
cd kubernetes/minikube
./start_minikube.sh
kubectl apply -f namespace.yaml
```

### 3. Deploy Test Services

```bash
# Deploy mock services to Minikube
kubectl apply -f deployments/ -R
```

## Test Execution Flow

### LocalStack Tests

1. **Connection Test**: Verifies LocalStack is running
2. **S3 Tests**: Creates bucket, uploads objects, lists buckets
3. **Lambda Tests**: Invokes Lambda function and verifies response

### Kubernetes Tests

1. **Connection Test**: Verifies Kubernetes cluster is accessible
2. **Deployment Test**: Creates deployment and waits for readiness
3. **HPA Test**: Creates HPA and verifies configuration
4. **Scaling Test**: Triggers scaling events and verifies pod count changes

### Failure Injection Tests

1. **Crash Simulation**: Deletes a pod to simulate crash
2. **Recovery Verification**: Waits for pod to be recreated
3. **Agent Reaction**: Tests Self-Healing Agent response

## Expected Results

### LocalStack Tests

- ✅ LocalStack health check passes
- ✅ S3 bucket created successfully
- ✅ Objects uploaded and retrieved correctly
- ✅ Lambda function invokes and returns response

### Kubernetes Tests

- ✅ Kubernetes cluster accessible
- ✅ Deployment created with 2 replicas
- ✅ HPA created with min=2, max=10
- ✅ Scaling events trigger pod count changes
- ✅ HPA status shows current/desired replicas

### Failure Injection Tests

- ✅ Pod deletion simulates crash
- ✅ Deployment recreates pod automatically
- ✅ Self-Healing Agent processes healing requests
- ✅ CloudAdapter successfully restarts pods

## Troubleshooting

### LocalStack Not Available

```
Error: LocalStack not available at http://localhost:4566
```

**Solution:**
```bash
# Start LocalStack
cd cloud-simulation/localstack
docker-compose up -d

# Verify it's running
curl http://localhost:4566/_localstack/health
```

### Kubernetes Not Available

```
Error: Kubernetes not available
```

**Solution:**
```bash
# Start Minikube
minikube start

# Verify kubectl works
kubectl get nodes

# Set KUBECONFIG if needed
export KUBECONFIG=~/.kube/config
```

### Lambda Function Not Found

```
Error: Lambda function self-healing-test-lambda not found
```

**Solution:**
```bash
# Run bootstrap script to deploy Lambda
cd cloud-simulation/localstack
./bootstrap.sh
```

### Pod Not Recreating

If pods don't recreate after deletion:
- Check deployment replicas: `kubectl get deployment -n self-healing-cloud`
- Check pod status: `kubectl get pods -n self-healing-cloud`
- Check events: `kubectl get events -n self-healing-cloud`

### Test Timeouts

If tests timeout:
- Increase timeout values in test files
- Check resource availability (CPU, memory)
- Verify services are running correctly

## Continuous Integration

### GitHub Actions Example

```yaml
name: Cloud Simulation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-go@v2
        with:
          go-version: '1.21'
      
      - name: Start LocalStack
        run: |
          cd cloud-simulation/localstack
          docker-compose up -d
          ./bootstrap.sh
      
      - name: Start Minikube
        run: |
          minikube start
          kubectl apply -f kubernetes/minikube/namespace.yaml
      
      - name: Run Tests
        run: |
          export AWS_ENDPOINT_URL=http://localhost:4566
          go test -v ./tests/cloud
```

## Test Data Cleanup

Tests automatically clean up resources, but manual cleanup may be needed:

```bash
# Clean up Kubernetes resources
kubectl delete deployment test-* -n self-healing-cloud
kubectl delete hpa test-* -n self-healing-cloud

# Clean up LocalStack resources
aws --endpoint-url=http://localhost:4566 s3 rb s3://test-bucket-cloud-simulation --force
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test resources
3. **Timeouts**: Use appropriate timeouts for async operations
4. **Skip Logic**: Skip tests if prerequisites aren't met
5. **Logging**: Use `t.Logf()` for debugging information

## Related Documentation

- [LocalStack Setup](../../cloud-simulation/localstack/README.md)
- [Minikube Setup](../../kubernetes/minikube/README.md)
- [Agent Integration](../../agents/INTEGRATION_README.md)
- [Docker Compose Simulation](../../docker/docker-compose.simulation.README.md)

