# Kubernetes Directory

This folder contains Kubernetes configuration files for deploying and orchestrating the multi-agent system in a Kubernetes cluster. Kubernetes provides automated deployment, scaling, and management of containerized applications.

## Overview

Kubernetes is used to:

- **Orchestrate Agents**: Deploy and manage multiple agent containers
- **Auto-Scaling**: Automatically scale agents based on demand
- **Service Discovery**: Enable agents to discover and communicate with each other
- **High Availability**: Ensure agents are always available with automatic restarts
- **Resource Management**: Manage CPU and memory resources efficiently

## Directory Structure

- **`/kubernetes/helm/`**: Helm charts for deploying the system
- **`/kubernetes/manifests/`**: Kubernetes YAML manifests for deployment

## Prerequisites

- Kubernetes cluster (local: Minikube, Kind, or cloud: EKS, GKE, AKS)
- kubectl configured to access your cluster
- Docker images pushed to a container registry

## Quick Start

### Using Minikube (Local)

```bash
# Start Minikube
minikube start

# Verify cluster
kubectl get nodes

# Deploy agents
kubectl apply -f kubernetes/manifests/
```

### Using Helm

```bash
# Install Helm chart
helm install multi-agent-system ./kubernetes/helm/multi-agent-system/

# Upgrade deployment
helm upgrade multi-agent-system ./kubernetes/helm/multi-agent-system/

# Uninstall
helm uninstall multi-agent-system
```

## Kubernetes Manifests

Manifests are located in `/kubernetes/manifests/` and include:

### Deployments

Deployments manage agent pods and ensure desired replica counts:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: self-healing-agent
spec:
  replicas: 2
  selector:
    matchLabels:
      app: self-healing-agent
  template:
    metadata:
      labels:
        app: self-healing-agent
    spec:
      containers:
      - name: self-healing-agent
        image: your-registry.com/self-healing-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: AGENT_MODE
          value: "auto"
```

### Services

Services provide stable network endpoints for agents:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: self-healing-agent
spec:
  selector:
    app: self-healing-agent
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### ConfigMaps

ConfigMaps store configuration data:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  agent-mode: "auto"
  log-level: "INFO"
  monitoring-interval: "30s"
```

### Secrets

Secrets store sensitive data:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
type: Opaque
data:
  database-password: <base64-encoded>
  api-key: <base64-encoded>
```

## Helm Charts

Helm charts are located in `/kubernetes/helm/` and provide:

- **Templated Manifests**: Parameterized Kubernetes resources
- **Dependency Management**: Manage chart dependencies
- **Versioning**: Version and release management
- **Values Files**: Environment-specific configurations

### Chart Structure

```
helm/multi-agent-system/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    └── ingress.yaml
```

### Installing with Helm

```bash
# Development
helm install multi-agent-system ./kubernetes/helm/multi-agent-system/ \
  -f ./kubernetes/helm/multi-agent-system/values-dev.yaml

# Production
helm install multi-agent-system ./kubernetes/helm/multi-agent-system/ \
  -f ./kubernetes/helm/multi-agent-system/values-prod.yaml
```

## Deployment Strategies

### Rolling Update

Default Kubernetes deployment strategy:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### Blue-Green Deployment

Deploy new version alongside old version:

```bash
# Deploy new version
kubectl apply -f deployment-v2.yaml

# Switch traffic
kubectl patch service agent-service -p '{"spec":{"selector":{"version":"v2"}}}'
```

### Canary Deployment

Gradually roll out new version:

```yaml
# Deploy canary (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-canary
spec:
  replicas: 1  # 10% of total
```

## Auto-Scaling

### Horizontal Pod Autoscaler (HPA)

Automatically scale pods based on CPU/memory:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: self-healing-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: self-healing-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Pod Autoscaler (VPA)

Automatically adjust pod resource requests:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: self-healing-agent-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: self-healing-agent
  updatePolicy:
    updateMode: "Auto"
```

## Service Discovery

Agents can discover each other using Kubernetes DNS:

```python
# In agent code
scaling_agent_host = "scaling-agent-service.default.svc.cluster.local"
self_healing_agent_host = "self-healing-agent-service.default.svc.cluster.local"
```

## Resource Management

### Resource Requests and Limits

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Namespace Isolation

```bash
# Create namespace
kubectl create namespace agents

# Deploy to namespace
kubectl apply -f manifests/ -n agents
```

## Monitoring and Logging

### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Prometheus Integration

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```

## Ingress

Expose agents to external traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent-ingress
spec:
  rules:
  - host: agents.example.com
    http:
      paths:
      - path: /self-healing
        pathType: Prefix
        backend:
          service:
            name: self-healing-agent
            port:
              number: 80
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>
```

### Service Not Accessible

```bash
# Check service
kubectl get svc

# Test service
kubectl port-forward svc/self-healing-agent 8080:80
```

### Resource Issues

```bash
# Check resource usage
kubectl top pods

# Check node resources
kubectl top nodes
```

## Best Practices

1. **Use Deployments**: Always use Deployments, not Pods directly
2. **Resource Limits**: Set appropriate resource requests and limits
3. **Health Checks**: Implement liveness and readiness probes
4. **Secrets Management**: Use Kubernetes Secrets or external secret managers
5. **Namespace Isolation**: Use namespaces to separate environments
6. **Labels and Selectors**: Use consistent labeling strategy
7. **ConfigMaps**: Store non-sensitive configuration in ConfigMaps

## Related Documentation

- Docker setup: `/docker/README.md`
- CI/CD pipeline: `/ci-cd/README.md`
- Monitoring: `/monitoring/README.md`

