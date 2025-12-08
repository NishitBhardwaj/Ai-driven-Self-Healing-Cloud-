# Cloud Simulation Guide

## Overview

Cloud simulation is a critical component of the AI-driven Self-Healing Cloud system, enabling local development and testing without requiring actual cloud infrastructure. This document explains why cloud simulation is important, how it integrates with the AI layers, and how to use it effectively.

## Why Cloud Simulation is Important

### Cost Efficiency

Running cloud services locally eliminates the costs associated with:
- AWS service usage (S3, Lambda, EC2, DynamoDB)
- Data transfer fees
- Compute instance costs
- Storage costs

### Development Speed

Local simulation provides:
- **Instant feedback**: No network latency to cloud services
- **Rapid iteration**: Test changes immediately without deployment delays
- **Offline development**: Work without internet connectivity
- **Faster debugging**: Direct access to logs and state

### Testing and Validation

Cloud simulation enables:
- **Reproducible tests**: Consistent environment for testing
- **Failure injection**: Simulate failures safely without impacting production
- **Integration testing**: Test agent interactions with cloud services
- **Performance testing**: Measure system behavior under various conditions

### Learning and Experimentation

Developers can:
- Experiment with cloud services without risk
- Learn AWS/Kubernetes APIs locally
- Test different configurations quickly
- Understand system behavior before production deployment

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Simulation Layer                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  LocalStack  │      │   Minikube   │                     │
│  │  (AWS Sim)   │      │  (K8s Sim)   │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                    │                               │
│         └──────────┬─────────┘                               │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │  Cloud Adapters      │                             │
│         │  (Phase 4)           │                             │
│         └──────────┬───────────┘                             │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │  AI Agents          │                             │
│         │  (Phase 5)           │                             │
│         └─────────────────────┘                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Phase 4 and Phase 5 Integration

### Phase 4: Cloud Infrastructure Layer

Phase 4 provides the **cloud adapters** that abstract cloud service interactions:

#### Components

1. **Cloud Adapters** (`/agents/*/cloud_adapter.go`, `k8s_scaling.go`, etc.)
   - Kubernetes operations (pod restart, deployment rollback, scaling)
   - AWS operations (Lambda invocation, S3 operations)
   - Prometheus metrics collection
   - Security policy validation

2. **Service Interfaces**
   - Standardized APIs for cloud operations
   - Error handling and retry logic
   - Connection management
   - Resource lifecycle management

#### Responsibilities

- **Infrastructure Abstraction**: Hide cloud provider specifics
- **Operation Execution**: Perform actual cloud operations
- **State Management**: Track resource states
- **Error Recovery**: Handle transient failures

### Phase 5: AI Intelligence Layer

Phase 5 provides the **AI agents** that make intelligent decisions:

#### Components

1. **Self-Healing Agent**
   - Detects failures using ML models
   - Decides healing strategies using reinforcement learning
   - Learns from past failures
   - Explains actions using LLM

2. **Scaling Agent**
   - Predicts load using time series models
   - Optimizes resource allocation
   - Learns scaling patterns
   - Explains scaling decisions

3. **Performance Monitoring Agent**
   - Detects anomalies using statistical models
   - Identifies performance bottlenecks
   - Learns normal behavior patterns
   - Explains anomalies

#### Responsibilities

- **Intelligent Decision Making**: Use AI/ML to make optimal decisions
- **Learning**: Continuously improve from experience
- **Explanation**: Provide human-readable reasoning
- **Adaptation**: Adjust to changing conditions

### How They Interact

```
┌─────────────────────────────────────────────────────────────┐
│                    Interaction Flow                         │
└─────────────────────────────────────────────────────────────┘

1. Monitoring Layer (Phase 4)
   │
   ├─> Detects metric anomaly
   │   └─> Cloud Adapter: FetchMetrics()
   │
   └─> Detects pod failure
       └─> Cloud Adapter: GetPodStatus()

2. AI Analysis Layer (Phase 5)
   │
   ├─> Self-Healing Agent analyzes failure
   │   ├─> Uses ML model to classify failure type
   │   ├─> Uses RL model to select healing strategy
   │   └─> Generates explanation using LLM
   │
   └─> Scaling Agent analyzes metrics
       ├─> Uses time series model to predict load
       ├─> Uses optimization model to determine scaling
       └─> Generates explanation using LLM

3. Action Execution Layer (Phase 4)
   │
   ├─> Self-Healing Agent executes healing
   │   └─> Cloud Adapter: RestartPod() or RollbackDeployment()
   │
   └─> Scaling Agent executes scaling
       └─> Cloud Adapter: SetReplicas()

4. Verification Layer (Phase 4)
   │
   └─> Cloud Adapter: VerifyRecovery()
       └─> Reports back to AI Agent
```

### Example: Failure Detection and Healing

```go
// Phase 4: Cloud Adapter detects failure
func (ca *CloudAdapter) MonitorPods() {
    pods, _ := ca.k8sClient.CoreV1().Pods(namespace).List(...)
    for _, pod := range pods.Items {
        if pod.Status.Phase == "Failed" {
            // Phase 5: AI Agent analyzes failure
            agent := selfhealing.NewSelfHealingAgent()
            request := &HealingRequest{
                ServiceID: pod.Name,
                FailureType: agent.ClassifyFailure(pod), // ML model
            }
            
            // Phase 5: AI Agent decides action
            strategy := agent.SelectHealingStrategy(request) // RL model
            
            // Phase 4: Cloud Adapter executes action
            switch strategy {
            case "restart":
                ca.RestartPod(pod.Name)
            case "rollback":
                ca.RollbackDeployment(pod.Labels["app"])
            }
            
            // Phase 5: AI Agent explains action
            explanation := agent.HealExplanation() // LLM
        }
    }
}
```

## Running LocalStack and Minikube Together

### Prerequisites

- Docker and Docker Compose installed
- Minikube installed
- kubectl configured
- AWS CLI (optional, for testing)

### Step-by-Step Setup

#### 1. Start LocalStack

```bash
# Navigate to LocalStack directory
cd cloud-simulation/localstack

# Start LocalStack
docker-compose up -d

# Wait for LocalStack to be ready
curl http://localhost:4566/_localstack/health

# Bootstrap AWS resources
./bootstrap.sh
```

#### 2. Start Minikube

```bash
# Navigate to Minikube directory
cd ../../kubernetes/minikube

# Start Minikube cluster
./start_minikube.sh

# Verify cluster is running
kubectl get nodes

# Create namespace
kubectl apply -f namespace.yaml
```

#### 3. Deploy Mock Services

```bash
# Deploy all mock microservices
kubectl apply -f deployments/compute-service/
kubectl apply -f deployments/storage-service/
kubectl apply -f deployments/logging-service/

# Verify deployments
kubectl get deployments -n self-healing-cloud
kubectl get pods -n self-healing-cloud
```

#### 4. Configure Environment Variables

```bash
# For agents running locally
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export KUBECONFIG=~/.kube/config
export KUBERNETES_NAMESPACE=self-healing-cloud
export PROMETHEUS_URL=http://localhost:9090
```

#### 5. Start Simulation Services (Optional)

```bash
# Start Prometheus, MinIO, etc.
cd ../../docker
docker-compose -f docker-compose.simulation.yml up -d
```

### Using the Run Script

For convenience, use the provided script:

```bash
# Run entire simulation environment
./scripts/run_simulation.sh
```

This script:
- Starts LocalStack
- Starts Minikube
- Deploys mock services
- Validates environment
- Prints all endpoints

## How Agents Detect Failures

### Detection Mechanisms

#### 1. Health Check Monitoring

Agents continuously monitor health check endpoints:

```go
// Cloud Adapter monitors health
func (ca *CloudAdapter) MonitorHealth() {
    for {
        pods, _ := ca.k8sClient.CoreV1().Pods(namespace).List(...)
        for _, pod := range pods.Items {
            // Check liveness probe
            if pod.Status.ContainerStatuses[0].Ready == false {
                ca.ReportFailure(pod.Name, "health_check_failed")
            }
        }
        time.Sleep(30 * time.Second)
    }
}
```

#### 2. Metrics-Based Detection

Agents analyze Prometheus metrics for anomalies:

```go
// Performance Monitoring Agent
func (ma *MetricsAnalyzer) DetectAnomalies() {
    metrics, _ := ma.promAdapter.FetchMetrics()
    anomalies, _ := ma.promAdapter.DetectAnomaly(metrics)
    
    for _, anomaly := range anomalies {
        if anomaly.Severity == "high" {
            ma.ReportAnomaly(anomaly)
        }
    }
}
```

#### 3. Event-Based Detection

Agents listen to Kubernetes events:

```go
// Self-Healing Agent watches events
func (a *SelfHealingAgent) WatchEvents() {
    watcher, _ := a.k8sClient.CoreV1().Events(namespace).Watch(...)
    for event := range watcher.ResultChan() {
        if event.Type == "Warning" {
            a.HandleFailure(event.Object)
        }
    }
}
```

#### 4. Log Analysis

Agents analyze logs for error patterns:

```python
# Security Agent analyzes logs
def detect_intrusion(self, logs):
    patterns = [
        "failed_login",
        "unauthorized_access",
        "sql_injection"
    ]
    
    for log in logs:
        for pattern in patterns:
            if pattern in log['message']:
                self.report_threat(log, pattern)
```

### Failure Classification

AI agents classify failures using ML models:

```go
// Self-Healing Agent classifies failure
func (a *SelfHealingAgent) ClassifyFailure(pod *corev1.Pod) string {
    features := []float64{
        float64(pod.Status.ContainerStatuses[0].RestartCount),
        // ... extract features
    }
    
    // Use trained ML model
    failureType := a.mlModel.Predict(features)
    return failureType // "crash", "timeout", "resource_exhaustion", etc.
}
```

### Failure Response Flow

```
1. Detection
   │
   ├─> Health check fails
   ├─> Metrics exceed threshold
   ├─> Event received
   └─> Log pattern detected
   │
   ▼
2. Classification (Phase 5 - AI)
   │
   ├─> ML model classifies failure type
   ├─> RL model selects strategy
   └─> LLM generates explanation
   │
   ▼
3. Action Selection (Phase 5 - AI)
   │
   ├─> Restart pod
   ├─> Rollback deployment
   ├─> Scale resources
   └─> Replace pod
   │
   ▼
4. Execution (Phase 4 - Cloud Adapter)
   │
   ├─> Cloud Adapter executes action
   ├─> Monitors recovery
   └─> Verifies success
   │
   ▼
5. Learning (Phase 5 - AI)
   │
   ├─> Record outcome
   ├─> Update ML models
   └─> Improve future decisions
```

## Testing with Cloud Simulation

### Running Tests

```bash
# Run all cloud simulation tests
cd tests/cloud
go test -v

# Run specific test suite
go test -v -run TestLocalStack
go test -v -run TestKubernetes
go test -v -run TestFailure
```

### Failure Injection

```bash
# Inject failures using provided scripts
cd kubernetes/minikube/failure-injection

# Kill random pod
./kill_random_pod.sh compute-service

# Overload CPU
./overload_cpu.sh compute-service

# Inject network latency
./inject_network_latency.sh

# Delete service
./delete_service.sh compute-service
```

## Troubleshooting

### LocalStack Issues

**Problem**: LocalStack not starting
```bash
# Check Docker is running
docker ps

# Check LocalStack logs
docker-compose -f cloud-simulation/localstack/docker-compose.yml logs

# Verify port 4566 is available
netstat -an | grep 4566
```

**Problem**: Lambda function not found
```bash
# Run bootstrap script
cd cloud-simulation/localstack
./bootstrap.sh

# Verify Lambda exists
aws --endpoint-url=http://localhost:4566 lambda list-functions
```

### Minikube Issues

**Problem**: Minikube not starting
```bash
# Check Minikube status
minikube status

# View Minikube logs
minikube logs

# Restart Minikube
minikube stop
minikube start
```

**Problem**: Pods not creating
```bash
# Check deployment status
kubectl describe deployment -n self-healing-cloud

# Check events
kubectl get events -n self-healing-cloud

# Check resource quotas
kubectl describe quota -n self-healing-cloud
```

### Agent Connection Issues

**Problem**: Agents can't connect to LocalStack
```bash
# Verify environment variables
echo $AWS_ENDPOINT_URL

# Test connection
curl http://localhost:4566/_localstack/health

# Check agent logs
kubectl logs -l app=self-healing-agent -n self-healing-cloud
```

**Problem**: Agents can't connect to Kubernetes
```bash
# Verify kubeconfig
kubectl config view

# Test connection
kubectl get nodes

# Check RBAC permissions
kubectl auth can-i create pods --namespace=self-healing-cloud
```

## Best Practices

1. **Always Clean Up**: Use `reset_simulation.sh` to clean up test resources
2. **Monitor Resources**: Watch CPU/memory usage of simulation services
3. **Use Namespaces**: Isolate test environments using Kubernetes namespaces
4. **Version Control**: Keep simulation configurations in version control
5. **Document Changes**: Update documentation when changing simulation setup
6. **Test Incrementally**: Test one component at a time before integration

## Related Documentation

- [LocalStack Setup](../cloud-simulation/localstack/README.md)
- [Minikube Setup](../kubernetes/minikube/README.md)
- [Agent Integration](../agents/INTEGRATION_README.md)
- [Docker Compose Simulation](../docker/docker-compose.simulation.README.md)
- [Cloud Test Suite](../tests/cloud/README.md)

