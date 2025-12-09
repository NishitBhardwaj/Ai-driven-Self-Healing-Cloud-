# Centralized Logging System (ELK Stack)

This directory contains configuration files for the ELK Stack (Elasticsearch, Logstash, Kibana) to provide centralized logging for all agents.

## Overview

The ELK Stack provides:
- **Elasticsearch**: Centralized log storage and search
- **Logstash**: Log ingestion, filtering, and transformation
- **Kibana**: Log visualization and dashboards

## Configuration Files

### 1. Elasticsearch Configuration (`elasticsearch.yml`)

Elasticsearch configuration for log storage:
- Cluster name: `ai-cloud-logging`
- HTTP port: `9200`
- Security disabled (for development)
- Auto-create indices enabled

**Connection**: Agents connect to `http://localhost:9200`

### 2. Logstash Configuration (`logstash.conf`)

Logstash pipeline configuration:
- **Inputs**:
  - TCP port 5000 (for Go agents)
  - UDP port 5001 (for high-volume logs)
  - HTTP port 8080 (for REST API logs)
  - File input (for file-based logs)
- **Filters**:
  - Parse agent logs
  - Extract agent information
  - Parse timestamps
  - Extract actions, explanations, confidence levels
  - Classify log types (error, action, info)
- **Outputs**:
  - Elasticsearch index: `agent-logs-%{+YYYY.MM.dd}`
  - Index template: `agent-logs`

### 3. Kibana Configuration (`kibana.yml`)

Kibana configuration for log visualization:
- Server port: `5601`
- Elasticsearch connection: `http://elasticsearch:9200`
- Security disabled (for development)

**Access**: Open `http://localhost:5601` in browser

### 4. Docker Compose (`elk-docker-compose.yml`)

Docker Compose file to run the entire ELK Stack:
- Elasticsearch service
- Logstash service
- Kibana service
- Network configuration
- Volume mounts

## Setup

### Using Docker Compose

```bash
# Start ELK Stack
cd config/logging
docker-compose -f elk-docker-compose.yml up -d

# Check status
docker-compose -f elk-docker-compose.yml ps

# View logs
docker-compose -f elk-docker-compose.yml logs -f

# Stop ELK Stack
docker-compose -f elk-docker-compose.yml down
```

### Manual Setup

1. **Start Elasticsearch**:
```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -v $(pwd)/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

2. **Start Logstash**:
```bash
docker run -d \
  --name logstash \
  -p 5000:5000 \
  -p 5001:5001/udp \
  -v $(pwd)/logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  docker.elastic.co/logstash/logstash:8.11.0
```

3. **Start Kibana**:
```bash
docker run -d \
  --name kibana \
  -p 5601:5601 \
  -v $(pwd)/kibana.yml:/usr/share/kibana/config/kibana.yml \
  docker.elastic.co/kibana/kibana:8.11.0
```

## Agent Logging

### Go Agents

Agents use the `ELKLogger` from `config/logging/agent_logger.go`:

```go
import "github.com/ai-driven-self-healing-cloud/config/logging"

elkLogger := logging.GetDefaultELKLogger()

// Log action
elkLogger.LogAction(agentID, agentName, "restart_pod", explanation)

// Log error
elkLogger.LogError(agentID, agentName, err, context)

// Log explanation
elkLogger.LogExplanation(agentID, agentName, explanation)

// Log confidence
elkLogger.LogConfidence(agentID, agentName, 0.95, "auto", "High confidence based on historical data")
```

### Python Agents

Python agents can send logs via TCP/UDP to Logstash:

```python
import json
import socket
import time

def log_to_elk(agent_id, agent_name, action, explanation, confidence):
    log_entry = {
        "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "agent_id": agent_id,
        "agent_name": agent_name,
        "action": action,
        "action_taken": action,
        "explanation": explanation,
        "confidence": confidence,
        "log_type": "action",
        "level": "info"
    }
    
    # Send to Logstash via TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 5000))
        sock.sendall(json.dumps(log_entry).encode() + b'\n')
    finally:
        sock.close()
```

## Logged Events

### Action Triggers

All agent actions are logged with:
- Agent ID and name
- Action type
- Timestamp
- Explanation
- Confidence level
- Mode (auto/manual)

### Errors

All errors are logged with:
- Agent ID and name
- Error message
- Error type
- Context information
- Timestamp

### Explanations

All explanations are logged with:
- Full explanation text
- Reasoning chain
- Confidence level
- Alternative actions
- Context

### Confidence Levels

Confidence levels are logged with:
- Confidence value (0.0 to 1.0)
- Mode (auto/manual)
- Reasoning for confidence
- Timestamp

## Kibana Dashboards

### Pre-configured Dashboards

1. **Agent Actions Dashboard** (`agent-actions-dashboard.json`)
   - Visualize all agent actions
   - Filter by agent, action type, mode
   - View explanations and confidence levels

2. **Agent Errors Dashboard** (`agent-errors-dashboard.json`)
   - Monitor agent errors
   - Filter by error type, agent
   - Track error trends

3. **Agent Explanations Dashboard** (`agent-explanations-dashboard.json`)
   - View all explanations
   - Filter by agent, confidence level
   - View reasoning chains

### Creating Custom Dashboards

1. Open Kibana at `http://localhost:5601`
2. Go to **Dashboard** → **Create Dashboard**
3. Add visualizations:
   - **Time Series**: Agent actions over time
   - **Pie Chart**: Actions by agent
   - **Bar Chart**: Confidence levels
   - **Data Table**: Recent actions with explanations
4. Save dashboard

## Index Patterns

### Default Index Pattern

- **Pattern**: `agent-logs-*`
- **Time Field**: `@timestamp`
- **Format**: Daily indices (agent-logs-2024.01.01)

### Creating Index Pattern in Kibana

1. Go to **Management** → **Stack Management** → **Index Patterns**
2. Click **Create Index Pattern**
3. Enter pattern: `agent-logs-*`
4. Select time field: `@timestamp`
5. Click **Create Index Pattern**

## Query Examples

### Find All Actions by Agent

```
agent_name:"Self-Healing Agent" AND log_type:action
```

### Find High Confidence Decisions

```
confidence:>0.9 AND mode:auto
```

### Find Errors in Last Hour

```
log_type:error AND @timestamp:[now-1h TO now]
```

### Find Actions with Explanations

```
has_explanation:true AND action:*
```

### Find Auto Mode Actions

```
mode:auto AND log_type:action
```

## Environment Variables

Set these environment variables to configure ELK Stack:

```bash
# Logstash connection
export LOGSTASH_HOST=localhost
export LOGSTASH_PORT=5000

# Elasticsearch connection
export ELASTICSEARCH_URL=http://localhost:9200

# Environment
export ENVIRONMENT=development
```

## Troubleshooting

### Logs Not Appearing in Kibana

1. Check Logstash is running: `docker ps | grep logstash`
2. Check Elasticsearch is running: `curl http://localhost:9200/_cluster/health`
3. Check index exists: `curl http://localhost:9200/_cat/indices`
4. Verify Logstash pipeline: `docker logs logstash`

### Connection Errors

1. Verify network connectivity
2. Check firewall settings
3. Verify ports are not in use
4. Check Docker network configuration

### Performance Issues

1. Increase Elasticsearch heap size
2. Adjust Logstash batch size
3. Use UDP for high-volume logs
4. Consider log rotation

## Next Steps

1. **Start ELK Stack**: Run Docker Compose
2. **Configure Agents**: Update agents to use ELK logger
3. **Create Dashboards**: Set up Kibana dashboards
4. **Monitor Logs**: Use Kibana to monitor agent activity
5. **Set Up Alerts**: Configure alerts for critical errors

