# Minikube Kubernetes Setup

This directory contains the complete Minikube setup for local Kubernetes cluster testing of the Self-Healing Cloud system.

## Overview

This setup provides:
- **Local Kubernetes Cluster**: Minikube-based cluster with all necessary addons
- **Mock Microservices**: Three test services (compute, storage, logging)
- **Autoscaling**: Horizontal Pod Autoscalers (HPA) for each service
- **Chaos Engineering**: Failure injection scripts for testing self-healing capabilities

## Quick Start

### 1. Start Minikube Cluster

```bash
# Make script executable
chmod +x start_minikube.sh

# Start cluster with all addons
./start_minikube.sh
```

This will:
- Create a Minikube cluster named `self-healing-cloud`
- Enable metrics-server (required for HPA)
- Enable ingress controller
- Enable dashboard
- Configure load balancer emulation

### 2. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 3. Deploy Mock Microservices

```bash
# Deploy all services
kubectl apply -f deployments/compute-service/
kubectl apply -f deployments/storage-service/
kubectl apply -f deployments/logging-service/

# Or deploy all at once
kubectl apply -f deployments/ -R
```

### 4. Verify Deployment

```bash
# Check namespace
kubectl get ns self-healing-cloud

# Check all resources
kubectl get all -n self-healing-cloud

# Check HPA status
kubectl get hpa -n self-healing-cloud

# Check pod metrics
kubectl top pods -n self-healing-cloud
```

## Directory Structure

```
kubernetes/minikube/
├── start_minikube.sh          # Minikube cluster startup script
├── namespace.yaml              # Self-healing-cloud namespace
├── deployments/                # Mock microservices
│   ├── compute-service/
│   │   ├── deployment.yaml     # Deployment manifest
│   │   ├── service.yaml        # Service manifest
│   │   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   │   ├── configmap.yaml      # Configuration
│   │   └── README.md           # Service documentation
│   ├── storage-service/
│   │   └── ... (same structure)
│   └── logging-service/
│       └── ... (same structure)
└── failure-injection/         # Chaos engineering scripts
    ├── kill_random_pod.sh      # Kill random pod
    ├── overload_cpu.sh          # CPU overload
    ├── inject_network_latency.sh # Network latency
    ├── delete_service.sh        # Delete service
    └── README.md                # Failure injection docs
```

## Mock Microservices

### Compute Service

Simulates CPU-intensive workloads.

- **Replicas**: 2-10 (HPA)
- **CPU Target**: 70%
- **Memory Target**: 80%
- **Endpoints**: `/health`, `/ready`, `/metrics`

### Storage Service

Simulates storage operations.

- **Replicas**: 2-8 (HPA)
- **CPU Target**: 75%
- **Memory Target**: 85%
- **Endpoints**: `/health`, `/ready`, `/metrics`, `/api/v1/storage`

### Logging Service

Simulates log aggregation.

- **Replicas**: 2-6 (HPA)
- **CPU Target**: 70%
- **Memory Target**: 80%
- **Endpoints**: `/health`, `/ready`, `/metrics`, `/api/v1/logs`

## Failure Injection

The `failure-injection/` directory contains scripts for chaos engineering:

- **kill_random_pod.sh**: Randomly kills pods to test auto-recovery
- **overload_cpu.sh**: Creates CPU stress to test autoscaling
- **inject_network_latency.sh**: Adds network latency to test resilience
- **delete_service.sh**: Deletes services to test service recovery

See [failure-injection/README.md](failure-injection/README.md) for detailed usage.

## Testing Self-Healing Agent

### Example Test Workflow

```bash
# 1. Start cluster and deploy services
./start_minikube.sh
kubectl apply -f namespace.yaml
kubectl apply -f deployments/ -R

# 2. Verify services are running
kubectl get pods -n self-healing-cloud

# 3. Inject a failure
cd failure-injection
./kill_random_pod.sh compute-service

# 4. Monitor Self-Healing Agent response
kubectl logs -f -l app=self-healing-agent -n self-healing-cloud

# 5. Verify recovery
kubectl get pods -n self-healing-cloud
kubectl get events -n self-healing-cloud --sort-by='.lastTimestamp'
```

### Testing Autoscaling

```bash
# 1. Overload CPU to trigger HPA
cd failure-injection
./overload_cpu.sh compute-service

# 2. Monitor HPA scaling
watch kubectl get hpa -n self-healing-cloud

# 3. Check pod scaling
kubectl get pods -n self-healing-cloud -w

# 4. View resource usage
kubectl top pods -n self-healing-cloud
```

## Configuration

### Minikube Configuration

Edit `start_minikube.sh` to customize:
- Memory allocation
- CPU count
- Disk size
- Kubernetes version

### Service Configuration

Each service has a ConfigMap that can be modified:

```bash
# Edit ConfigMap
kubectl edit configmap compute-service-config -n self-healing-cloud

# Apply changes (pods will restart)
kubectl rollout restart deployment/compute-service -n self-healing-cloud
```

### HPA Configuration

Adjust autoscaling parameters in `hpa.yaml` files:

```yaml
minReplicas: 2
maxReplicas: 10
metrics:
- type: Resource
  resource:
    name: cpu
    target:
      averageUtilization: 70
```

## Monitoring

### Kubernetes Dashboard

```bash
# Open dashboard
minikube dashboard -p self-healing-cloud

# Or get URL
minikube dashboard -p self-healing-cloud --url
```

### Metrics

```bash
# Pod metrics
kubectl top pods -n self-healing-cloud

# Node metrics
kubectl top nodes

# HPA metrics
kubectl get hpa -n self-healing-cloud
kubectl describe hpa <hpa-name> -n self-healing-cloud
```

### Logs

```bash
# Service logs
kubectl logs -l app=compute-service -n self-healing-cloud

# All pods logs
kubectl logs -l app=compute-service -n self-healing-cloud --all-containers=true

# Follow logs
kubectl logs -f -l app=compute-service -n self-healing-cloud
```

### Events

```bash
# Recent events
kubectl get events -n self-healing-cloud --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n self-healing-cloud --watch
```

## Troubleshooting

### Minikube Not Starting

```bash
# Check Docker is running
docker ps

# Check Minikube status
minikube status -p self-healing-cloud

# View Minikube logs
minikube logs -p self-healing-cloud

# Delete and recreate
minikube delete -p self-healing-cloud
./start_minikube.sh
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n self-healing-cloud

# Describe pod
kubectl describe pod <pod-name> -n self-healing-cloud

# Check pod logs
kubectl logs <pod-name> -n self-healing-cloud

# Check events
kubectl get events -n self-healing-cloud
```

### HPA Not Working

```bash
# Check metrics-server
kubectl get pods -n kube-system | grep metrics-server

# Check HPA status
kubectl describe hpa <hpa-name> -n self-healing-cloud

# Test metrics
kubectl top pods -n self-healing-cloud
```

### Services Not Accessible

```bash
# Check service
kubectl get svc -n self-healing-cloud

# Check endpoints
kubectl get endpoints -n self-healing-cloud

# Port forward for testing
kubectl port-forward svc/compute-service 8080:80 -n self-healing-cloud
```

## Cleanup

### Stop Cluster

```bash
minikube stop -p self-healing-cloud
```

### Delete Cluster

```bash
minikube delete -p self-healing-cloud
```

### Delete Resources

```bash
# Delete all resources in namespace
kubectl delete all --all -n self-healing-cloud

# Delete namespace (deletes everything)
kubectl delete namespace self-healing-cloud
```

## Integration with Self-Healing Agent

The Self-Healing Agent should:

1. **Monitor** these services via:
   - Kubernetes API
   - Prometheus metrics
   - Health check endpoints
   - CloudWatch (if using LocalStack)

2. **Detect** failures via:
   - Pod status changes
   - Service unavailability
   - Resource pressure
   - Network issues

3. **Remediate** by:
   - Restarting failed pods
   - Scaling services
   - Recreating deleted services
   - Adjusting resource limits

4. **Verify** recovery via:
   - Health checks
   - Service availability
   - Metrics normalization

## Next Steps

1. **Deploy Self-Healing Agent**: Configure agent to monitor this namespace
2. **Run Chaos Tests**: Use failure injection scripts to test agent
3. **Monitor Results**: Track agent response times and success rates
4. **Iterate**: Adjust agent configuration based on test results

## Related Documentation

- [Kubernetes Main README](../README.md)
- [Self-Healing Agent](../../agents/self-healing/README.md)
- [LocalStack Setup](../../cloud-simulation/localstack/README.md)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)

