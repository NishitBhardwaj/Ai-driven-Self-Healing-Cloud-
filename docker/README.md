# Docker Directory

This folder contains Docker-related files for containerizing and running the AI agents and services. Docker enables consistent deployment across different environments and simplifies the development and testing process.

## Overview

Docker is used to:

- **Containerize Agents**: Package each agent with its dependencies
- **Local Development**: Run the entire system locally using Docker Compose
- **Consistent Environments**: Ensure agents run the same way in development, staging, and production
- **Isolation**: Isolate agents and services from each other

## Directory Structure

- **`/docker/agents/`**: Dockerfiles for individual agents
- **`/docker/docker-compose/`**: Docker Compose configuration files for local setup

## Agent Dockerfiles

Each agent has its own Dockerfile located in `/docker/agents/`. These Dockerfiles define:

- Base image (Python, Node.js, etc.)
- Dependencies and packages
- Agent code and configuration
- Entry point and startup commands

### Example Dockerfile Structure

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/self-healing/ ./agents/self-healing/

# Set environment variables
ENV AGENT_NAME=self-healing
ENV AGENT_MODE=auto

# Run agent
CMD ["python", "agents/self-healing/self_healing_agent.py"]
```

## Building Agent Images

### Build Individual Agent

```bash
cd docker/agents
docker build -t self-healing-agent:latest -f self-healing.Dockerfile .
```

### Build All Agents

```bash
cd docker/agents
./build-all.sh
```

## Docker Compose

Docker Compose allows you to run multiple containers together, simulating the entire multi-agent system locally.

### Configuration Files

Configuration files are located in `/docker/docker-compose/`:

- **`docker-compose.yml`**: Main compose file for local development
- **`docker-compose.prod.yml`**: Production configuration
- **`docker-compose.test.yml`**: Testing configuration

### Services Defined

The Docker Compose setup includes:

- **Agents**: All AI agents (self-healing, scaling, task-solving, etc.)
- **Databases**: PostgreSQL, MongoDB, Redis
- **Message Brokers**: RabbitMQ, Kafka
- **Cloud Simulation**: LocalStack, MinIO
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack

### Starting Services

```bash
cd docker/docker-compose

# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres mongodb redis

# View logs
docker-compose logs -f self-healing-agent

# Stop services
docker-compose down
```

### Environment Variables

Create a `.env` file in `/docker/docker-compose/`:

```env
# Agent Configuration
AGENT_MODE=auto
LOG_LEVEL=INFO

# Database Configuration
POSTGRES_PASSWORD=postgres
MONGODB_PASSWORD=admin
REDIS_PASSWORD=

# Cloud Simulation
LOCALSTACK_ENDPOINT=http://localhost:4566
MINIO_ENDPOINT=http://localhost:9000

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

## Development Workflow

### 1. Local Development

```bash
# Start all services
cd docker/docker-compose
docker-compose up -d

# Run agent in development mode
docker-compose up self-healing-agent

# View logs
docker-compose logs -f
```

### 2. Testing

```bash
# Run tests in containers
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Run specific test suite
docker-compose run --rm test-agent pytest tests/unit/
```

### 3. Debugging

```bash
# Access container shell
docker-compose exec self-healing-agent /bin/bash

# View container logs
docker-compose logs self-healing-agent

# Inspect container
docker-compose ps
```

## Multi-Stage Builds

For optimized production images, use multi-stage builds:

```dockerfile
# Build stage
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY agents/self-healing/ ./agents/self-healing/
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "agents/self-healing/self_healing_agent.py"]
```

## Image Optimization

### Best Practices

1. **Use .dockerignore**: Exclude unnecessary files from build context
2. **Layer Caching**: Order Dockerfile commands to maximize cache hits
3. **Multi-Stage Builds**: Reduce final image size
4. **Minimal Base Images**: Use slim or alpine variants
5. **Combine RUN Commands**: Reduce number of layers

### Example .dockerignore

```
.git
.gitignore
*.md
tests/
docs/
.env
*.log
```

## Container Registry

### Push Images to Registry

```bash
# Tag image
docker tag self-healing-agent:latest your-registry.com/self-healing-agent:latest

# Push to registry
docker push your-registry.com/self-healing-agent:latest
```

### Pull Images from Registry

```bash
docker pull your-registry.com/self-healing-agent:latest
```

## Health Checks

Add health checks to Dockerfiles:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

## Resource Limits

Set resource limits in Docker Compose:

```yaml
services:
  self-healing-agent:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## Networking

### Custom Networks

```yaml
networks:
  agent-network:
    driver: bridge
```

### Service Communication

Services can communicate using service names:

```python
# In agent code
postgres_host = "postgres"  # Service name in docker-compose
mongodb_host = "mongodb"
```

## Volumes

### Persistent Data

```yaml
volumes:
  postgres_data:
  mongodb_data:
  redis_data:
```

### Mount Host Directories

```yaml
services:
  agent:
    volumes:
      - ./agents:/app/agents
      - ./config:/app/config
```

## Troubleshooting

### Container Won't Start

- Check logs: `docker-compose logs agent-name`
- Verify environment variables
- Check port conflicts
- Verify dependencies are available

### Build Failures

- Check Dockerfile syntax
- Verify base image exists
- Check network connectivity for package downloads
- Review build context size

### Performance Issues

- Check resource limits
- Monitor container resource usage
- Optimize Dockerfile layers
- Use multi-stage builds

## Related Documentation

- Kubernetes deployment: `/kubernetes/README.md`
- CI/CD pipeline: `/ci-cd/README.md`
- Agent development: `/agents/README.md`

