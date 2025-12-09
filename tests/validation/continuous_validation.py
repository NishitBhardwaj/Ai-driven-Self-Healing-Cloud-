"""
Continuous Validation
Monitors system performance improvements over multiple feedback loops
"""

import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque
import threading

logger = logging.getLogger(__name__)


@dataclass
class PerformanceSnapshot:
    """Snapshot of system performance at a point in time"""
    timestamp: float
    success_rate: float
    avg_latency: float
    error_rate: float
    resource_efficiency: float
    cost_efficiency: float


class ContinuousValidator:
    """Continuously validates system performance improvements"""
    
    def __init__(self, validation_interval: int = 3600):  # 1 hour
        self.validation_interval = validation_interval
        self.performance_history: deque = deque(maxlen=1000)
        
        self.running = False
        self.validation_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start continuous validation"""
        if self.running:
            logger.warning("Continuous validator is already running")
            return
        
        self.running = True
        self.validation_thread = threading.Thread(target=self._validation_loop, daemon=True)
        self.validation_thread.start()
        logger.info("Continuous validation started")
    
    def stop(self):
        """Stop continuous validation"""
        self.running = False
        if self.validation_thread:
            self.validation_thread.join(timeout=10)
        logger.info("Continuous validation stopped")
    
    def _validation_loop(self):
        """Main validation loop"""
        while self.running:
            try:
                snapshot = self._capture_performance_snapshot()
                if snapshot:
                    self.performance_history.append(snapshot)
                    self._analyze_trends()
                
                time.sleep(self.validation_interval)
                
            except Exception as e:
                logger.error(f"Error in validation loop: {e}", exc_info=True)
                time.sleep(self.validation_interval)
    
    def _capture_performance_snapshot(self) -> Optional[PerformanceSnapshot]:
        """Capture current performance snapshot"""
        try:
            from monitoring.performance.performance_monitor import PerformanceMonitor
            from ai_engine.continuous_learning.data_collector import DataCollector
            
            monitor = PerformanceMonitor()
            data_collector = DataCollector()
            
            # Get performance summaries for all agents
            agents = ["self-healing", "scaling", "task-solving", "optimization"]
            
            total_success_rate = 0.0
            total_latency = 0.0
            total_error_rate = 0.0
            count = 0
            
            for agent_name in agents:
                summary = monitor.get_performance_summary(agent_name)
                if summary:
                    total_success_rate += summary.get("task_success_rate", 0.0)
                    total_latency += summary.get("average_latency_p95", 0.0)
                    count += 1
            
            if count == 0:
                return None
            
            avg_success_rate = total_success_rate / count
            avg_latency = total_latency / count
            error_rate = 1.0 - avg_success_rate
            
            # Calculate resource efficiency (simplified)
            resource_efficiency = 0.7  # Placeholder
            
            # Calculate cost efficiency (simplified)
            cost_efficiency = 0.8  # Placeholder
            
            return PerformanceSnapshot(
                timestamp=time.time(),
                success_rate=avg_success_rate,
                avg_latency=avg_latency,
                error_rate=error_rate,
                resource_efficiency=resource_efficiency,
                cost_efficiency=cost_efficiency
            )
            
        except Exception as e:
            logger.error(f"Error capturing performance snapshot: {e}")
            return None
    
    def _analyze_trends(self):
        """Analyze performance trends"""
        if len(self.performance_history) < 2:
            return
        
        recent = list(self.performance_history)[-10:]  # Last 10 snapshots
        
        # Calculate trends
        success_rate_trend = self._calculate_trend([s.success_rate for s in recent])
        latency_trend = self._calculate_trend([s.avg_latency for s in recent])
        error_rate_trend = self._calculate_trend([s.error_rate for s in recent])
        
        # Log improvements
        if success_rate_trend > 0.01:  # 1% improvement
            logger.info(f"Success rate improving: +{success_rate_trend:.2%} trend")
        
        if latency_trend < -0.01:  # 1% reduction
            logger.info(f"Latency improving: {latency_trend:.2%} trend")
        
        if error_rate_trend < -0.01:  # 1% reduction
            logger.info(f"Error rate improving: {error_rate_trend:.2%} trend")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (slope) of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope
    
    def get_performance_report(self) -> Dict:
        """Get performance improvement report"""
        if len(self.performance_history) < 2:
            return {"status": "insufficient_data"}
        
        recent = list(self.performance_history)[-10:]
        oldest = recent[0]
        newest = recent[-1]
        
        improvements = {
            "success_rate_change": newest.success_rate - oldest.success_rate,
            "latency_change": newest.avg_latency - oldest.avg_latency,
            "error_rate_change": newest.error_rate - oldest.error_rate,
            "time_span": newest.timestamp - oldest.timestamp
        }
        
        return {
            "snapshots": len(self.performance_history),
            "improvements": improvements,
            "trends": {
                "success_rate": self._calculate_trend([s.success_rate for s in recent]),
                "latency": self._calculate_trend([s.avg_latency for s in recent]),
                "error_rate": self._calculate_trend([s.error_rate for s in recent])
            }
        }

