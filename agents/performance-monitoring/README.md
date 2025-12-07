# Performance Monitoring Agent

## Purpose

The Performance Monitoring Agent is responsible for:
- Collecting metrics from Prometheus
- Detecting performance anomalies
- Identifying threshold violations
- Providing insights for optimization

## Responsibilities

1. **Metrics Collection**: Regularly queries Prometheus for metrics
2. **Anomaly Detection**: Identifies unusual patterns in metrics
3. **Threshold Monitoring**: Alerts when metrics exceed thresholds
4. **Performance Analysis**: Provides insights on system performance

## Endpoints

- `GET /health` - Health check endpoint
- `GET /metrics` - Get collected metrics
- `POST /action` - Execute a monitoring action
- `GET /status` - Get agent status

## Metrics Collected

- CPU usage
- Memory usage
- Network I/O
- Request latency
- Error rates

## Configuration

See `config.json` for Prometheus connection settings and anomaly detection thresholds.

## Events

- Publishes: `anomaly.detected`, `threshold.exceeded`
- Subscribes: `metrics.collected`

