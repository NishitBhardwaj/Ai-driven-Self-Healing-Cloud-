# Kubernetes Load Balancing Configuration

This directory contains Kubernetes load balancing configurations including Ingress, LoadBalancer services, and service mesh configurations.

## Overview

Load balancing distributes incoming traffic across multiple pods to ensure high availability, reliability, and optimal performance.

## Components

### 1. Ingress Controller

**File**: `ingress.yaml`

NGINX Ingress Controller configuration with:
- SSL/TLS termination
- Path-based routing
- Rate limiting
- Session affinity
- Health checks

**Features**:
- Routes `/api/*` to respective agent services
- SSL redirect enabled
- Load balancing: Round robin
- Upstream hash by request URI
- Proxy timeouts: 60s

**Prerequisites**:
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Apply**:
```bash
kubectl apply -f kubernetes/load-balancing/ingress.yaml
```

### 2. LoadBalancer Services

**File**: `service-load-balancer.yaml`

Cloud provider LoadBalancer services for direct external access.

**Features**:
- AWS Network Load Balancer (NLB)
- Cross-zone load balancing
- Connection idle timeout: 60s
- Session affinity: Client IP (3 hours)

**Apply**:
```bash
kubectl apply -f kubernetes/load-balancing/service-load-balancer.yaml
```

## Load Balancing Strategies

### 1. Round Robin (Default)

Distributes requests evenly across all pods.

**Configuration**:
```yaml
nginx.ingress.kubernetes.io/load-balance: "round_robin"
```

### 2. Least Connections

Routes to the pod with the fewest active connections.

**Configuration**:
```yaml
nginx.ingress.kubernetes.io/load-balance: "least_conn"
```

### 3. IP Hash

Routes based on client IP address (session affinity).

**Configuration**:
```yaml
nginx.ingress.kubernetes.io/upstream-hash-by: "$remote_addr"
```

### 4. Request URI Hash

Routes based on request URI (for caching).

**Configuration**:
```yaml
nginx.ingress.kubernetes.io/upstream-hash-by: "$request_uri"
```

## Service Types

### ClusterIP (Default)

Internal service, accessible only within cluster.

**Use Case**: Inter-service communication

### NodePort

Exposes service on each node's IP at a static port.

**Use Case**: Development, testing

### LoadBalancer

Cloud provider load balancer.

**Use Case**: Production external access

### Ingress

HTTP/HTTPS routing with SSL termination.

**Use Case**: Production web traffic

## Health Checks

### Liveness Probe

Determines if pod is alive and should be restarted.

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Readiness Probe

Determines if pod is ready to receive traffic.

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Session Affinity

### Client IP Affinity

Routes same client to same pod.

```yaml
sessionAffinity: ClientIP
sessionAffinityConfig:
  clientIP:
    timeoutSeconds: 10800  # 3 hours
```

### Cookie-Based Affinity

Uses cookies for session affinity.

```yaml
stickiness:
  enabled: true
  type: lb_cookie
  cookie_duration: 86400
```

## Monitoring

### Check Ingress Status

```bash
kubectl get ingress -n ai-cloud-production
kubectl describe ingress ai-cloud-ingress -n ai-cloud-production
```

### Check LoadBalancer Services

```bash
kubectl get svc -n ai-cloud-production
kubectl describe svc ai-cloud-self-healing-lb -n ai-cloud-production
```

### Check Endpoints

```bash
kubectl get endpoints -n ai-cloud-production
```

## Best Practices

1. **Use Ingress for HTTP/HTTPS**: Better for web traffic
2. **Use LoadBalancer for TCP**: Better for non-HTTP protocols
3. **Enable Health Checks**: Ensure traffic only goes to healthy pods
4. **Configure Timeouts**: Set appropriate timeouts
5. **Monitor Load**: Track load distribution across pods

## Troubleshooting

### Ingress Not Working

1. Check ingress controller: `kubectl get pods -n ingress-nginx`
2. Check ingress status: `kubectl describe ingress`
3. Verify DNS: `nslookup api.ai-cloud.example.com`
4. Check ingress logs: `kubectl logs -n ingress-nginx deployment/ingress-nginx-controller`

### LoadBalancer Not Getting IP

1. Check service: `kubectl describe svc`
2. Verify cloud provider integration
3. Check node status: `kubectl get nodes`
4. Review cloud provider logs

### Uneven Load Distribution

1. Check pod health: `kubectl get pods`
2. Verify readiness probes
3. Check load balancing algorithm
4. Monitor metrics: `kubectl top pods`

## Next Steps

1. **Configure SSL Certificates**: Set up Let's Encrypt or custom certificates
2. **Set Up Monitoring**: Monitor load balancer metrics
3. **Configure Rate Limiting**: Prevent abuse
4. **Enable WAF**: Web Application Firewall
5. **Optimize**: Tune based on traffic patterns

