# Docker Containerization Guide

This directory contains Dockerfiles and build scripts for containerizing all agents in the AI-Driven Self-Healing Cloud system.

## Overview

All agents are containerized using Docker for:
- **Consistency**: Same environment across development, staging, and production
- **Portability**: Run anywhere Docker is supported
- **Isolation**: Each agent runs in its own container
- **Scalability**: Easy to scale horizontally
- **Security**: Isolated from host system

## Directory Structure

```
docker/
├── agents/
│   ├── self-healing/
│   │   └── Dockerfile
│   ├── scaling/
│   │   └── Dockerfile
│   ├── task-solving/
│   │   └── Dockerfile
│   ├── performance-monitoring/
│   │   └── Dockerfile
│   ├── coding/
│   │   └── Dockerfile
│   ├── security/
│   │   └── Dockerfile
│   └── optimization/
│       └── Dockerfile
├── build.sh          # Linux/Mac build script
├── build.ps1         # Windows PowerShell build script
└── README.md         # This file
```

## Dockerfiles

### Go Agents (Self-Healing, Scaling, Task-Solving, Performance-Monitoring)

**Multi-stage build**:
- **Builder stage**: Compiles Go application
- **Runtime stage**: Minimal Alpine Linux image

**Features**:
- Multi-stage builds for smaller images
- Health checks included
- Non-root user (security)
- Minimal dependencies

### Python Agents (Coding, Security, Optimization)

**Single-stage build**:
- Python 3.11 slim base image
- System dependencies installed
- Python packages from requirements.txt

**Features**:
- Optimized layer caching
- Health checks included
- Minimal base image

## Building Images

### Using Build Scripts

**Linux/Mac**:
```bash
# Build all images
./docker/build.sh build

# Push all images
./docker/build.sh push

# Build and push all images
./docker/build.sh all
```

**Windows PowerShell**:
```powershell
# Build all images
.\docker\build.ps1 -Action build

# Push all images
.\docker\build.ps1 -Action push

# Build and push all images
.\docker\build.ps1 -Action all
```

### Manual Build

**Build single agent**:
```bash
docker build -t ai-cloud-self-healing:latest \
  -f docker/agents/self-healing/Dockerfile .
```

**Build all agents**:
```bash
for agent in self-healing scaling task-solving performance-monitoring coding security optimization; do
  docker build -t ai-cloud-${agent}:latest \
    -f docker/agents/${agent}/Dockerfile .
done
```

## Container Registries

### GitHub Container Registry (GHCR)

**Login**:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

**Push**:
```bash
docker tag ai-cloud-self-healing:latest ghcr.io/USERNAME/ai-cloud-self-healing:latest
docker push ghcr.io/USERNAME/ai-cloud-self-healing:latest
```

### Docker Hub

**Login**:
```bash
docker login
```

**Push**:
```bash
docker tag ai-cloud-self-healing:latest USERNAME/ai-cloud-self-healing:latest
docker push USERNAME/ai-cloud-self-healing:latest
```

### AWS ECR

**Login**:
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

**Push**:
```bash
docker tag ai-cloud-self-healing:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-cloud-self-healing:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ai-cloud-self-healing:latest
```

### Google Container Registry (GCR)

**Login**:
```bash
gcloud auth configure-docker
```

**Push**:
```bash
docker tag ai-cloud-self-healing:latest \
  gcr.io/PROJECT_ID/ai-cloud-self-healing:latest
docker push gcr.io/PROJECT_ID/ai-cloud-self-healing:latest
```

### Azure Container Registry (ACR)

**Login**:
```bash
az acr login --name REGISTRY_NAME
```

**Push**:
```bash
docker tag ai-cloud-self-healing:latest \
  REGISTRY_NAME.azurecr.io/ai-cloud-self-healing:latest
docker push REGISTRY_NAME.azurecr.io/ai-cloud-self-healing:latest
```

## Environment Variables

Configure build scripts with environment variables:

```bash
export DOCKER_REGISTRY="ghcr.io"
export IMAGE_PREFIX="ai-cloud"
export IMAGE_TAG="v1.0.0"

./docker/build.sh all
```

## Image Tags

Use semantic versioning for tags:

- `latest`: Latest build (development)
- `v1.0.0`: Specific version (production)
- `v1.0.0-abc1234`: Version with commit hash
- `dev`: Development builds

## Best Practices

1. **Use Multi-Stage Builds**: Reduce image size
2. **Layer Caching**: Order Dockerfile commands for better caching
3. **Security Scanning**: Scan images for vulnerabilities
4. **Tag Appropriately**: Use semantic versioning
5. **Health Checks**: Include health checks in Dockerfiles
6. **Non-Root User**: Run containers as non-root when possible
7. **Minimal Base Images**: Use Alpine or slim variants
8. **.dockerignore**: Exclude unnecessary files

## Security

### Image Scanning

**Trivy**:
```bash
trivy image ai-cloud-self-healing:latest
```

**Docker Scout**:
```bash
docker scout cves ai-cloud-self-healing:latest
```

### Non-Root User

All Dockerfiles should run as non-root:
```dockerfile
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser
USER appuser
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build and push
  run: |
    export DOCKER_REGISTRY=ghcr.io
    export IMAGE_PREFIX=${{ github.repository_owner }}/ai-cloud
    export IMAGE_TAG=${{ github.sha }}
    ./docker/build.sh all
```

### GitLab CI

```yaml
build:
  script:
    - export DOCKER_REGISTRY=$CI_REGISTRY
    - export IMAGE_PREFIX=$CI_REGISTRY_IMAGE
    - export IMAGE_TAG=$CI_COMMIT_SHA
    - ./docker/build.sh all
```

## Troubleshooting

### Build Fails

1. Check Dockerfile syntax
2. Verify dependencies are available
3. Check disk space: `docker system df`
4. Clear build cache: `docker builder prune`

### Push Fails

1. Verify login: `docker login`
2. Check permissions
3. Verify registry URL
4. Check network connectivity

### Image Too Large

1. Use multi-stage builds
2. Remove unnecessary files
3. Use .dockerignore
4. Use minimal base images

## Next Steps

1. **Build Images**: Build all agent images
2. **Push to Registry**: Push to your container registry
3. **Deploy to Kubernetes**: Use Helm charts to deploy
4. **Monitor**: Set up monitoring for containers
