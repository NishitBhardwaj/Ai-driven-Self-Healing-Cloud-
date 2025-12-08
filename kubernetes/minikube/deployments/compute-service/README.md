# Compute Service

A mock microservice that simulates compute-intensive workloads for testing the Self-Healing Agent system.

## Overview

The compute-service is designed to:
- Simulate CPU-intensive workloads
- Generate metrics for monitoring
- Respond to health checks
- Support horizontal pod autoscaling
- Provide endpoints for testing failure scenarios

## Deployment

```bash
# Apply all resources
kubectl apply -f kubernetes/minikube/deployments/compute-service/

# Or apply individually
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f configmap.yaml
```

## Configuration

The service is configured via ConfigMap (`compute-service-config`):

- `log_level`: Logging level (INFO, DEBUG, WARN, ERROR)
- `workload_intensity`: Workload intensity (low, medium, high)
- `max_concurrent_requests`: Maximum concurrent requests
- `timeout_seconds`: Request timeout
- `retry_attempts`: Number of retry attempts

## Endpoints

- **Health Check**: `http://compute-service/health`
- **Readiness**: `http://compute-service/ready`
- **Metrics**: `http://compute-service:8080/metrics`

## Autoscaling

The service uses HorizontalPodAutoscaler (HPA) with:
- **Min Replicas**: 2
- **Max Replicas**: 10
- **CPU Target**: 70% utilization
- **Memory Target**: 80% utilization

## Testing

```bash
# Get service URL
kubectl get svc compute-service -n self-healing-cloud

# Port forward to access service
kubectl port-forward svc/compute-service 8080:80 -n self-healing-cloud

# Check HPA status
kubectl get hpa compute-service-hpa -n self-healing-cloud

# View pod metrics
kubectl top pods -l app=compute-service -n self-healing-cloud
```

## Failure Scenarios

This service can be used to test:
- Pod failures (killed pods)
- CPU overload
- Memory pressure
- Network latency
- Service unavailability

See `../../failure-injection/` for chaos engineering scripts.

