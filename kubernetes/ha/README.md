# Kubernetes High Availability Configuration

This directory contains Kubernetes configurations for high availability, failover, and disaster recovery.

## Overview

High availability ensures that your application remains accessible even when individual components fail. This is achieved through:

- **Multi-Zone Deployment**: Pods distributed across multiple availability zones
- **Pod Disruption Budgets**: Ensures minimum number of pods remain available
- **Anti-Affinity Rules**: Prevents pods from being scheduled on the same node/zone
- **Health Checks**: Liveness and readiness probes
- **Automatic Failover**: Kubernetes automatically reschedules failed pods

## Components

### 1. Pod Disruption Budgets (PDB)

**File**: `pod-disruption-budget.yaml`

Ensures a minimum number of pods remain available during voluntary disruptions (updates, node maintenance).

**Features**:
- **Self-Healing Agent**: Min 2 pods available
- **Scaling Agent**: Min 2 pods available
- **Task-Solving Agent**: Min 3 pods available (critical service)
- **Performance Monitoring**: Min 2 pods available
- **Security Agent**: Min 2 pods available
- **Coding Agent**: Min 1 pod available
- **Optimization Agent**: Min 1 pod available

**Apply**:
```bash
kubectl apply -f kubernetes/ha/pod-disruption-budget.yaml
```

**Check Status**:
```bash
kubectl get pdb -n ai-cloud-production
kubectl describe pdb ai-cloud-self-healing-pdb -n ai-cloud-production
```

### 2. Pod Anti-Affinity

**File**: `anti-affinity.yaml`

Ensures pods are distributed across different nodes and zones.

**Types**:
- **Node Anti-Affinity**: Pods on different nodes (preferred)
- **Zone Anti-Affinity**: Pods in different zones (preferred)
- **Required Anti-Affinity**: Hard requirement (for critical services)

**Features**:
- Self-Healing: 3 replicas across nodes/zones
- Scaling: 3 replicas across nodes/zones
- Task-Solving: 5 replicas, required node anti-affinity

**Apply**:
```bash
kubectl apply -f kubernetes/ha/anti-affinity.yaml
```

**Verify Distribution**:
```bash
kubectl get pods -n ai-cloud-production -o wide
kubectl get nodes -o wide
```

## High Availability Best Practices

### 1. Multi-Zone Deployment

Ensure your cluster spans multiple availability zones:

**AWS EKS**:
```bash
eksctl create cluster \
  --name ai-cloud-cluster \
  --region us-east-1 \
  --zones us-east-1a,us-east-1b,us-east-1c
```

**GCP GKE**:
```bash
gcloud container clusters create ai-cloud-cluster \
  --region us-central1 \
  --node-locations us-central1-a,us-central1-b,us-central1-c
```

**Azure AKS**:
```bash
az aks create \
  --resource-group ai-cloud-rg \
  --name ai-cloud-cluster \
  --node-count 3 \
  --zones 1 2 3
```

### 2. Resource Requests and Limits

Set appropriate resource requests and limits:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 3. Health Checks

Configure liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

### 4. Replica Counts

Set appropriate replica counts based on criticality:

- **Critical Services**: 5+ replicas
- **Important Services**: 3 replicas
- **Standard Services**: 2 replicas
- **Optional Services**: 1 replica

### 5. Rolling Updates

Use rolling updates for zero-downtime deployments:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0  # Ensure availability during updates
```

## Monitoring High Availability

### Check Pod Distribution

```bash
# Check pod distribution across nodes
kubectl get pods -n ai-cloud-production -o wide

# Check pod distribution across zones
kubectl get pods -n ai-cloud-production -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\t"}{.metadata.labels.topology\.kubernetes\.io/zone}{"\n"}{end}'
```

### Check Pod Disruption Budgets

```bash
# List all PDBs
kubectl get pdb -n ai-cloud-production

# Describe a specific PDB
kubectl describe pdb ai-cloud-self-healing-pdb -n ai-cloud-production
```

### Check Node Health

```bash
# List nodes
kubectl get nodes

# Describe node
kubectl describe node <node-name>

# Check node conditions
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

## Failover Testing

### Simulate Node Failure

```bash
# Drain a node (safely evicts pods)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Verify pods are rescheduled
kubectl get pods -n ai-cloud-production -o wide

# Uncordon the node
kubectl uncordon <node-name>
```

### Simulate Pod Failure

```bash
# Delete a pod
kubectl delete pod <pod-name> -n ai-cloud-production

# Verify pod is recreated
kubectl get pods -n ai-cloud-production
```

### Test Pod Disruption Budget

```bash
# Try to delete multiple pods
kubectl delete pod -l component=self-healing -n ai-cloud-production

# Verify PDB prevents deletion below minimum
kubectl get pdb ai-cloud-self-healing-pdb -n ai-cloud-production
```

## Troubleshooting

### Pods Not Distributing Across Zones

1. Check node zones:
```bash
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.labels.topology\.kubernetes\.io/zone}{"\n"}{end}'
```

2. Verify anti-affinity rules:
```bash
kubectl describe pod <pod-name> -n ai-cloud-production
```

3. Check node capacity:
```bash
kubectl describe node <node-name>
```

### PDB Not Working

1. Check PDB status:
```bash
kubectl describe pdb <pdb-name> -n ai-cloud-production
```

2. Verify selector matches pods:
```bash
kubectl get pods -l component=self-healing -n ai-cloud-production
```

3. Check PDB configuration:
```bash
kubectl get pdb <pdb-name> -n ai-cloud-production -o yaml
```

## Next Steps

1. **Configure Health Checks**: Add liveness and readiness probes
2. **Set Resource Limits**: Configure requests and limits
3. **Enable Monitoring**: Set up alerts for pod failures
4. **Test Failover**: Regularly test node and pod failures
5. **Document Runbooks**: Create runbooks for common failure scenarios

