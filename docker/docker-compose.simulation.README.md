# Docker Compose Simulation Environment

This Docker Compose file sets up a complete cloud simulation environment for testing the Self-Healing Cloud system locally.

## Services

### 1. LocalStack
**Ports:** 4566 (Gateway), 4510-4559 (External services)  
**UI:** http://localhost:8080

Simulates AWS services:
- S3, Lambda, CloudWatch, EC2, DynamoDB, SQS, SNS, IAM, CloudWatch Logs

**Environment Variables:**
- `AWS_ENDPOINT_URL=http://localhost:4566`
- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`
- `AWS_DEFAULT_REGION=us-east-1`

### 2. MinIO
**Ports:** 9000 (API), 9001 (Console)  
**Console:** http://localhost:9001  
**Credentials:** minioadmin / minioadmin

S3-compatible object storage for local development.

**Environment Variables:**
- `MINIO_ENDPOINT=http://localhost:9000`
- `MINIO_ACCESS_KEY=minioadmin`
- `MINIO_SECRET_KEY=minioadmin`

### 3. Prometheus
**Port:** 9090  
**UI:** http://localhost:9090

Metrics collection and storage system.

**Environment Variables:**
- `PROMETHEUS_URL=http://localhost:9090`

### 4. Mock Logging Service
**Port:** 8081  
**Endpoints:**
- `GET /health` - Health check
- `GET /logs` - Retrieve logs
- `POST /logs` - Submit logs
- `GET /metrics` - Prometheus metrics

Simple nginx-based mock service for testing logging functionality.

### 5. Fake Identity Provider
**Ports:** 8082 (API), 8083 (Control)  
**API:** http://localhost:8082

Mock OAuth2/OIDC identity provider using MockServer.

**Endpoints:**
- `/.well-known/openid-configuration` - OIDC discovery
- `/authorize` - Authorization endpoint
- `/token` - Token endpoint
- `/userinfo` - User info endpoint

### 6. Node Exporter
**Port:** 9100

Exports system metrics (CPU, memory, disk, network) in Prometheus format.

### 7. cAdvisor
**Port:** 8084  
**UI:** http://localhost:8084

Container metrics exporter for Docker containers.

## Quick Start

### 1. Start All Services

```bash
cd docker
docker-compose -f docker-compose.simulation.yml up -d
```

### 2. Verify Services

```bash
# Check all services are running
docker-compose -f docker-compose.simulation.yml ps

# Check LocalStack health
curl http://localhost:4566/_localstack/health

# Check Prometheus
curl http://localhost:9090/-/healthy

# Check MinIO
curl http://localhost:9000/minio/health/live
```

### 3. Access UIs

- **LocalStack UI:** http://localhost:8080
- **MinIO Console:** http://localhost:9001 (minioadmin/minioadmin)
- **Prometheus:** http://localhost:9090
- **cAdvisor:** http://localhost:8084

## Agent Configuration

### For Agents Running in Docker

Agents should use the following environment variables:

```yaml
environment:
  - AWS_ENDPOINT_URL=http://localstack:4566
  - AWS_ACCESS_KEY_ID=test
  - AWS_SECRET_ACCESS_KEY=test
  - AWS_DEFAULT_REGION=us-east-1
  - MINIO_ENDPOINT=http://minio:9000
  - MINIO_ACCESS_KEY=minioadmin
  - MINIO_SECRET_KEY=minioadmin
  - PROMETHEUS_URL=http://prometheus:9090
  - KUBECONFIG=/kubeconfig/config
```

### For Agents Running Locally (Outside Docker)

```bash
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export MINIO_ENDPOINT=http://localhost:9000
export PROMETHEUS_URL=http://localhost:9090
export KUBECONFIG=~/.kube/config
```

## Kubernetes Integration

### Mounting Kubeconfig

To allow agents to connect to Minikube, mount the kubeconfig file:

```yaml
volumes:
  - ~/.kube/config:/kubeconfig/config:ro
```

Or for Windows:
```yaml
volumes:
  - ${USERPROFILE}/.kube/config:/kubeconfig/config:ro
```

### Using Minikube from Docker

If running agents in Docker and connecting to Minikube on the host:

1. **Get Minikube IP:**
   ```bash
   minikube ip
   ```

2. **Update kubeconfig to use Minikube IP:**
   ```bash
   kubectl config set-cluster minikube --server=https://$(minikube ip):8443
   ```

3. **Mount kubeconfig in docker-compose:**
   ```yaml
   volumes:
     - ~/.kube/config:/kubeconfig/config:ro
   ```

4. **Set environment variable:**
   ```yaml
   environment:
     - KUBECONFIG=/kubeconfig/config
   ```

## Service Discovery

Services can discover each other using Docker service names:

- `localstack` - LocalStack service
- `minio` - MinIO service
- `prometheus` - Prometheus service
- `mock-logging-service` - Mock logging service
- `fake-identity-provider` - Fake identity provider

Example:
```python
import boto3

# Connect to LocalStack from within Docker network
s3_client = boto3.client(
    's3',
    endpoint_url='http://localstack:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)
```

## Data Persistence

All data is persisted in Docker volumes:
- `localstack-data` - LocalStack state
- `minio-data` - MinIO data
- `prometheus-data` - Prometheus metrics

To reset all data:
```bash
docker-compose -f docker-compose.simulation.yml down -v
```

## Monitoring

### Prometheus Targets

Prometheus is configured to scrape:
- Node Exporter (localhost:9100)
- cAdvisor (localhost:8084)
- Mock Logging Service (localhost:8081)

### Example Queries

```promql
# CPU usage
100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# Container CPU
rate(container_cpu_usage_seconds_total[5m])
```

## Logging

View logs for all services:
```bash
docker-compose -f docker-compose.simulation.yml logs -f
```

View logs for specific service:
```bash
docker-compose -f docker-compose.simulation.yml logs -f localstack
docker-compose -f docker-compose.simulation.yml logs -f prometheus
```

## Troubleshooting

### Port Conflicts

If ports are already in use, modify the port mappings in `docker-compose.simulation.yml`:

```yaml
ports:
  - "4567:4566"  # Change host port
```

### LocalStack Not Starting

```bash
# Check logs
docker-compose -f docker-compose.simulation.yml logs localstack

# Verify Docker socket is accessible
ls -la /var/run/docker.sock
```

### MinIO Access Issues

```bash
# Check MinIO logs
docker-compose -f docker-compose.simulation.yml logs minio

# Verify credentials
# Default: minioadmin / minioadmin
```

### Prometheus Not Scraping

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify configuration
docker-compose -f docker-compose.simulation.yml exec prometheus cat /etc/prometheus/prometheus.yml
```

## Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose.simulation.yml stop

# Stop and remove containers
docker-compose -f docker-compose.simulation.yml down

# Stop and remove containers + volumes (deletes all data)
docker-compose -f docker-compose.simulation.yml down -v
```

## Integration with Agents

### Self-Healing Agent

```go
// Set environment variables
os.Setenv("AWS_ENDPOINT_URL", "http://localstack:4566")
os.Setenv("KUBECONFIG", "/kubeconfig/config")

// Use cloud adapter
adapter, _ := NewCloudAdapter()
adapter.RestartPod("pod-name")
```

### Scaling Agent

```go
// Set environment
os.Setenv("KUBECONFIG", "/kubeconfig/config")

// Use k8s scaling
scaling, _ := NewK8sScaling()
scaling.SetReplicas("service-name", 5)
```

### Performance Monitoring Agent

```go
// Set environment
os.Setenv("PROMETHEUS_URL", "http://prometheus:9090")

// Use metrics adapter
adapter, _ := NewPrometheusAdapter()
adapter.ConnectToPrometheus()
metrics, _ := adapter.FetchMetrics()
```

### Security Agent

```python
# Set environment
os.environ["AWS_ENDPOINT_URL"] = "http://localstack:4566"

# Use cloud security adapter
adapter = CloudSecurityAdapter()
misconfigs = adapter.detect_security_misconfig()
```

## Next Steps

1. **Start services:** `docker-compose -f docker-compose.simulation.yml up -d`
2. **Configure agents** with environment variables
3. **Test integrations** using the provided examples
4. **Monitor services** via Prometheus and UIs
5. **Run agent tests** against simulated cloud

