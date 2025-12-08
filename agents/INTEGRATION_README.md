# Agent Cloud Integration

This document describes the cloud integration adapters for connecting agents to simulated cloud infrastructure (LocalStack and Kubernetes).

## Overview

The integration layer provides adapters for:
- **Self-Healing Agent**: Kubernetes pod operations and AWS Lambda invocation
- **Scaling Agent**: Kubernetes scaling operations with prediction
- **Performance Monitoring Agent**: Prometheus metrics collection and anomaly detection
- **Security Agent**: Cloud security misconfiguration detection and IAM policy validation

## Dependencies

### Go Dependencies

The following Go packages need to be added to `go.mod`:

```bash
go get k8s.io/client-go@latest
go get k8s.io/api@latest
go get github.com/aws/aws-sdk-go@latest
go mod tidy
```

Required packages:
- `k8s.io/client-go` - Kubernetes client library
- `k8s.io/api` - Kubernetes API types
- `github.com/aws/aws-sdk-go` - AWS SDK for Lambda operations

### Python Dependencies

For the security agent, install:

```bash
pip install boto3
```

## Files

### 1. `/agents/self-healing/cloud_adapter.go`

Provides cloud operations for the Self-Healing Agent:

- **RestartPod(name string)**: Restarts a pod by deleting it (Kubernetes recreates it)
- **RollbackDeployment(name string)**: Rolls back a deployment to previous revision
- **ReplacePod(name string)**: Replaces a failed pod
- **CallLambda(functionName string)**: Invokes AWS Lambda function via LocalStack
- **HealExplanation()**: Returns structured reasoning for healing actions

**Usage:**
```go
adapter, err := NewCloudAdapter()
if err != nil {
    log.Fatal(err)
}

// Restart a pod
err = adapter.RestartPod("compute-service-abc123")

// Rollback deployment
err = adapter.RollbackDeployment("compute-service")

// Invoke Lambda
err = adapter.CallLambda("self-healing-test-lambda")
```

### 2. `/agents/scaling/k8s_scaling.go`

Provides Kubernetes scaling operations:

- **GetCurrentReplicas(serviceName)**: Gets current replica count
- **SetReplicas(serviceName, replicas)**: Sets replica count
- **PredictAndScale()**: Predicts load and scales services automatically

**Usage:**
```go
scaling, err := NewK8sScaling()
if err != nil {
    log.Fatal(err)
}

// Get current replicas
replicas, err := scaling.GetCurrentReplicas("compute-service")

// Set replicas
err = scaling.SetReplicas("compute-service", 5)

// Predict and scale
err = scaling.PredictAndScale()
```

### 3. `/agents/performance-monitoring/metrics_adapter.go`

Provides Prometheus metrics integration:

- **ConnectToPrometheus()**: Verifies connection to Prometheus
- **FetchMetrics()**: Fetches metrics from Prometheus
- **DetectAnomaly(metrics)**: Detects anomalies in metrics

**Usage:**
```go
adapter, err := NewPrometheusAdapter()
if err != nil {
    log.Fatal(err)
}

// Connect
err = adapter.ConnectToPrometheus()

// Fetch metrics
metrics, err := adapter.FetchMetrics()

// Detect anomalies
anomalies, err := adapter.DetectAnomaly(metrics)
```

### 4. `/agents/security/cloud_security.py`

Provides cloud security operations:

- **detect_security_misconfig(resource_type)**: Detects security misconfigurations
- **validate_iam_policy(policy_document)**: Validates IAM policies
- **analyze_request_logs(log_group, hours)**: Analyzes CloudWatch logs for threats

**Usage:**
```python
from cloud_security import CloudSecurityAdapter

adapter = CloudSecurityAdapter()

# Detect misconfigurations
misconfigs = adapter.detect_security_misconfig("all")

# Validate IAM policy
policy = {...}
validation = adapter.validate_iam_policy(policy)

# Analyze logs
analysis = adapter.analyze_request_logs("/aws/lambda/test", hours=24)
```

## Environment Variables

### Kubernetes

- `KUBERNETES_NAMESPACE`: Namespace to operate in (default: `self-healing-cloud`)
- `KUBECONFIG`: Path to kubeconfig file (default: `~/.kube/config`)

### AWS/LocalStack

- `AWS_ENDPOINT_URL`: LocalStack endpoint (default: `http://localhost:4566`)
- `AWS_DEFAULT_REGION`: AWS region (default: `us-east-1`)
- `AWS_ACCESS_KEY_ID`: AWS access key (default: `test` for LocalStack)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (default: `test` for LocalStack)

### Prometheus

- `PROMETHEUS_URL`: Prometheus server URL (default: `http://localhost:9090`)

## Integration with Agents

### Self-Healing Agent

Update `heal.go` to use `CloudAdapter`:

```go
import "github.com/ai-driven-self-healing-cloud/agents/self-healing"

// In Healer struct
cloudAdapter *CloudAdapter

// In Heal method
if h.cloudAdapter == nil {
    h.cloudAdapter, _ = NewCloudAdapter()
}

// Use adapter
switch action {
case "restart":
    h.cloudAdapter.RestartPod(request.ServiceID)
case "rollback":
    h.cloudAdapter.RollbackDeployment(request.ServiceID)
case "replace":
    h.cloudAdapter.ReplacePod(request.ServiceID)
}
```

### Scaling Agent

Update `autoscale.go` to use `K8sScaling`:

```go
import "github.com/ai-driven-self-healing-cloud/agents/scaling"

// In AutoScaler struct
k8sScaling *K8sScaling

// In ScaleUp/ScaleDown methods
if as.k8sScaling == nil {
    as.k8sScaling, _ = NewK8sScaling()
}

replicas, _ := as.k8sScaling.GetCurrentReplicas(serviceID)
as.k8sScaling.SetReplicas(serviceID, targetReplicas)
```

### Performance Monitoring Agent

Update `metrics.go` to use `PrometheusAdapter`:

```go
import "github.com/ai-driven-self-healing-cloud/agents/performancemonitoring"

// In MetricsAnalyzer struct
promAdapter *PrometheusAdapter

// In CollectMetrics method
if ma.promAdapter == nil {
    ma.promAdapter, _ = NewPrometheusAdapter()
}

ma.promAdapter.ConnectToPrometheus()
metrics, _ := ma.promAdapter.FetchMetrics()
```

### Security Agent

Update `agent.py` to use `CloudSecurityAdapter`:

```python
from cloud_security import CloudSecurityAdapter

# In SecurityAgent class
def __init__(self):
    self.cloud_adapter = CloudSecurityAdapter()

def detect_intrusion(self, logs, network_traffic=None):
    # Use cloud adapter
    misconfigs = self.cloud_adapter.detect_security_misconfig()
    log_analysis = self.cloud_adapter.analyze_request_logs()
    # ... process results
```

## Testing

### Test Kubernetes Integration

```bash
# Ensure kubectl is configured
kubectl get nodes

# Test in namespace
export KUBERNETES_NAMESPACE=self-healing-cloud

# Run agent tests
go test ./agents/self-healing/...
go test ./agents/scaling/...
```

### Test LocalStack Integration

```bash
# Start LocalStack
cd cloud-simulation/localstack
docker-compose up -d

# Set environment variables
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Test Lambda invocation
go test ./agents/self-healing/... -run TestCloudAdapter
```

### Test Prometheus Integration

```bash
# Ensure Prometheus is running
curl http://localhost:9090/-/healthy

# Set environment variable
export PROMETHEUS_URL=http://localhost:9090

# Test metrics collection
go test ./agents/performance-monitoring/... -run TestPrometheusAdapter
```

## Troubleshooting

### Kubernetes Client Errors

- **"failed to load kubeconfig"**: Ensure `~/.kube/config` exists or set `KUBECONFIG`
- **"connection refused"**: Check if Kubernetes cluster is running
- **"unauthorized"**: Verify RBAC permissions for the service account

### LocalStack Errors

- **"connection refused"**: Ensure LocalStack is running on port 4566
- **"function not found"**: Deploy Lambda function using bootstrap script
- **"endpoint URL"**: Verify `AWS_ENDPOINT_URL` is set correctly

### Prometheus Errors

- **"connection refused"**: Ensure Prometheus is running
- **"query failed"**: Check PromQL query syntax
- **"no data"**: Verify metrics are being exported from services

## Next Steps

1. **Integrate adapters** into agent code
2. **Add error handling** and retry logic
3. **Implement caching** for frequently accessed data
4. **Add metrics** for adapter operations
5. **Create unit tests** for each adapter
6. **Document API** endpoints and parameters

