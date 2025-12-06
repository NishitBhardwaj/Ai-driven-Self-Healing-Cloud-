# Monitoring Directory

This folder contains configuration files and dashboards for monitoring and logging the multi-agent system. Monitoring ensures system health, performance optimization, and quick issue detection.

## Overview

The monitoring setup includes:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **ELK Stack**: Centralized logging (Elasticsearch, Logstash, Kibana)

## Prometheus

Prometheus is used for collecting and storing metrics from agents and services.

### Configuration

Configuration files are located in `/monitoring/prometheus/`:

- **`prometheus.yml`**: Main Prometheus configuration
- **`alerts.yml`**: Alerting rules
- **`targets/`**: Service discovery targets

### Setup

```bash
# Using Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Access Prometheus

Open http://localhost:9090 in your browser.

### Metrics Endpoints

Agents should expose metrics at `/metrics` endpoint:

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Define metrics
tasks_processed = Counter('tasks_processed_total', 'Total tasks processed')
agent_uptime = Gauge('agent_uptime_seconds', 'Agent uptime in seconds')
task_duration = Histogram('task_duration_seconds', 'Task processing duration')

# Start metrics server
start_http_server(8080)
```

### Alerting Rules

Define alerts in `/monitoring/prometheus/alerts.yml`:

```yaml
groups:
  - name: agent_alerts
    rules:
      - alert: AgentDown
        expr: up{job="self-healing-agent"} == 0
        for: 1m
        annotations:
          summary: "Self-healing agent is down"
```

## Grafana

Grafana provides visualization dashboards for Prometheus metrics.

### Configuration

Configuration files are located in `/monitoring/grafana/`:

- **`dashboards/`**: Dashboard JSON files
- **`provisioning/`**: Data sources and dashboard provisioning

### Setup

```bash
# Using Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/monitoring/grafana/dashboards:/var/lib/grafana/dashboards \
  grafana/grafana
```

### Access Grafana

Open http://localhost:3000 and log in with:
- Username: `admin`
- Password: `admin` (change on first login)

### Dashboards

Pre-configured dashboards are available in `/monitoring/grafana/dashboards/`:

- **Agent Performance**: CPU, memory, request rates
- **System Health**: Overall system status
- **Error Rates**: Error tracking and alerting
- **Resource Usage**: Cloud resource utilization

### Creating Dashboards

1. Go to Grafana UI → Dashboards → New Dashboard
2. Add panels with Prometheus queries
3. Export dashboard JSON to `/monitoring/grafana/dashboards/`

## ELK Stack

ELK Stack provides centralized logging for all agents and services.

### Components

- **Elasticsearch**: Log storage and search
- **Logstash**: Log processing and transformation
- **Kibana**: Log visualization and analysis

### Configuration

Configuration files are located in `/monitoring/elk/`:

- **`elasticsearch/`**: Elasticsearch configuration
- **`logstash/`**: Logstash pipeline configuration
- **`kibana/`**: Kibana configuration

### Setup

```bash
# Using Docker Compose
cd monitoring/elk
docker-compose up -d
```

### Logging from Agents

Agents should send logs to Logstash:

```python
import logging
import logstash

# Configure logging
logger = logging.getLogger('agent')
logger.addHandler(logstash.TCPLogstashHandler('localhost', 5000, version=1))
logger.setLevel(logging.INFO)

# Log events
logger.info('Agent started', extra={'agent_name': 'self-healing'})
```

### Access Kibana

Open http://localhost:5601 in your browser.

## Agent Instrumentation

### Metrics

Expose Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
agent_requests = Counter('agent_requests_total', 'Total requests', ['agent', 'status'])
agent_latency = Histogram('agent_latency_seconds', 'Request latency', ['agent'])
agent_active = Gauge('agent_active_tasks', 'Active tasks', ['agent'])

# Use metrics
agent_requests.labels(agent='self-healing', status='success').inc()
agent_latency.labels(agent='self-healing').observe(0.5)
agent_active.labels(agent='self-healing').set(5)
```

### Logging

Structured logging with context:

```python
import logging
import json

logger = logging.getLogger('agent')

def log_with_context(level, message, **context):
    log_data = {
        'message': message,
        'agent': 'self-healing',
        'timestamp': datetime.utcnow().isoformat(),
        **context
    }
    getattr(logger, level)(json.dumps(log_data))
```

### Tracing

Distributed tracing for request flows:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_task") as span:
    span.set_attribute("task_id", task_id)
    span.set_attribute("agent", "self-healing")
    # Process task
```

## Key Metrics to Monitor

### Agent Metrics

- **Request Rate**: Requests per second
- **Error Rate**: Errors per second
- **Latency**: P50, P95, P99 latencies
- **Active Tasks**: Number of active tasks
- **Queue Depth**: Pending tasks in queue

### System Metrics

- **CPU Usage**: Per agent and overall
- **Memory Usage**: Per agent and overall
- **Network I/O**: Network traffic
- **Disk I/O**: Disk read/write operations

### Business Metrics

- **Tasks Completed**: Total tasks processed
- **Success Rate**: Percentage of successful tasks
- **Recovery Time**: Time to recover from failures
- **Cost**: Cloud resource costs

## Alerting

### Alert Channels

Configure alert channels in Prometheus:

- **Email**: Send alerts via email
- **Slack**: Send alerts to Slack channels
- **PagerDuty**: Integrate with PagerDuty
- **Webhooks**: Custom webhook integrations

### Alert Examples

```yaml
- alert: HighErrorRate
  expr: rate(agent_errors_total[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High error rate detected"

- alert: HighLatency
  expr: histogram_quantile(0.95, agent_latency_seconds) > 1
  for: 5m
  annotations:
    summary: "High latency detected"
```

## Log Analysis

### Common Log Queries

**Find errors in last hour:**
```
level:ERROR AND timestamp:[now-1h TO now]
```

**Find slow requests:**
```
duration:>1s AND agent:self-healing
```

**Find failed tasks:**
```
status:failed AND agent:task-solving
```

## Performance Monitoring

### APM (Application Performance Monitoring)

Monitor application performance:

- **Transaction Tracing**: Track request flows
- **Database Queries**: Monitor query performance
- **External API Calls**: Track external service calls
- **Error Tracking**: Capture and analyze errors

## Cost Monitoring

Monitor cloud resource costs:

- **Resource Usage**: Track resource consumption
- **Cost Allocation**: Allocate costs by agent/service
- **Cost Optimization**: Identify cost-saving opportunities

## Best Practices

1. **Comprehensive Metrics**: Monitor all critical metrics
2. **Alert Fatigue**: Avoid too many alerts; focus on actionable alerts
3. **Dashboard Design**: Create clear, actionable dashboards
4. **Log Retention**: Set appropriate log retention policies
5. **Performance Impact**: Minimize monitoring overhead
6. **Documentation**: Document metrics and alerts

## Troubleshooting

### Prometheus Not Scraping

- Check service discovery configuration
- Verify metrics endpoints are accessible
- Check network connectivity

### Grafana Dashboards Not Loading

- Verify Prometheus data source configuration
- Check dashboard JSON syntax
- Verify time range settings

### ELK Stack Issues

- Check Elasticsearch cluster health
- Verify Logstash pipeline configuration
- Check log ingestion rates

## Related Documentation

- Kubernetes monitoring: `/kubernetes/README.md`
- Agent development: `/agents/README.md`
- CI/CD pipeline: `/ci-cd/README.md`

