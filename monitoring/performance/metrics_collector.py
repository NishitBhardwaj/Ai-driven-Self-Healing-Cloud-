"""
Real-Time Metrics Collector
Continuously collects performance metrics: CPU, memory, latency, error rates
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import deque
import threading
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System-wide performance metrics"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    error_rate: float
    request_rate: float
    throughput: float


@dataclass
class AgentMetrics:
    """Agent-specific performance metrics"""
    timestamp: float
    agent_name: str
    cpu_usage: float
    memory_usage: float
    success_rate: float
    failure_rate: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    task_success_rate: float
    failure_recovery_time: float
    resource_consumption: Dict[str, float]
    active_tasks: int
    completed_tasks: int
    failed_tasks: int


class MetricsCollector:
    """Collects real-time performance metrics"""
    
    def __init__(self, collection_interval: int = 10):
        self.collection_interval = collection_interval  # seconds
        
        # Metrics storage
        self.system_metrics: deque = deque(maxlen=10000)
        self.agent_metrics: Dict[str, deque] = {}
        
        # Collection state
        self.running = False
        self.collection_thread: Optional[threading.Thread] = None
        
        # Storage
        self.storage_path = Path("data/monitoring/performance")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start metrics collection"""
        if self.running:
            logger.warning("Metrics collector is already running")
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collector started")
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=10)
        logger.info("Metrics collector stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                if system_metrics:
                    self.system_metrics.append(system_metrics)
                
                # Collect agent metrics
                for agent_name in self._get_agent_list():
                    agent_metrics = self._collect_agent_metrics(agent_name)
                    if agent_metrics:
                        if agent_name not in self.agent_metrics:
                            self.agent_metrics[agent_name] = deque(maxlen=10000)
                        self.agent_metrics[agent_name].append(agent_metrics)
                
                # Sleep until next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}", exc_info=True)
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect system-wide metrics"""
        try:
            # In production, this would fetch from monitoring system
            # For now, this is a placeholder that would be called with actual metrics
            # from Prometheus, system APIs, etc.
            
            # Placeholder - would be replaced with actual collection
            return None
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def _collect_agent_metrics(self, agent_name: str) -> Optional[AgentMetrics]:
        """Collect agent-specific metrics"""
        try:
            # In production, this would fetch from agent's metrics endpoint
            # For now, this is a placeholder
            return None
        except Exception as e:
            logger.error(f"Error collecting metrics for {agent_name}: {e}")
            return None
    
    def _get_agent_list(self) -> List[str]:
        """Get list of agents to monitor"""
        return [
            "self-healing",
            "scaling",
            "task-solving",
            "performance-monitoring",
            "coding",
            "security",
            "optimization"
        ]
    
    def record_system_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_io: float,
        latency_p50: float,
        latency_p95: float,
        latency_p99: float,
        error_rate: float,
        request_rate: float,
        throughput: float
    ):
        """Record system metrics"""
        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            error_rate=error_rate,
            request_rate=request_rate,
            throughput=throughput
        )
        
        self.system_metrics.append(metrics)
        logger.debug(f"Recorded system metrics: CPU={cpu_usage:.2%}, Memory={memory_usage:.2%}")
    
    def record_agent_metrics(
        self,
        agent_name: str,
        cpu_usage: float,
        memory_usage: float,
        success_rate: float,
        failure_rate: float,
        latency_p50: float,
        latency_p95: float,
        latency_p99: float,
        task_success_rate: float,
        failure_recovery_time: float,
        resource_consumption: Dict[str, float],
        active_tasks: int,
        completed_tasks: int,
        failed_tasks: int
    ):
        """Record agent-specific metrics"""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = deque(maxlen=10000)
        
        metrics = AgentMetrics(
            timestamp=time.time(),
            agent_name=agent_name,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            success_rate=success_rate,
            failure_rate=failure_rate,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            task_success_rate=task_success_rate,
            failure_recovery_time=failure_recovery_time,
            resource_consumption=resource_consumption,
            active_tasks=active_tasks,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks
        )
        
        self.agent_metrics[agent_name].append(metrics)
        logger.debug(f"Recorded metrics for {agent_name}: Success={success_rate:.2%}, Latency P95={latency_p95:.3f}s")
    
    def get_recent_system_metrics(self, limit: int = 1000) -> List[Dict]:
        """Get recent system metrics"""
        return [asdict(m) for m in list(self.system_metrics)[-limit:]]
    
    def get_recent_agent_metrics(self, agent_name: str, limit: int = 1000) -> List[Dict]:
        """Get recent agent metrics"""
        if agent_name not in self.agent_metrics:
            return []
        return [asdict(m) for m in list(self.agent_metrics[agent_name])[-limit:]]
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics"""
        summary = {
            "system": {
                "total_metrics": len(self.system_metrics),
                "latest_timestamp": self.system_metrics[-1].timestamp if self.system_metrics else None
            },
            "agents": {}
        }
        
        for agent_name, metrics_deque in self.agent_metrics.items():
            if metrics_deque:
                latest = metrics_deque[-1]
                summary["agents"][agent_name] = {
                    "total_metrics": len(metrics_deque),
                    "latest_success_rate": latest.success_rate,
                    "latest_latency_p95": latest.latency_p95,
                    "latest_timestamp": latest.timestamp
                }
        
        return summary
    
    def save_metrics(self):
        """Save metrics to disk"""
        timestamp = int(time.time())
        
        # Save system metrics
        if self.system_metrics:
            system_file = self.storage_path / f"system_metrics_{timestamp}.json"
            with open(system_file, 'w') as f:
                json.dump([asdict(m) for m in list(self.system_metrics)[-1000:]], f, indent=2)
            logger.info(f"Saved {len(self.system_metrics)} system metrics to {system_file}")
        
        # Save agent metrics
        for agent_name, metrics_deque in self.agent_metrics.items():
            if metrics_deque:
                agent_file = self.storage_path / f"{agent_name}_metrics_{timestamp}.json"
                with open(agent_file, 'w') as f:
                    json.dump([asdict(m) for m in list(metrics_deque)[-1000:]], f, indent=2)
                logger.info(f"Saved {len(metrics_deque)} metrics for {agent_name} to {agent_file}")

