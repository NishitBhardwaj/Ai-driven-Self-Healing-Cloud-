# Kubernetes Ingress Configuration

This directory contains Ingress configurations for exposing agent services to external traffic.

## Overview

Ingress provides:
- **External Access**: Expose services to external traffic
- **SSL/TLS Termination**: Handle HTTPS at the ingress level
- **Path-Based Routing**: Route traffic based on URL paths
- **Load Balancing**: Distribute traffic across service instances
- **Rate Limiting**: Protect services from abuse

## Components

### 1. Public Ingress

**File**: `ingress.yaml`

Exposes agent APIs to external traffic with:
- SSL/TLS termination
- Path-based routing (`/api/self-healing`, `/api/scaling`, etc.)
- Rate limiting (100 req/s)
- CORS support
- Health check endpoint

**Routes**:
- `/api/self-healing` → Self-Healing Agent
- `/api/scaling` → Scaling Agent
- `/api/task-solving` → Task-Solving Agent
- `/api/performance-monitoring` → Performance Monitoring Agent
- `/api/coding` → Coding Agent
- `/api/security` → Security Agent
- `/api/optimization` → Optimization Agent
- `/health` → Health check endpoint
- `/metrics` → Metrics endpoint (internal)

**Apply**:
```bash
kubectl apply -f kubernetes/ingress/ingress.yaml
```

### 2. Internal Ingress

**File**: `ingress-internal.yaml`

Provides internal service-to-service communication:
- No SSL/TLS (internal network)
- Internal hostname
- Service mesh integration

**Apply**:
```bash
kubectl apply -f kubernetes/ingress/ingress-internal.yaml
```

## Prerequisites

### NGINX Ingress Controller

**Install**:
```bash
# Using Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Or using kubectl
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
```

**Verify**:
```bash
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

### cert-manager (for SSL/TLS)

**Install**:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Create ClusterIssuer**:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

## Configuration

### SSL/TLS

Update the ingress to use your domain and certificate:

```yaml
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: ai-cloud-tls
  rules:
  - host: api.yourdomain.com
```

### Rate Limiting

Adjust rate limits in annotations:

```yaml
annotations:
  nginx.ingress.kubernetes.io/limit-rps: "100"  # Requests per second
  nginx.ingress.kubernetes.io/limit-connections: "10"  # Concurrent connections
```

### CORS

Configure CORS for your frontend:

```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-origin: "https://yourdomain.com"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
```

## Usage

### Apply Ingress

```bash
# Apply public ingress
kubectl apply -f kubernetes/ingress/ingress.yaml

# Apply internal ingress
kubectl apply -f kubernetes/ingress/ingress-internal.yaml
```

### Check Ingress Status

```bash
# List ingresses
kubectl get ingress -n ai-cloud-production

# Describe ingress
kubectl describe ingress ai-cloud-ingress -n ai-cloud-production

# Get ingress IP
kubectl get ingress ai-cloud-ingress -n ai-cloud-production \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Test Ingress

```bash
# Test health endpoint
curl https://api.ai-cloud.example.com/health

# Test agent endpoint
curl https://api.ai-cloud.example.com/api/self-healing/health

# Test with authentication
curl -H "Authorization: Bearer $TOKEN" \
  https://api.ai-cloud.example.com/api/self-healing/status
```

## Monitoring

### Check Ingress Logs

```bash
# NGINX Ingress Controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Filter by host
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller | grep api.ai-cloud.example.com
```

### Metrics

NGINX Ingress Controller exposes Prometheus metrics:

```bash
# Port forward to metrics endpoint
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 10254:10254

# Query metrics
curl http://localhost:10254/metrics
```

## Troubleshooting

### Ingress Not Getting IP

1. Check ingress controller:
```bash
kubectl get pods -n ingress-nginx
```

2. Check ingress status:
```bash
kubectl describe ingress ai-cloud-ingress -n ai-cloud-production
```

3. Check load balancer service:
```bash
kubectl get svc -n ingress-nginx
```

### SSL Certificate Not Working

1. Check cert-manager:
```bash
kubectl get certificates -n ai-cloud-production
kubectl describe certificate ai-cloud-tls -n ai-cloud-production
```

2. Check certificate request:
```bash
kubectl get certificaterequests -n ai-cloud-production
```

3. Check ClusterIssuer:
```bash
kubectl get clusterissuer
kubectl describe clusterissuer letsencrypt-prod
```

### 502 Bad Gateway

1. Check backend services:
```bash
kubectl get svc -n ai-cloud-production
kubectl get pods -n ai-cloud-production
```

2. Check service endpoints:
```bash
kubectl get endpoints -n ai-cloud-production
```

3. Test service directly:
```bash
kubectl port-forward svc/ai-cloud-self-healing 8080:8080 -n ai-cloud-production
curl http://localhost:8080/health
```

## Best Practices

1. **Use SSL/TLS**: Always use HTTPS in production
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **CORS**: Configure CORS appropriately
4. **Health Checks**: Include health check endpoints
5. **Monitoring**: Monitor ingress metrics and logs
6. **Security**: Use network policies to restrict access
7. **Annotations**: Use appropriate ingress annotations

## Next Steps

1. **Install Ingress Controller**: Install NGINX Ingress Controller
2. **Install cert-manager**: Set up SSL/TLS certificates
3. **Apply Ingress**: Apply ingress configurations
4. **Configure DNS**: Point your domain to ingress IP
5. **Test**: Test all endpoints
6. **Monitor**: Set up monitoring and alerts

