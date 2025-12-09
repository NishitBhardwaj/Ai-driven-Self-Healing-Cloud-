# Monitoring, Logging & Security - Complete Guide

This directory contains comprehensive monitoring, logging, and security configurations for the AI-Driven Self-Healing Cloud system.

## Overview

The monitoring and logging system provides:
- **Centralized Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics Collection**: Prometheus for time-series metrics
- **Visualization**: Grafana dashboards for real-time monitoring
- **Alerting**: Alertmanager for proactive notifications
- **Security Monitoring**: Security-specific dashboards and alerts

## Directory Structure

```
monitoring/
├── prometheus/
│   └── k8s-prometheus.yml          # Kubernetes Prometheus config
├── grafana/
│   └── dashboards/
│       ├── system-health-dashboard.json
│       ├── agent-performance-dashboard.json
│       ├── resource-usage-dashboard.json
│       ├── error-rates-dashboard.json
│       ├── event-flows-dashboard.json
│       ├── security-monitoring-dashboard.json  # NEW
│       └── agent-actions-dashboard.json        # NEW
├── alertmanager/
│   └── alertmanager.yml            # Alert routing configuration
└── README.md                       # This file

config/
├── monitoring/
│   ├── prometheus.yml              # Prometheus configuration
│   ├── alerts.yml                  # Alerting rules
│   └── prometheus_metrics.go       # Go metrics library
└── logging/
    ├── elk-docker-compose.yml      # ELK Stack setup
    ├── logstash.conf               # Logstash pipeline
    ├── elasticsearch.yml           # Elasticsearch config
    ├── kibana.yml                  # Kibana config
    └── agent_logger.go             # Go logging library

kubernetes/
└── monitoring/
    └── servicemonitor.yaml         # ServiceMonitor for Prometheus
```

## Components

### 1. ELK Stack (Elasticsearch, Logstash, Kibana)

**Purpose**: Centralized logging and log analysis

**Setup**:
```bash
cd config/logging
docker-compose -f elk-docker-compose.yml up -d
```

**Access**:
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Logstash: http://localhost:5000

**Features**:
- Structured logging from all agents
- Log aggregation and indexing
- Search and analysis in Kibana
- Pre-built dashboards for agent logs

**Documentation**: See `config/logging/README.md`

### 2. Prometheus

**Purpose**: Metrics collection and time-series database

**Configuration**:
- `config/monitoring/prometheus.yml`: Standard Prometheus config
- `monitoring/prometheus/k8s-prometheus.yml`: Kubernetes-optimized config

**Setup**:
```bash
# Using Docker
docker run -d \
  -p 9090:9090 \
  -v $(pwd)/config/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Using Kubernetes
kubectl apply -f kubernetes/monitoring/servicemonitor.yaml
```

**Access**: http://localhost:9090

**Metrics Collected**:
- Agent health and status
- CPU and memory usage
- Action success/failure rates
- Task completion rates
- Security events
- System resources

### 3. Grafana

**Purpose**: Metrics visualization and dashboards

**Dashboards**:
1. **System Health Dashboard**: Overall system health
2. **Agent Performance Dashboard**: Individual agent performance
3. **Resource Usage Dashboard**: CPU, memory, disk usage
4. **Error Rates Dashboard**: Error rates and failures
5. **Event Flows Dashboard**: Event timeline and flows
6. **Security Monitoring Dashboard**: Security events and alerts (NEW)
7. **Agent Actions Dashboard**: Action rates and success rates (NEW)

**Setup**:
```bash
# Using Docker
docker run -d \
  -p 3000:3000 \
  -v $(pwd)/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards \
  grafana/grafana

# Using Kubernetes
kubectl apply -f monitoring/grafana/
```

**Access**: http://localhost:3000 (admin/admin)

**Import Dashboards**:
1. Go to Grafana UI
2. Navigate to Dashboards → Import
3. Upload dashboard JSON files from `monitoring/grafana/dashboards/`

### 4. Alertmanager

**Purpose**: Alert routing and notification

**Configuration**: `monitoring/alertmanager/alertmanager.yml`

**Features**:
- Route alerts by severity
- Multiple notification channels (Email, Slack, PagerDuty)
- Alert grouping and deduplication
- Inhibition rules

**Setup**:
```bash
# Using Docker
docker run -d \
  -p 9093:9093 \
  -v $(pwd)/monitoring/alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager
```

**Access**: http://localhost:9093

### 5. Kubernetes ServiceMonitor

**Purpose**: Automatic metric discovery in Kubernetes

**File**: `kubernetes/monitoring/servicemonitor.yaml`

**Features**:
- Automatic discovery of agent pods
- Scraping configuration
- Label-based filtering

**Apply**:
```bash
kubectl apply -f kubernetes/monitoring/servicemonitor.yaml
```

## Alerting Rules

### Critical Alerts

- **AgentDown**: Agent is down for more than 1 minute
- **SecurityIntrusionDetected**: Security intrusion detected
- **SystemHighLoad**: System load above threshold

### Warning Alerts

- **AgentHighErrorRate**: High error rate for agent
- **HighCPUUsage**: CPU usage above 90%
- **HighMemoryUsage**: Memory usage above 90%
- **DiskSpaceLow**: Disk space below 10%

### Security Alerts

- **SecurityIntrusionDetected**: Immediate notification
- **BlockedAttacks**: High number of blocked attacks

## Monitoring Best Practices

1. **Set Appropriate Thresholds**: Adjust alert thresholds based on your environment
2. **Monitor Key Metrics**: Focus on metrics that indicate system health
3. **Regular Dashboard Review**: Review dashboards regularly for trends
4. **Alert Tuning**: Tune alerts to reduce false positives
5. **Log Retention**: Set appropriate log retention policies
6. **Backup Metrics**: Backup Prometheus data regularly

## Security Monitoring

### Security Dashboard

The Security Monitoring Dashboard provides:
- Intrusion alerts over time
- Blocked attacks statistics
- Top attack sources
- Security agent health

### Security Alerts

- **Intrusion Detected**: Immediate critical alert
- **High Attack Rate**: Warning when attack rate is high
- **Security Agent Down**: Critical alert if security agent is down

## Troubleshooting

### Prometheus Not Scraping

1. Check ServiceMonitor:
```bash
kubectl get servicemonitor -n ai-cloud-production
kubectl describe servicemonitor ai-cloud-agents -n ai-cloud-production
```

2. Check Prometheus targets:
```bash
# Access Prometheus UI
# Navigate to Status → Targets
```

3. Check pod annotations:
```bash
kubectl get pod <pod-name> -n ai-cloud-production -o yaml | grep prometheus
```

### Grafana Not Showing Data

1. Check data source:
```bash
# In Grafana UI: Configuration → Data Sources
# Verify Prometheus data source is configured
```

2. Check query:
```bash
# Test query in Prometheus UI first
# Then use same query in Grafana
```

### ELK Stack Not Receiving Logs

1. Check Logstash:
```bash
docker logs logstash
```

2. Check Elasticsearch:
```bash
curl http://localhost:9200/_cluster/health
```

3. Check agent logging:
```bash
# Verify agents are sending logs to Logstash
# Check agent logs for errors
```

## Next Steps

1. **Deploy Monitoring Stack**: Deploy Prometheus, Grafana, and ELK
2. **Import Dashboards**: Import Grafana dashboards
3. **Configure Alerts**: Set up Alertmanager with your notification channels
4. **Monitor**: Start monitoring your system
5. **Tune**: Adjust thresholds and alerts based on actual usage
