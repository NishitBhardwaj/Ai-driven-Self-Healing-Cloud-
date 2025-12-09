"""
Prometheus metrics for Optimization Agent
"""

from prometheus_client import Counter, Gauge, start_http_server
import os

# Metrics
optimization_runs_total = Counter(
    'optimization_runs_total',
    'Total number of optimization runs'
)

cost_savings_total = Gauge(
    'cost_savings_total',
    'Total cost savings in dollars'
)

resource_optimizations_total = Counter(
    'resource_optimizations_total',
    'Total number of resource optimizations'
)

agent_requests_total = Counter(
    'agent_requests_total',
    'Total number of requests processed by agents',
    ['agent', 'status']
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total number of errors encountered by agents',
    ['agent', 'error_type']
)

agent_uptime_seconds = Gauge(
    'agent_uptime_seconds',
    'Agent uptime in seconds',
    ['agent']
)

# Start metrics server
def start_metrics_server(port=8087):
    """Start Prometheus metrics HTTP server"""
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}")

# Record metrics
def record_optimization_run():
    """Record an optimization run"""
    optimization_runs_total.inc()
    agent_requests_total.labels(agent='optimization-agent', status='success').inc()

def set_cost_savings(savings: float):
    """Set cost savings"""
    cost_savings_total.set(savings)

def record_resource_optimization():
    """Record a resource optimization"""
    resource_optimizations_total.inc()
    agent_requests_total.labels(agent='optimization-agent', status='success').inc()

def record_agent_error(error_type: str):
    """Record an agent error"""
    agent_errors_total.labels(agent='optimization-agent', error_type=error_type).inc()

def set_agent_uptime(uptime_seconds: float):
    """Set agent uptime"""
    agent_uptime_seconds.labels(agent='optimization-agent').set(uptime_seconds)

