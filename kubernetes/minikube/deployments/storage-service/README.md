# Storage Service

A mock microservice that simulates storage operations for testing the Self-Healing Agent system.

## Overview

The storage-service is designed to:
- Simulate storage-intensive workloads
- Handle data persistence operations
- Generate storage-related metrics
- Support horizontal pod autoscaling
- Provide endpoints for testing failure scenarios

## Deployment

```bash
# Apply all resources
kubectl apply -f kubernetes/minikube/deployments/storage-service/

# Or apply individually
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml
kubectl apply -f configmap.yaml
```

## Configuration

The service is configured via ConfigMap (`storage-service-config`):

- `log_level`: Logging level (INFO, DEBUG, WARN, ERROR)
- `storage_backend`: Storage backend type (local, s3, nfs)
- `max_storage_size`: Maximum storage size
- `storage_path`: Path for local storage
- `cache_enabled`: Enable caching
- `cache_size_mb`: Cache size in MB
- `replication_factor`: Data replication factor

## Endpoints

- **Health Check**: `http://storage-service/health`
- **Readiness**: `http://storage-service/ready`
- **Metrics**: `http://storage-service:8080/metrics`
- **Storage API**: `http://storage-service/api/v1/storage`

## Autoscaling

The service uses HorizontalPodAutoscaler (HPA) with:
- **Min Replicas**: 2
- **Max Replicas**: 8
- **CPU Target**: 75% utilization
- **Memory Target**: 85% utilization

## Storage

The service uses an `emptyDir` volume for local storage. In production, this would be replaced with:
- PersistentVolumeClaims (PVC)
- StatefulSets for stateful workloads
- External storage backends (S3, NFS, etc.)

## Testing

```bash
# Get service URL
kubectl get svc storage-service -n self-healing-cloud

# Port forward to access service
kubectl port-forward svc/storage-service 8080:80 -n self-healing-cloud

# Check HPA status
kubectl get hpa storage-service-hpa -n self-healing-cloud

# View pod metrics
kubectl top pods -l app=storage-service -n self-healing-cloud

# Check storage usage
kubectl exec -it <pod-name> -n self-healing-cloud -- df -h /data
```

## Failure Scenarios

This service can be used to test:
- Storage failures
- Disk space exhaustion
- I/O errors
- Network latency affecting storage operations
- Pod failures during storage operations

See `../../failure-injection/` for chaos engineering scripts.

