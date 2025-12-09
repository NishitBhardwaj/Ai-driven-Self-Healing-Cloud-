# Kubernetes Auto-Scaling Configuration

This directory contains Kubernetes auto-scaling configurations including Horizontal Pod Autoscaler (HPA), Vertical Pod Autoscaler (VPA), and Cluster Autoscaler.

## Overview

Auto-scaling ensures that your application has the right number of pods and nodes to handle the current load, automatically scaling up during high demand and scaling down during low demand to optimize costs.

## Components

### 1. Horizontal Pod Autoscaler (HPA)

**File**: `hpa-advanced.yaml`

Automatically scales the number of pods based on:
- **CPU utilization**: Scales when CPU > 70-80%
- **Memory utilization**: Scales when memory > 80-85%
- **Custom metrics**: Request rate, queue depth, tasks per second

**Features**:
- Min replicas: 2-3
- Max replicas: 15-25 (depending on agent)
- Scale-up policies: Aggressive (100% or 4 pods per 30s)
- Scale-down policies: Conservative (50% per 60s, 5min stabilization)

**Apply**:
```bash
kubectl apply -f kubernetes/autoscaling/hpa-advanced.yaml
```

### 2. Vertical Pod Autoscaler (VPA)

**File**: `vpa.yaml`

Automatically adjusts CPU and memory requests/limits for pods based on historical usage.

**Features**:
- Update mode: Auto (automatically applies recommendations)
- Min allowed: 50m CPU, 64Mi memory
- Max allowed: 2000m-4000m CPU, 2Gi-4Gi memory

**Prerequisites**:
```bash
# Install VPA
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler/
./hack/vpa-up.sh
```

**Apply**:
```bash
kubectl apply -f kubernetes/autoscaling/vpa.yaml
```

### 3. Cluster Autoscaler

**File**: `cluster-autoscaler.yaml`

Automatically adjusts the size of the Kubernetes cluster by adding or removing nodes.

**Features**:
- Auto-discovery via ASG tags
- Scale-down enabled
- Scale-down delay: 10 minutes after scale-up
- Scale-down unneeded time: 10 minutes
- Utilization threshold: 50%

**Prerequisites**:
- AWS EKS cluster
- IAM permissions for autoscaling

**Apply**:
```bash
kubectl apply -f kubernetes/autoscaling/cluster-autoscaler.yaml
```

## Configuration

### HPA Metrics

**Resource Metrics**:
- CPU utilization
- Memory utilization

**Custom Metrics** (requires metrics server):
- `http_requests_per_second`
- `scaling_requests_per_second`
- `tasks_per_second`
- `task_queue_depth`

### Scaling Behavior

**Scale Up**:
- Stabilization window: 0s (immediate)
- Policies:
  - Percent: 100% increase per 30s
  - Pods: 2-5 pods per 30s
  - Select policy: Max (most aggressive)

**Scale Down**:
- Stabilization window: 300s (5 minutes)
- Policies:
  - Percent: 50% decrease per 60s
  - Pods: 1 pod per 60s
  - Select policy: Min (most conservative)

## Monitoring

### Check HPA Status

```bash
kubectl get hpa -n ai-cloud-production
kubectl describe hpa ai-cloud-self-healing-advanced -n ai-cloud-production
```

### Check VPA Status

```bash
kubectl get vpa -n ai-cloud-production
kubectl describe vpa ai-cloud-self-healing-vpa -n ai-cloud-production
```

### Check Cluster Autoscaler

```bash
kubectl logs -n kube-system deployment/cluster-autoscaler
```

## Best Practices

1. **Start Conservative**: Begin with higher thresholds and adjust
2. **Monitor Metrics**: Watch scaling behavior and adjust policies
3. **Set Appropriate Limits**: Use VPA recommendations as starting point
4. **Test Scaling**: Load test to verify scaling behavior
5. **Cost Optimization**: Use spot instances for non-critical workloads

## Troubleshooting

### HPA Not Scaling

1. Check metrics server: `kubectl top pods`
2. Verify HPA configuration: `kubectl describe hpa`
3. Check pod metrics: `kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods`

### VPA Not Working

1. Verify VPA is installed: `kubectl get deployment vpa-recommender -n kube-system`
2. Check VPA status: `kubectl describe vpa`
3. Review VPA logs: `kubectl logs -n kube-system deployment/vpa-recommender`

### Cluster Autoscaler Not Scaling

1. Check IAM permissions
2. Verify ASG tags are correct
3. Check autoscaler logs: `kubectl logs -n kube-system deployment/cluster-autoscaler`
4. Verify node group configuration

## Next Steps

1. **Install Metrics Server**: Required for HPA resource metrics
2. **Install Prometheus Adapter**: Required for custom metrics
3. **Configure Alerts**: Set up alerts for scaling events
4. **Monitor Costs**: Track costs with scaling enabled
5. **Optimize**: Adjust thresholds based on actual usage

