"""
Performance Monitor
Main orchestrator for performance monitoring and feedback
"""

import time
import logging
from typing import Dict, List, Optional
import threading

from .metrics_collector import MetricsCollector
from .agent_success_tracker import AgentSuccessTracker
from .timeseries_forecaster import TimeSeriesForecaster
from .prometheus_exporter import PrometheusMetricsExporter, AgentMetricsCollector

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self):
        # Initialize components
        self.metrics_collector = MetricsCollector(collection_interval=10)
        self.success_tracker = AgentSuccessTracker()
        self.forecaster = TimeSeriesForecaster()
        
        # Prometheus exporter
        self.prometheus_exporter = PrometheusMetricsExporter(port=9091)
        self.metrics_collector_prom = AgentMetricsCollector(self.prometheus_exporter)
        
        # Monitoring intervals
        self.forecast_interval = 300  # 5 minutes
        self.summary_interval = 3600  # 1 hour
        
        # Running state
        self.running = False
        self.monitoring_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start performance monitoring"""
        if self.running:
            logger.warning("Performance monitor is already running")
            return
        
        self.running = True
        
        # Start metrics collection
        self.metrics_collector.start()
        
        # Start Prometheus exporter
        self.prometheus_exporter.start_server()
        
        # Start monitoring loop
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Performance monitor started")
    
    def stop(self):
        """Stop performance monitoring"""
        self.running = False
        
        # Stop metrics collection
        self.metrics_collector.stop()
        
        # Stop Prometheus exporter
        self.prometheus_exporter.stop_server()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("Performance monitor stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_forecast = time.time()
        last_summary = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic forecasting
                if current_time - last_forecast >= self.forecast_interval:
                    self._update_forecasts()
                    last_forecast = current_time
                
                # Periodic summary
                if current_time - last_summary >= self.summary_interval:
                    self._generate_summary()
                    self._save_data()
                    last_summary = current_time
                
                # Update Prometheus metrics
                self._update_prometheus_metrics()
                
                # Sleep
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(60)
    
    def _update_forecasts(self):
        """Update performance forecasts"""
        logger.debug("Updating performance forecasts...")
        
        agents = [
            "self-healing",
            "scaling",
            "task-solving",
            "performance-monitoring",
            "coding",
            "security",
            "optimization"
        ]
        
        for agent_name in agents:
            # Forecast key metrics
            metrics_to_forecast = [
                "cpu_usage",
                "memory_usage",
                "success_rate",
                "latency_p95",
                "error_rate"
            ]
            
            for metric_name in metrics_to_forecast:
                # Get recent metrics
                recent_metrics = self.metrics_collector.get_recent_agent_metrics(agent_name, limit=100)
                if recent_metrics:
                    # Add to forecaster
                    for metric in recent_metrics[-10:]:  # Last 10 data points
                        value = metric.get(metric_name, 0.0)
                        if value > 0:
                            self.forecaster.add_data_point(agent_name, metric_name, value, metric["timestamp"])
                    
                    # Generate forecast
                    self.forecaster.forecast_linear_trend(agent_name, metric_name, horizon_seconds=3600)
    
    def _update_prometheus_metrics(self):
        """Update Prometheus metrics from collected data"""
        agents = [
            "self-healing",
            "scaling",
            "task-solving",
            "performance-monitoring",
            "coding",
            "security",
            "optimization"
        ]
        
        for agent_name in agents:
            # Get performance summary
            performance = self.success_tracker.calculate_performance(agent_name)
            
            # Get recent metrics
            recent_metrics = self.metrics_collector.get_recent_agent_metrics(agent_name, limit=1)
            
            if recent_metrics:
                latest = recent_metrics[-1]
                
                # Update Prometheus metrics
                self.metrics_collector_prom.update_agent_metrics(
                    agent_name=agent_name,
                    success_rate=performance.task_success_rate,
                    latency_p50=latest.get("latency_p50", 0.0),
                    latency_p95=latest.get("latency_p95", 0.0),
                    latency_p99=latest.get("latency_p99", 0.0),
                    cpu_usage=latest.get("cpu_usage", 0.0),
                    memory_usage=latest.get("memory_usage", 0.0),
                    task_success_rate=performance.task_success_rate,
                    failure_recovery_time=performance.average_recovery_time,
                    active_tasks=performance.active_tasks,
                    completed_tasks=performance.completed_tasks,
                    failed_tasks=performance.failed_tasks
                )
    
    def _generate_summary(self):
        """Generate performance summary"""
        logger.info("Generating performance summary...")
        
        summary = {
            "timestamp": time.time(),
            "agents": {}
        }
        
        agents = [
            "self-healing",
            "scaling",
            "task-solving",
            "performance-monitoring",
            "coding",
            "security",
            "optimization"
        ]
        
        for agent_name in agents:
            # Get performance
            performance = self.success_tracker.calculate_performance(agent_name)
            
            # Get forecasts
            forecasts = self.forecaster.get_recent_forecasts(agent_name, limit=5)
            
            summary["agents"][agent_name] = {
                "performance": {
                    "task_success_rate": performance.task_success_rate,
                    "average_recovery_time": performance.average_recovery_time,
                    "total_tasks": performance.total_tasks,
                    "average_cpu_usage": performance.average_cpu_usage,
                    "average_memory_usage": performance.average_memory_usage,
                    "average_latency_p95": performance.average_latency_p95
                },
                "forecasts": [
                    {
                        "metric": f.metric_name,
                        "predicted_value": f.predicted_value,
                        "confidence": f.confidence,
                        "trend": f.trend,
                        "recommendation": f.recommendation
                    }
                    for f in forecasts
                ]
            }
        
        logger.info("Performance summary generated")
        return summary
    
    def _save_data(self):
        """Save monitoring data"""
        self.metrics_collector.save_metrics()
        self.success_tracker.save_performance_data()
    
    def record_task_result(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        success: bool,
        execution_time: float,
        error_message: Optional[str] = None
    ):
        """Record task result for tracking"""
        self.success_tracker.record_task(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            success=success,
            execution_time=execution_time,
            error_message=error_message
        )
    
    def record_failure_recovery(
        self,
        failure_id: str,
        agent_name: str,
        failure_type: str,
        recovery_action: str,
        recovery_time: float,
        success: bool
    ):
        """Record failure and recovery"""
        self.success_tracker.record_failure(failure_id, agent_name, failure_type)
        self.success_tracker.record_recovery(failure_id, agent_name, recovery_action, success)
    
    def get_performance_summary(self, agent_name: Optional[str] = None) -> Dict:
        """Get performance summary"""
        return self.success_tracker.get_performance_summary(agent_name)
    
    def get_forecasts(self, agent_name: str) -> List[Dict]:
        """Get performance forecasts for an agent"""
        forecasts = self.forecaster.get_recent_forecasts(agent_name)
        return [
            {
                "metric_name": f.metric_name,
                "predicted_value": f.predicted_value,
                "confidence": f.confidence,
                "trend": f.trend,
                "recommendation": f.recommendation,
                "forecast_horizon": f.forecast_horizon
            }
            for f in forecasts
        ]

