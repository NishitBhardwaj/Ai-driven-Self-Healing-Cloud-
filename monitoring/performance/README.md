# Performance Monitoring and Feedback

This directory contains the performance monitoring system that continuously tracks system and agent performance, provides real-time metrics, and forecasts future performance.

## Overview

The performance monitoring system provides:
- **Real-Time Metrics**: Continuous collection of CPU, memory, latency, error rates
- **Agent-Specific Metrics**: Success rates, latency, scalability, resource usage per agent
- **Success Tracking**: Task success rates, failure recovery times, resource consumption
- **Time-Series Forecasting**: Predicts and optimizes future performance

## Components

### 1. Metrics Collector (`metrics_collector.py`)

Collects real-time performance metrics:

**System Metrics**:
- CPU, memory, disk, network usage
- Latency (P50, P95, P99)
- Error rate, request rate, throughput

**Agent Metrics**:
- CPU and memory usage per agent
- Success/failure rates
- Latency percentiles
- Task success rate
- Failure recovery time
- Resource consumption

**Usage**:
```python
from monitoring.performance import MetricsCollector

collector = MetricsCollector(collection_interval=10)
collector.start()

# Record system metrics
collector.record_system_metrics(
    cpu_usage=0.65,
    memory_usage=0.70,
    disk_usage=0.50,
    network_io=100.0,
    latency_p50=0.1,
    latency_p95=0.3,
    latency_p99=0.5,
    error_rate=0.01,
    request_rate=1000.0,
    throughput=10000.0
)

# Record agent metrics
collector.record_agent_metrics(
    agent_name="self-healing",
    cpu_usage=0.60,
    memory_usage=0.65,
    success_rate=0.95,
    failure_rate=0.05,
    latency_p50=0.2,
    latency_p95=0.5,
    latency_p99=0.8,
    task_success_rate=0.98,
    failure_recovery_time=2.5,
    resource_consumption={"cpu": 0.6, "memory": 0.65},
    active_tasks=5,
    completed_tasks=100,
    failed_tasks=2
)
```

### 2. Agent Success Tracker (`agent_success_tracker.py`)

Tracks agent performance over time:

**Metrics Tracked**:
- Task success rate
- Failure recovery time
- Resource consumption
- Task completion statistics

**Usage**:
```python
from monitoring.performance import AgentSuccessTracker

tracker = AgentSuccessTracker()

# Record task result
tracker.record_task(
    task_id="task-123",
    agent_name="self-healing",
    task_type="restart_service",
    success=True,
    execution_time=2.5
)

# Record failure and recovery
tracker.record_failure("failure-456", "self-healing", "service_crash")
tracker.record_recovery("failure-456", "self-healing", "restart_service", success=True)

# Get performance summary
performance = tracker.calculate_performance("self-healing")
print(f"Success rate: {performance.task_success_rate:.2%}")
print(f"Avg recovery time: {performance.average_recovery_time:.2f}s")
```

### 3. Time-Series Forecaster (`timeseries_forecaster.py`)

Forecasts future performance using time-series models:

**Forecasting Methods**:
- Simple Moving Average
- Exponential Smoothing
- Linear Trend

**Usage**:
```python
from monitoring.performance import TimeSeriesForecaster

forecaster = TimeSeriesForecaster()

# Add data points
forecaster.add_data_point("self-healing", "cpu_usage", 0.65)
forecaster.add_data_point("self-healing", "cpu_usage", 0.70)
forecaster.add_data_point("self-healing", "cpu_usage", 0.75)

# Forecast
forecast = forecaster.forecast_linear_trend(
    agent_name="self-healing",
    metric_name="cpu_usage",
    horizon_seconds=3600
)

print(f"Predicted CPU: {forecast.predicted_value:.2%}")
print(f"Trend: {forecast.trend}")
print(f"Recommendation: {forecast.recommendation}")
```

### 4. Prometheus Exporter (`prometheus_exporter.py`)

Exports agent metrics in Prometheus format:

**Features**:
- HTTP endpoint for metrics (`/metrics`)
- Prometheus text format
- Health check endpoint (`/health`)

**Usage**:
```python
from monitoring.performance import PrometheusMetricsExporter, AgentMetricsCollector

exporter = PrometheusMetricsExporter(port=9091)
exporter.start_server()

collector = AgentMetricsCollector(exporter)

# Update metrics
collector.update_agent_metrics(
    agent_name="self-healing",
    success_rate=0.95,
    latency_p50=0.2,
    latency_p95=0.5,
    latency_p99=0.8,
    cpu_usage=0.60,
    memory_usage=0.65,
    task_success_rate=0.98,
    failure_recovery_time=2.5,
    active_tasks=5,
    completed_tasks=100,
    failed_tasks=2
)

# Metrics available at http://localhost:9091/metrics
```

### 5. Performance Monitor (`performance_monitor.py`)

Main orchestrator for all performance monitoring:

**Usage**:
```python
from monitoring.performance import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start()

# Record task result
monitor.record_task_result(
    task_id="task-123",
    agent_name="self-healing",
    task_type="restart_service",
    success=True,
    execution_time=2.5
)

# Record failure recovery
monitor.record_failure_recovery(
    failure_id="failure-456",
    agent_name="self-healing",
    failure_type="service_crash",
    recovery_action="restart_service",
    recovery_time=2.5,
    success=True
)

# Get performance summary
summary = monitor.get_performance_summary("self-healing")

# Get forecasts
forecasts = monitor.get_forecasts("self-healing")
```

## Integration with Prometheus and Grafana

### Prometheus Configuration

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'agent-metrics'
    static_configs:
      - targets: ['localhost:9091']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Grafana Dashboard

Import the agent performance dashboard to visualize:
- Success rates over time
- Latency percentiles
- Resource usage
- Forecasts and trends

## Forecasting Methods

### Simple Moving Average

- **Use Case**: Stable metrics with little trend
- **Window**: Last N data points
- **Best For**: Short-term predictions

### Exponential Smoothing

- **Use Case**: Recent values more important
- **Alpha**: Smoothing factor (0-1)
- **Best For**: Medium-term predictions

### Linear Trend

- **Use Case**: Clear upward/downward trends
- **Method**: Linear regression
- **Best For**: Long-term predictions

## Metrics Exposed

### System Metrics

- `system_cpu_usage_percent`
- `system_memory_usage_percent`
- `system_latency_p95_seconds`
- `system_error_rate`
- `system_request_rate`
- `system_throughput`

### Agent Metrics

- `ai_cloud_success_rate{agent="..."}`
- `ai_cloud_latency_p95_seconds{agent="..."}`
- `ai_cloud_cpu_usage_percent{agent="..."}`
- `ai_cloud_memory_usage_percent{agent="..."}`
- `ai_cloud_task_success_rate{agent="..."}`
- `ai_cloud_failure_recovery_time_seconds{agent="..."}`
- `ai_cloud_active_tasks{agent="..."}`
- `ai_cloud_completed_tasks_total{agent="..."}`
- `ai_cloud_failed_tasks_total{agent="..."}`

## Best Practices

1. **Regular Collection**: Collect metrics every 10-60 seconds
2. **Forecast Updates**: Update forecasts every 5-15 minutes
3. **Data Retention**: Keep historical data for trend analysis
4. **Alert on Trends**: Set alerts based on forecasted values
5. **Review Forecasts**: Regularly review forecast accuracy

## Next Steps

1. **Integrate with Agents**: Add metrics collection to all agents
2. **Set Up Dashboards**: Create Grafana dashboards for visualization
3. **Configure Alerts**: Set up alerts based on forecasts
4. **Improve Forecasting**: Implement advanced models (LSTM, Transformers)
5. **Automated Actions**: Trigger actions based on forecasts

