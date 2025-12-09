"""
Prometheus Exporter for Agent-Specific Metrics
Exposes agent metrics in Prometheus format
"""

import time
import logging
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

logger = logging.getLogger(__name__)


class PrometheusMetricsExporter:
    """Exports agent metrics in Prometheus format"""
    
    def __init__(self, port: int = 9091):
        self.port = port
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
    
    def register_metric(
        self,
        agent_name: str,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Register a metric value"""
        key = f"{agent_name}_{metric_name}"
        if labels:
            key += "_" + "_".join(f"{k}={v}" for k, v in sorted(labels.items()))
        
        self.metrics[key] = {
            "value": value,
            "timestamp": time.time(),
            "labels": labels or {}
        }
    
    def format_prometheus_metrics(self) -> str:
        """Format metrics in Prometheus text format"""
        lines = []
        
        # Group metrics by name
        metric_groups: Dict[str, List[Dict]] = {}
        for key, data in self.metrics.items():
            # Extract metric name (before first _)
            parts = key.split("_", 1)
            if len(parts) == 2:
                agent_name, metric_name = parts
                full_name = f"ai_cloud_{metric_name}"
            else:
                full_name = f"ai_cloud_{key}"
            
            if full_name not in metric_groups:
                metric_groups[full_name] = []
            
            metric_groups[full_name].append({
                "key": key,
                "value": data["value"],
                "labels": data["labels"]
            })
        
        # Format each metric group
        for metric_name, metrics in metric_groups.items():
            for metric in metrics:
                labels_str = ""
                if metric["labels"]:
                    labels_str = "{" + ", ".join(
                        f'{k}="{v}"' for k, v in sorted(metric["labels"].items())
                    ) + "}"
                
                lines.append(f"{metric_name}{labels_str} {metric['value']}")
        
        return "\n".join(lines) + "\n"
    
    def start_server(self):
        """Start HTTP server to expose metrics"""
        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/metrics":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; version=0.0.4")
                    self.end_headers()
                    self.wfile.write(exporter.format_prometheus_metrics().encode())
                elif self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "healthy"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        exporter = self
        
        try:
            self.server = HTTPServer(("0.0.0.0", self.port), MetricsHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            logger.info(f"Prometheus metrics exporter started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start metrics exporter: {e}")
    
    def stop_server(self):
        """Stop HTTP server"""
        if self.server:
            self.server.shutdown()
            logger.info("Prometheus metrics exporter stopped")


class AgentMetricsCollector:
    """Collects and exports agent-specific metrics"""
    
    def __init__(self, exporter: PrometheusMetricsExporter):
        self.exporter = exporter
        
        # Metrics storage
        self.agent_metrics: Dict[str, Dict[str, float]] = {}
    
    def update_agent_metrics(
        self,
        agent_name: str,
        success_rate: float,
        latency_p50: float,
        latency_p95: float,
        latency_p99: float,
        cpu_usage: float,
        memory_usage: float,
        task_success_rate: float,
        failure_recovery_time: float,
        active_tasks: int,
        completed_tasks: int,
        failed_tasks: int
    ):
        """Update agent metrics and export to Prometheus"""
        
        # Store metrics
        self.agent_metrics[agent_name] = {
            "success_rate": success_rate,
            "latency_p50": latency_p50,
            "latency_p95": latency_p95,
            "latency_p99": latency_p99,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "task_success_rate": task_success_rate,
            "failure_recovery_time": failure_recovery_time,
            "active_tasks": active_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks
        }
        
        # Export to Prometheus
        labels = {"agent": agent_name}
        
        self.exporter.register_metric(agent_name, "success_rate", success_rate, labels)
        self.exporter.register_metric(agent_name, "latency_p50_seconds", latency_p50, labels)
        self.exporter.register_metric(agent_name, "latency_p95_seconds", latency_p95, labels)
        self.exporter.register_metric(agent_name, "latency_p99_seconds", latency_p99, labels)
        self.exporter.register_metric(agent_name, "cpu_usage_percent", cpu_usage * 100, labels)
        self.exporter.register_metric(agent_name, "memory_usage_percent", memory_usage * 100, labels)
        self.exporter.register_metric(agent_name, "task_success_rate", task_success_rate, labels)
        self.exporter.register_metric(agent_name, "failure_recovery_time_seconds", failure_recovery_time, labels)
        self.exporter.register_metric(agent_name, "active_tasks", float(active_tasks), labels)
        self.exporter.register_metric(agent_name, "completed_tasks_total", float(completed_tasks), labels)
        self.exporter.register_metric(agent_name, "failed_tasks_total", float(failed_tasks), labels)
    
    def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, float]]:
        """Get current metrics for an agent"""
        return self.agent_metrics.get(agent_name)

