# Configuration Directory

This folder contains configuration files for agents, cloud services, and system settings. Configuration files allow customization of system behavior without code changes.

## Overview

Configuration is organized into:

- **`/config/agents-config/`**: Agent-specific configuration files
- **`/config/cloud-config/`**: Cloud service configuration files

## Agent Configuration

Agent configuration files are located in `/config/agents-config/` and define:

- **Communication Settings**: Endpoints, ports, protocols
- **Behavior Parameters**: Thresholds, timeouts, retry policies
- **Resource Limits**: CPU, memory, connection limits
- **Mode Settings**: Auto/manual mode, logging levels

### Configuration Format

Configurations use YAML format for readability:

```yaml
# agents-config/self-healing-agent.yaml
agent:
  name: self-healing
  mode: auto
  log_level: INFO
  
communication:
  grpc_port: 50051
  rest_port: 8080
  message_queue: rabbitmq
  
monitoring:
  health_check_interval: 30s
  metrics_port: 9090
  
behavior:
  failure_detection:
    cpu_threshold: 80
    memory_threshold: 85
    check_interval: 10s
  
  recovery:
    max_retries: 3
    retry_delay: 5s
    timeout: 60s
```

### Loading Configuration

Agents load configuration at startup:

```python
import yaml

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config('config/agents-config/self-healing-agent.yaml')
```

## Cloud Configuration

Cloud configuration files are located in `/config/cloud-config/` and define:

- **LocalStack Settings**: Endpoint URLs, service configurations
- **MinIO Settings**: Storage endpoints, credentials
- **AWS Settings**: Region, credentials (for production)
- **Database Settings**: Connection strings, credentials

### Configuration Example

```yaml
# cloud-config/localstack.yaml
localstack:
  endpoint: http://localhost:4566
  services:
    - s3
    - dynamodb
    - lambda
    - sqs
  
  s3:
    buckets:
      - agent-logs
      - agent-data
  
  dynamodb:
    tables:
      - name: agent_events
        key_schema:
          - attribute_name: event_id
            key_type: HASH
```

## Environment-Specific Configuration

Different configurations for different environments:

- **`config-dev.yaml`**: Development environment
- **`config-staging.yaml`**: Staging environment
- **`config-prod.yaml`**: Production environment

### Using Environment Variables

Override configuration with environment variables:

```bash
export AGENT_MODE=manual
export LOG_LEVEL=DEBUG
export DATABASE_HOST=localhost
```

## Configuration Management

### Version Control

- **Sensitive Data**: Never commit secrets to version control
- **Templates**: Use configuration templates with placeholders
- **Secrets Management**: Use Kubernetes Secrets or external secret managers

### Configuration Validation

Validate configuration on load:

```python
import jsonschema

schema = {
    "type": "object",
    "properties": {
        "agent": {"type": "object"},
        "communication": {"type": "object"}
    },
    "required": ["agent", "communication"]
}

def validate_config(config, schema):
    jsonschema.validate(config, schema)
```

## Best Practices

1. **Separate Concerns**: Keep agent config separate from cloud config
2. **Use Defaults**: Provide sensible defaults
3. **Documentation**: Document all configuration options
4. **Validation**: Validate configuration on load
5. **Secrets**: Never store secrets in configuration files
6. **Environment Variables**: Use environment variables for sensitive data

## Configuration Examples

### Self-Healing Agent

```yaml
agent:
  name: self-healing
  mode: auto
  
behavior:
  failure_detection:
    cpu_threshold: 80
    memory_threshold: 85
  recovery:
    max_retries: 3
```

### Scaling Agent

```yaml
agent:
  name: scaling
  mode: auto
  
behavior:
  scaling:
    min_replicas: 2
    max_replicas: 10
    target_cpu: 70
    scale_up_threshold: 80
    scale_down_threshold: 50
```

### Task-Solving Agent

```yaml
agent:
  name: task-solving
  mode: auto
  
behavior:
  task_processing:
    max_concurrent_tasks: 10
    timeout: 300s
    retry_policy:
      max_retries: 3
      backoff: exponential
```

## Related Documentation

- Agent development: `/agents/README.md`
- Cloud simulation: `/cloud-simulation/README.md`
- Kubernetes: `/kubernetes/README.md`

