"""
Prometheus metrics for Security Agent
"""

from prometheus_client import Counter, Gauge, start_http_server
import os

# Metrics
intrusion_alerts_total = Counter(
    'intrusion_alerts_total',
    'Total number of intrusion alerts',
    ['severity', 'type']
)

blocked_attacks_total = Counter(
    'blocked_attacks_total',
    'Total number of blocked attacks'
)

security_scans_total = Counter(
    'security_scans_total',
    'Total number of security scans performed'
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
def start_metrics_server(port=8084):
    """Start Prometheus metrics HTTP server"""
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}")

# Record metrics
def record_intrusion_alert(severity: str, alert_type: str):
    """Record an intrusion alert"""
    intrusion_alerts_total.labels(severity=severity, type=alert_type).inc()
    agent_requests_total.labels(agent='security-agent', status='success').inc()

def record_blocked_attack():
    """Record a blocked attack"""
    blocked_attacks_total.inc()
    agent_requests_total.labels(agent='security-agent', status='success').inc()

def record_security_scan():
    """Record a security scan"""
    security_scans_total.inc()
    agent_requests_total.labels(agent='security-agent', status='success').inc()

def record_agent_error(error_type: str):
    """Record an agent error"""
    agent_errors_total.labels(agent='security-agent', error_type=error_type).inc()

def set_agent_uptime(uptime_seconds: float):
    """Set agent uptime"""
    agent_uptime_seconds.labels(agent='security-agent').set(uptime_seconds)

