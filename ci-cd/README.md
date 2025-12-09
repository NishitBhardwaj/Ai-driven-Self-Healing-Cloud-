# CI/CD Pipeline Documentation

This directory contains CI/CD pipeline configurations for automated building, testing, and deployment of the AI-Driven Self-Healing Cloud system.

## Overview

The CI/CD pipeline automates:
- **Continuous Integration (CI)**: Automated builds and tests on code push
- **Continuous Deployment (CD)**: Automated deployment to Kubernetes clusters
- **Docker Image Building**: Container images for all agents
- **Security Scanning**: Vulnerability scanning with Trivy
- **Rolling Updates**: Zero-downtime deployments

## Pipeline Flow

```
Code Push
    ↓
Unit Tests (Go + Python)
    ↓
Linting (Go + Python)
    ↓
Build Docker Images
    ↓
Security Scan
    ↓
Deploy to Kubernetes
    ↓
Smoke Tests
    ↓
Rollback on Failure
```

## CI/CD Platforms

### 1. GitHub Actions

**Location**: `.github/workflows/`

**Workflows**:
- `ci.yml`: Continuous Integration pipeline
- `cd.yml`: Continuous Deployment pipeline

**Features**:
- ✅ Automated on push/PR
- ✅ Parallel test execution
- ✅ Docker image building
- ✅ Kubernetes deployment
- ✅ Automatic rollback

**Setup**:
1. Push code to GitHub repository
2. Configure secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`
   - `EKS_CLUSTER_NAME`
3. Workflows run automatically

### 2. GitLab CI

**Location**: `.gitlab-ci.yml`

**Features**:
- ✅ Multi-stage pipeline
- ✅ Parallel builds
- ✅ Manual deployment gates
- ✅ Coverage reports
- ✅ Security scanning

**Setup**:
1. Push code to GitLab repository
2. Configure CI/CD variables:
   - `KUBE_CONTEXT_STAGING`
   - `KUBE_CONTEXT_PRODUCTION`
3. Pipeline runs automatically

### 3. Jenkins

**Location**: `Jenkinsfile`

**Features**:
- ✅ Declarative pipeline
- ✅ Parallel builds
- ✅ Email notifications
- ✅ Coverage reports
- ✅ Automatic rollback

**Setup**:
1. Install Jenkins plugins:
   - Docker Pipeline
   - Kubernetes CLI
   - Helm
   - Coverage
2. Configure credentials:
   - Docker registry credentials
   - Kubernetes config
3. Create pipeline job from Jenkinsfile

## Docker Images

### Go Agents

All Go agents use multi-stage builds:
- **Builder stage**: Compiles Go application
- **Runtime stage**: Minimal Alpine image

**Agents**:
- `self-healing`
- `scaling`
- `task-solving`
- `performance-monitoring`

### Python Agents

Python agents use slim Python images:
- **Base**: `python:3.11-slim`
- **Dependencies**: Installed from requirements.txt

**Agents**:
- `coding`
- `security`
- `optimization`

## Kubernetes Deployment

### Helm Charts

**Location**: `kubernetes/helm/ai-cloud/`

**Features**:
- ✅ All agents configurable
- ✅ Auto-scaling (HPA)
- ✅ Resource limits
- ✅ Health checks
- ✅ Service monitors for Prometheus

**Deploy**:
```bash
helm upgrade --install ai-cloud \
  kubernetes/helm/ai-cloud \
  --namespace ai-cloud-production \
  --set image.tag=v1.0.0 \
  --set environment=production
```

### Deployment Strategy

- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Liveness and readiness probes
- **Auto-Scaling**: Horizontal Pod Autoscaler (HPA)
- **Resource Management**: CPU and memory limits

## Testing

### Unit Tests

- **Go**: `go test ./tests/agents/...`
- **Python**: `pytest tests/agents/*_test.py`

### Integration Tests

- **Go**: `go test ./tests/integration/...`

### Smoke Tests

After deployment:
```bash
kubectl run test-client --image=curlimages/curl --rm -it -- \
  curl -f http://ai-cloud-self-healing:8080/health
```

## Security

### Scanning

- **Trivy**: Vulnerability scanning
- **CodeQL**: Code analysis (GitHub)
- **SAST**: Static analysis (GitLab)

### Best Practices

- ✅ Scan images before deployment
- ✅ Use minimal base images
- ✅ Regular dependency updates
- ✅ Secrets management
- ✅ Non-root containers

## Monitoring

### Metrics

- Prometheus ServiceMonitors configured
- Metrics exposed on `/metrics` endpoints
- Auto-discovered by Prometheus

### Logs

- Centralized logging to ELK Stack
- Structured JSON logs
- Log aggregation

## Rollback

### Automatic Rollback

On deployment failure:
- Helm automatically rolls back
- Previous version restored
- Team notified

### Manual Rollback

```bash
helm rollback ai-cloud <revision-number> -n <namespace>
```

## Environment Promotion

### Staging

- Auto-deploy from `develop` branch
- Manual approval required
- Smoke tests run

### Production

- Auto-deploy from `main` branch
- Manual approval required
- Full test suite
- Canary deployment (optional)

## Troubleshooting

### Build Failures

1. Check test output
2. Verify dependencies
3. Check Docker build logs
4. Review linting errors

### Deployment Failures

1. Check Kubernetes events: `kubectl get events`
2. Check pod logs: `kubectl logs <pod-name>`
3. Verify image pull: `kubectl describe pod <pod-name>`
4. Check resource limits

### Image Pull Errors

1. Verify registry credentials
2. Check image exists: `docker pull <image>`
3. Verify permissions
4. Check network connectivity

## Best Practices

1. **Small Commits**: Frequent, small commits
2. **Test Coverage**: Maintain >80% coverage
3. **Security**: Regular vulnerability scans
4. **Documentation**: Keep README updated
5. **Monitoring**: Monitor deployment metrics
6. **Rollback Plan**: Always have rollback strategy

## Next Steps

1. **Configure Secrets**: Set up secret management
2. **Enable Monitoring**: Configure Prometheus
3. **Set Up Alerts**: Configure alerting rules
4. **Optimize Builds**: Cache dependencies
5. **Multi-Environment**: Set up dev/staging/prod

## Support

For issues:
- Check pipeline logs
- Review deployment events
- Consult troubleshooting guide
- Contact DevOps team
