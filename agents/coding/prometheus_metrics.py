"""
Prometheus metrics for Coding Agent
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import os

# Metrics
code_fixes_total = Counter(
    'code_fixes_total',
    'Total number of code fixes performed'
)

code_generations_total = Counter(
    'code_generations_total',
    'Total number of code generations performed'
)

code_fix_duration_seconds = Histogram(
    'code_fix_duration_seconds',
    'Duration of code fixes in seconds',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0]
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
def start_metrics_server(port=8086):
    """Start Prometheus metrics HTTP server"""
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}")

# Record metrics
def record_code_fix(duration_seconds: float):
    """Record a code fix"""
    code_fixes_total.inc()
    code_fix_duration_seconds.observe(duration_seconds)
    agent_requests_total.labels(agent='coding-agent', status='success').inc()

def record_code_generation():
    """Record a code generation"""
    code_generations_total.inc()
    agent_requests_total.labels(agent='coding-agent', status='success').inc()

def record_agent_error(error_type: str):
    """Record an agent error"""
    agent_errors_total.labels(agent='coding-agent', error_type=error_type).inc()

def set_agent_uptime(uptime_seconds: float):
    """Set agent uptime"""
    agent_uptime_seconds.labels(agent='coding-agent').set(uptime_seconds)

