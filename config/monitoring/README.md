# Monitoring System with Prometheus & Grafana

This directory contains configuration files for Prometheus metrics collection and Grafana visualization.

## Overview

The monitoring system provides:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization dashboards and alerting

## Prometheus Configuration

### Configuration File (`prometheus.yml`)

Prometheus is configured to scrape metrics from all agents:
- Self-Healing Agent: `localhost:8081/metrics`
- Scaling Agent: `localhost:8082/metrics`
- Task-Solving Agent: `localhost:8083/metrics`
- Security Agent: `localhost:8084/metrics`
- Performance Monitoring Agent: `localhost:8085/metrics`
- Coding Agent: `localhost:8086/metrics`
- Optimization Agent: `localhost:8087/metrics`

### Alerting Rules (`alerts.yml`)

Pre-configured alerting rules:
- Agent Down
- High Error Rate
- Self-Healing High Failure Rate
- Scaling Agent Excessive Scaling
- Security Intrusion Detected
- High CPU/Memory Usage
- High Anomaly Detection Rate

## Agent Metrics

### Self-Healing Agent

- `heal_success_rate`: Success rate of healing actions (0.0 to 1.0)
- `heal_failures_total`: Total number of failed healing actions
- `heal_actions_total`: Total number of healing actions performed
- `heal_duration_seconds`: Duration of healing actions

### Scaling Agent

- `scaling_actions_total`: Total number of scaling actions (labeled by direction and service)
- `current_replicas`: Current number of replicas (labeled by service)
- `scaling_duration_seconds`: Duration of scaling actions

### Task-Solving Agent

- `tasks_completed_total`: Total number of completed tasks
- `task_failures_total`: Total number of failed tasks
- `tasks_in_progress`: Number of tasks currently in progress
- `task_duration_seconds`: Duration of task processing

### Security Agent

- `intrusion_alerts_total`: Total number of intrusion alerts (labeled by severity and type)
- `blocked_attacks_total`: Total number of blocked attacks
- `security_scans_total`: Total number of security scans performed

### Performance Monitoring Agent

- `anomalies_detected_total`: Total number of anomalies detected
- `cpu_usage_percent`: CPU usage percentage (labeled by service and node)
- `memory_usage_percent`: Memory usage percentage (labeled by service and node)
- `network_latency_seconds`: Network latency

### Coding Agent

- `code_fixes_total`: Total number of code fixes performed
- `code_generations_total`: Total number of code generations performed
- `code_fix_duration_seconds`: Duration of code fixes

### Optimization Agent

- `optimization_runs_total`: Total number of optimization runs
- `cost_savings_total`: Total cost savings in dollars
- `resource_optimizations_total`: Total number of resource optimizations

### Common Metrics (All Agents)

- `agent_requests_total`: Total requests (labeled by agent and status)
- `agent_errors_total`: Total errors (labeled by agent and error_type)
- `agent_latency_seconds`: Request latency (labeled by agent)
- `agent_uptime_seconds`: Agent uptime (labeled by agent)
- `agent_active_tasks`: Active tasks (labeled by agent)

## Setup

### Start Prometheus

```bash
# Using Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/config/monitoring/alerts.yml:/etc/prometheus/alerts.yml \
  prom/prometheus
```

### Start Grafana

```bash
# Using Docker
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/monitoring/grafana/dashboards:/var/lib/grafana/dashboards \
  -v $(pwd)/monitoring/grafana/provisioning:/etc/grafana/provisioning \
  grafana/grafana
```

### Access Points

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Grafana Dashboards

### Pre-configured Dashboards

1. **System Health Dashboard** (`system-health-dashboard.json`)
   - System CPU/Memory usage
   - Agent status
   - Error rate
   - Request rate

2. **Agent Performance Dashboard** (`agent-performance-dashboard.json`)
   - Agent request rate
   - Agent latency (P95, P99)
   - Agent uptime
   - Active tasks
   - Self-Healing success rate
   - Scaling actions
   - Tasks completed

3. **Resource Usage Dashboard** (`resource-usage-dashboard.json`)
   - CPU usage by service
   - Memory usage by service
   - Current replicas
   - Network latency
   - Cost savings

4. **Event Flows Dashboard** (`event-flows-dashboard.json`)
   - Healing actions
   - Scaling actions
   - Intrusion alerts
   - Anomalies detected
   - Code fixes
   - Optimization runs

5. **Error Rates Dashboard** (`error-rates-dashboard.json`)
   - Error rate by agent
   - Healing failures
   - Task failures
   - Error rate trend
   - Success vs failure rate

## Agent Integration

### Go Agents

Agents use the `MetricsRegistry` from `config/monitoring/prometheus_metrics.go`:

```go
import "github.com/ai-driven-self-healing-cloud/config/monitoring"

metrics := monitoring.GetMetricsRegistry()

// Record metrics
metrics.HealActionsTotal.Inc()
metrics.HealSuccessRate.Set(0.95)
metrics.RecordAgentRequest("self-healing-agent", "success")
```

Start metrics server:
```go
go agents/self-healing/metrics_server.go StartMetricsServer("8081")
```

### Python Agents

Agents use `prometheus_client`:

```python
from prometheus_metrics import (
    record_intrusion_alert,
    record_blocked_attack,
    start_metrics_server
)

# Start metrics server
start_metrics_server(8084)

# Record metrics
record_intrusion_alert("high", "intrusion_attempt")
record_blocked_attack()
```

## Prometheus Queries

### Example Queries

```promql
# Agent request rate
rate(agent_requests_total[5m])

# Agent error rate
rate(agent_errors_total[5m])

# Self-Healing success rate
heal_success_rate

# Scaling actions
rate(scaling_actions_total[5m])

# CPU usage
avg(cpu_usage_percent)

# Memory usage
avg(memory_usage_percent)

# Agent uptime
agent_uptime_seconds

# P95 latency
histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m]))
```

## Alerting

### Alert Rules

Alerts are defined in `alerts.yml`:
- Agent Down: Triggers when agent is down for > 1 minute
- High Error Rate: Triggers when error rate > 0.1 errors/second
- High CPU Usage: Triggers when CPU > 90%
- High Memory Usage: Triggers when memory > 90%
- Security Intrusion: Triggers when intrusion detected

### Grafana Alerts

Configure alerts in Grafana:
1. Go to **Alerting** → **Alert Rules**
2. Create new alert rule
3. Set condition (e.g., `cpu_usage_percent > 90`)
4. Configure notification channels

## Next Steps

1. **Start Prometheus**: Run Prometheus with configuration
2. **Start Grafana**: Run Grafana with dashboards
3. **Start Agents**: Ensure agents expose metrics on `/metrics` endpoint
4. **Import Dashboards**: Dashboards are auto-provisioned
5. **Configure Alerts**: Set up alert notification channels
6. **Monitor**: Use dashboards to monitor system health and performance

