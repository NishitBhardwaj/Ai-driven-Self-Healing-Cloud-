# Logging Service

A mock microservice that simulates logging and log aggregation operations for testing the Self-Healing Agent system.

## Overview

The logging-service is designed to:
- Simulate log collection and aggregation
- Handle high-volume log processing
- Generate logging-related metrics
- Support horizontal pod autoscaling
- Provide endpoints for testing failure scenarios

## Deployment

```bash
# Apply all resources
kubectl apply -f kubernetes/minikube/deployments/logging-service/

# Or apply individually
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f configmap.yaml
```

## Configuration

The service is configured via ConfigMap (`logging-service-config`):

- `log_level`: Logging level (INFO, DEBUG, WARN, ERROR)
- `log_retention_days`: Number of days to retain logs
- `max_log_size`: Maximum size per log file
- `log_format`: Log format (json, text, structured)
- `log_rotation`: Log rotation policy (daily, hourly, size-based)
- `aggregation_enabled`: Enable log aggregation

## Endpoints

- **Health Check**: `http://logging-service/health`
- **Readiness**: `http://logging-service/ready`
- **Metrics**: `http://logging-service:8080/metrics`
- **Logs API**: `http://logging-service/api/v1/logs`

## Autoscaling

The service uses HorizontalPodAutoscaler (HPA) with:
- **Min Replicas**: 2
- **Max Replicas**: 6
- **CPU Target**: 70% utilization
- **Memory Target**: 80% utilization

## Log Storage

The service uses an `emptyDir` volume for log storage. In production, this would be replaced with:
- PersistentVolumeClaims (PVC) for log persistence
- External log aggregation systems (ELK, Loki, etc.)
- Cloud storage backends (S3, CloudWatch, etc.)

## Testing

```bash
# Get service URL
kubectl get svc logging-service -n self-healing-cloud

# Port forward to access service
kubectl port-forward svc/logging-service 8080:80 -n self-healing-cloud

# Check HPA status
kubectl get hpa logging-service-hpa -n self-healing-cloud

# View pod metrics
kubectl top pods -l app=logging-service -n self-healing-cloud

# View logs
kubectl logs -l app=logging-service -n self-healing-cloud --tail=100
```

## Failure Scenarios

This service can be used to test:
- Log processing failures
- Disk space exhaustion from logs
- High log volume causing performance issues
- Network latency affecting log aggregation
- Pod failures during log processing

See `../../failure-injection/` for chaos engineering scripts.

