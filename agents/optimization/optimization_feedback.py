"""
Optimization Feedback System
Continuously evaluates resource usage and optimizes cost function
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Resource usage metrics at a point in time"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    response_time: float
    throughput: float
    error_rate: float
    cost_per_hour: float


@dataclass
class OptimizationFeedback:
    """Feedback for optimization decisions"""
    timestamp: float
    action_taken: str
    resource_before: ResourceMetrics
    resource_after: ResourceMetrics
    cost_change: float
    performance_change: float
    optimization_score: float
    recommendation: str


class OptimizationFeedbackSystem:
    """Continuously evaluates and optimizes resource management"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        
        # Resource metrics history
        self.metrics_history: deque = deque(maxlen=window_size)
        
        # Optimization feedback history
        self.feedback_history: deque = deque(maxlen=window_size)
        
        # Cost function parameters (learned over time)
        self.cost_weights = {
            "cpu_weight": 1.0,
            "memory_weight": 1.0,
            "response_time_weight": 0.5,
            "error_rate_weight": 2.0,
            "idle_penalty": 0.3,
            "over_provision_penalty": 1.5
        }
        
        # Performance thresholds
        self.thresholds = {
            "optimal_cpu": (0.4, 0.8),
            "optimal_memory": (0.4, 0.8),
            "max_response_time": 1.0,
            "max_error_rate": 0.01
        }
        
        # Storage
        self.storage_path = Path("data/optimization")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def record_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_io: float,
        response_time: float,
        throughput: float,
        error_rate: float,
        cost_per_hour: float
    ):
        """Record current resource metrics"""
        metrics = ResourceMetrics(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            cost_per_hour=cost_per_hour
        )
        
        self.metrics_history.append(metrics)
        logger.debug(f"Recorded metrics: CPU={cpu_usage:.2%}, Memory={memory_usage:.2%}, Cost=${cost_per_hour:.2f}/hr")
    
    def evaluate_optimization(
        self,
        action_taken: str,
        resource_before: ResourceMetrics,
        resource_after: ResourceMetrics
    ) -> OptimizationFeedback:
        """Evaluate optimization action and generate feedback"""
        
        # Calculate changes
        cost_change = resource_after.cost_per_hour - resource_before.cost_per_hour
        performance_change = (
            (resource_before.response_time - resource_after.response_time) / resource_before.response_time
            if resource_before.response_time > 0 else 0
        )
        
        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            resource_before,
            resource_after,
            cost_change,
            performance_change
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            resource_after,
            optimization_score,
            action_taken
        )
        
        feedback = OptimizationFeedback(
            timestamp=time.time(),
            action_taken=action_taken,
            resource_before=resource_before,
            resource_after=resource_after,
            cost_change=cost_change,
            performance_change=performance_change,
            optimization_score=optimization_score,
            recommendation=recommendation
        )
        
        self.feedback_history.append(feedback)
        
        logger.info(
            f"Optimization feedback - Action: {action_taken}, "
            f"Cost Change: ${cost_change:.2f}/hr, "
            f"Performance Change: {performance_change:.2%}, "
            f"Score: {optimization_score:.2f}"
        )
        
        return feedback
    
    def _calculate_optimization_score(
        self,
        resource_before: ResourceMetrics,
        resource_after: ResourceMetrics,
        cost_change: float,
        performance_change: float
    ) -> float:
        """Calculate optimization score (higher is better)"""
        
        # Cost component (negative cost change is good)
        cost_score = -cost_change * 10
        
        # Performance component (positive performance change is good)
        perf_score = performance_change * 100
        
        # Resource utilization component
        util_score = self._calculate_utilization_score(resource_after)
        
        # Error rate component (lower is better)
        error_score = -(resource_after.error_rate - resource_before.error_rate) * 1000
        
        # Weighted combination
        score = (
            cost_score * 0.4 +
            perf_score * 0.3 +
            util_score * 0.2 +
            error_score * 0.1
        )
        
        return score
    
    def _calculate_utilization_score(self, metrics: ResourceMetrics) -> float:
        """Calculate score based on resource utilization"""
        cpu_optimal = self.thresholds["optimal_cpu"][0] <= metrics.cpu_usage <= self.thresholds["optimal_cpu"][1]
        memory_optimal = self.thresholds["optimal_memory"][0] <= metrics.memory_usage <= self.thresholds["optimal_memory"][1]
        
        score = 0.0
        
        # CPU utilization score
        if cpu_optimal:
            score += 50
        elif metrics.cpu_usage < self.thresholds["optimal_cpu"][0]:
            # Under-utilized (idle penalty)
            score -= (self.thresholds["optimal_cpu"][0] - metrics.cpu_usage) * 100
        else:
            # Over-utilized
            score -= (metrics.cpu_usage - self.thresholds["optimal_cpu"][1]) * 100
        
        # Memory utilization score
        if memory_optimal:
            score += 50
        elif metrics.memory_usage < self.thresholds["optimal_memory"][0]:
            score -= (self.thresholds["optimal_memory"][0] - metrics.memory_usage) * 100
        else:
            score -= (metrics.memory_usage - self.thresholds["optimal_memory"][1]) * 100
        
        return score
    
    def _generate_recommendation(
        self,
        metrics: ResourceMetrics,
        optimization_score: float,
        action_taken: str
    ) -> str:
        """Generate optimization recommendation"""
        
        recommendations = []
        
        # CPU recommendations
        if metrics.cpu_usage < self.thresholds["optimal_cpu"][0]:
            recommendations.append(f"CPU under-utilized ({metrics.cpu_usage:.2%}), consider scaling down")
        elif metrics.cpu_usage > self.thresholds["optimal_cpu"][1]:
            recommendations.append(f"CPU over-utilized ({metrics.cpu_usage:.2%}), consider scaling up")
        
        # Memory recommendations
        if metrics.memory_usage < self.thresholds["optimal_memory"][0]:
            recommendations.append(f"Memory under-utilized ({metrics.memory_usage:.2%}), consider reducing allocation")
        elif metrics.memory_usage > self.thresholds["optimal_memory"][1]:
            recommendations.append(f"Memory over-utilized ({metrics.memory_usage:.2%}), consider increasing allocation")
        
        # Response time recommendations
        if metrics.response_time > self.thresholds["max_response_time"]:
            recommendations.append(f"Response time high ({metrics.response_time:.2f}s), optimize performance")
        
        # Error rate recommendations
        if metrics.error_rate > self.thresholds["max_error_rate"]:
            recommendations.append(f"Error rate high ({metrics.error_rate:.2%}), investigate issues")
        
        # Cost recommendations
        if metrics.cost_per_hour > 0:
            avg_cost = self._get_average_cost()
            if metrics.cost_per_hour > avg_cost * 1.2:
                recommendations.append(f"Cost above average (${metrics.cost_per_hour:.2f}/hr), optimize resource usage")
        
        if not recommendations:
            recommendations.append("Resources optimally configured")
        
        return "; ".join(recommendations)
    
    def _get_average_cost(self) -> float:
        """Get average cost from recent metrics"""
        if not self.metrics_history:
            return 0.0
        
        recent_metrics = list(self.metrics_history)[-100:]
        return np.mean([m.cost_per_hour for m in recent_metrics])
    
    def optimize_cost_function(self):
        """Optimize cost function weights based on feedback"""
        if len(self.feedback_history) < 100:
            logger.warning("Insufficient feedback data for cost function optimization")
            return
        
        logger.info("Optimizing cost function weights...")
        
        # Analyze feedback to adjust weights
        positive_feedback = [f for f in self.feedback_history if f.optimization_score > 0]
        negative_feedback = [f for f in self.feedback_history if f.optimization_score < 0]
        
        if not positive_feedback:
            return
        
        # Analyze successful optimizations
        avg_positive_score = np.mean([f.optimization_score for f in positive_feedback])
        avg_negative_score = np.mean([f.optimization_score for f in negative_feedback]) if negative_feedback else 0
        
        # Adjust weights based on what worked
        # This is simplified - in practice, use gradient descent or evolutionary algorithms
        if avg_positive_score > abs(avg_negative_score):
            # Successful optimizations, maintain or slightly adjust weights
            logger.info(f"Cost function performing well (avg score: {avg_positive_score:.2f})")
        else:
            # Need to adjust weights
            logger.info("Adjusting cost function weights based on feedback")
            # Adjust weights (simplified - use actual optimization in production)
            self.cost_weights["response_time_weight"] *= 1.1
            self.cost_weights["error_rate_weight"] *= 1.1
    
    def get_optimization_summary(self) -> Dict:
        """Get summary of optimization performance"""
        if not self.feedback_history:
            return {"status": "no_data"}
        
        recent_feedback = list(self.feedback_history)[-100:]
        
        avg_score = np.mean([f.optimization_score for f in recent_feedback])
        avg_cost_change = np.mean([f.cost_change for f in recent_feedback])
        avg_perf_change = np.mean([f.performance_change for f in recent_feedback])
        
        positive_count = sum(1 for f in recent_feedback if f.optimization_score > 0)
        success_rate = positive_count / len(recent_feedback) if recent_feedback else 0
        
        return {
            "average_score": avg_score,
            "average_cost_change": avg_cost_change,
            "average_performance_change": avg_perf_change,
            "success_rate": success_rate,
            "total_optimizations": len(self.feedback_history),
            "recent_optimizations": len(recent_feedback)
        }
    
    def save_feedback(self):
        """Save feedback history to disk"""
        if not self.feedback_history:
            return
        
        timestamp = int(time.time())
        file_path = self.storage_path / f"optimization_feedback_{timestamp}.json"
        
        feedback_data = {
            "feedback": [asdict(f) for f in list(self.feedback_history)[-1000:]]
        }
        
        with open(file_path, 'w') as f:
            json.dump(feedback_data, f, indent=2, default=str)
        
        logger.info(f"Saved {len(feedback_data['feedback'])} feedback records to {file_path}")

