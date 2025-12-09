"""
Auto-Scaling Optimization
Optimizes scaling decisions based on load predictions
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class LoadPrediction:
    """Load prediction for future time window"""
    timestamp: float
    predicted_cpu: float
    predicted_memory: float
    predicted_requests: float
    confidence: float
    time_horizon: float  # seconds into future


@dataclass
class ScalingDecision:
    """Scaling decision with reasoning"""
    timestamp: float
    action: str  # "scale_up", "scale_down", "maintain"
    current_cpu: float
    current_memory: float
    predicted_cpu: float
    predicted_memory: float
    target_replicas: int
    reasoning: str
    confidence: float


class AutoScalingOptimizer:
    """Optimizes auto-scaling decisions based on load predictions"""
    
    def __init__(self, prediction_horizon: int = 300):
        self.prediction_horizon = prediction_horizon  # 5 minutes
        
        # Historical load data
        self.load_history: deque = deque(maxlen=1000)
        
        # Scaling decisions history
        self.decision_history: deque = deque(maxlen=1000)
        
        # Prediction model (simplified - use ML in production)
        self.prediction_window = 60  # Use last 60 data points
        
        # Scaling thresholds (learned over time)
        self.scaling_thresholds = {
            "scale_up_cpu": 0.75,
            "scale_up_memory": 0.75,
            "scale_down_cpu": 0.30,
            "scale_down_memory": 0.30,
            "scale_up_requests": 1000,  # requests per second
            "scale_down_requests": 200
        }
        
        # Scaling parameters
        self.scaling_config = {
            "min_replicas": 2,
            "max_replicas": 20,
            "scale_up_step": 2,
            "scale_down_step": 1,
            "cooldown_period": 300  # seconds
        }
        
        # Storage
        self.storage_path = Path("data/optimization/autoscaling")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def record_load(
        self,
        cpu_usage: float,
        memory_usage: float,
        request_rate: float,
        current_replicas: int
    ):
        """Record current load metrics"""
        load_data = {
            "timestamp": time.time(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "request_rate": request_rate,
            "current_replicas": current_replicas
        }
        
        self.load_history.append(load_data)
        logger.debug(f"Recorded load: CPU={cpu_usage:.2%}, Memory={memory_usage:.2%}, Requests={request_rate:.1f}/s")
    
    def predict_load(self) -> LoadPrediction:
        """Predict future load using historical data"""
        if len(self.load_history) < self.prediction_window:
            logger.warning("Insufficient data for load prediction")
            # Return current load as prediction
            if self.load_history:
                latest = self.load_history[-1]
                return LoadPrediction(
                    timestamp=time.time(),
                    predicted_cpu=latest["cpu_usage"],
                    predicted_memory=latest["memory_usage"],
                    predicted_requests=latest["request_rate"],
                    confidence=0.5,
                    time_horizon=self.prediction_horizon
                )
            else:
                return LoadPrediction(
                    timestamp=time.time(),
                    predicted_cpu=0.5,
                    predicted_memory=0.5,
                    predicted_requests=500,
                    confidence=0.0,
                    time_horizon=self.prediction_horizon
                )
        
        # Get recent load data
        recent_loads = list(self.load_history)[-self.prediction_window:]
        
        # Simple prediction: trend-based (in production, use LSTM, ARIMA, etc.)
        cpu_values = [l["cpu_usage"] for l in recent_loads]
        memory_values = [l["memory_usage"] for l in recent_loads]
        request_values = [l["request_rate"] for l in recent_loads]
        
        # Calculate trend
        cpu_trend = np.polyfit(range(len(cpu_values)), cpu_values, 1)[0]
        memory_trend = np.polyfit(range(len(memory_values)), memory_values, 1)[0]
        request_trend = np.polyfit(range(len(request_values)), request_values, 1)[0]
        
        # Predict future values
        latest = recent_loads[-1]
        time_steps = self.prediction_horizon / 60  # Convert to minutes (assuming 1-minute intervals)
        
        predicted_cpu = latest["cpu_usage"] + cpu_trend * time_steps
        predicted_memory = latest["memory_usage"] + memory_trend * time_steps
        predicted_requests = latest["request_rate"] + request_trend * time_steps
        
        # Clamp predictions
        predicted_cpu = np.clip(predicted_cpu, 0.0, 1.0)
        predicted_memory = np.clip(predicted_memory, 0.0, 1.0)
        predicted_requests = max(0.0, predicted_requests)
        
        # Calculate confidence based on data stability
        cpu_std = np.std(cpu_values)
        confidence = max(0.0, 1.0 - cpu_std * 2)  # Lower std = higher confidence
        
        prediction = LoadPrediction(
            timestamp=time.time(),
            predicted_cpu=predicted_cpu,
            predicted_memory=predicted_memory,
            predicted_requests=predicted_requests,
            confidence=confidence,
            time_horizon=self.prediction_horizon
        )
        
        logger.debug(
            f"Load prediction - CPU: {predicted_cpu:.2%}, Memory: {predicted_memory:.2%}, "
            f"Requests: {predicted_requests:.1f}/s, Confidence: {confidence:.2%}"
        )
        
        return prediction
    
    def optimize_scaling_decision(
        self,
        current_cpu: float,
        current_memory: float,
        current_requests: float,
        current_replicas: int
    ) -> ScalingDecision:
        """Optimize scaling decision based on current and predicted load"""
        
        # Get load prediction
        prediction = self.predict_load()
        
        # Determine scaling action
        action = "maintain"
        target_replicas = current_replicas
        reasoning_parts = []
        
        # Check if scaling up is needed
        scale_up_needed = (
            prediction.predicted_cpu > self.scaling_thresholds["scale_up_cpu"] or
            prediction.predicted_memory > self.scaling_thresholds["scale_up_memory"] or
            prediction.predicted_requests > self.scaling_thresholds["scale_up_requests"]
        )
        
        # Check if scaling down is safe
        scale_down_safe = (
            prediction.predicted_cpu < self.scaling_thresholds["scale_down_cpu"] and
            prediction.predicted_memory < self.scaling_thresholds["scale_down_memory"] and
            prediction.predicted_requests < self.scaling_thresholds["scale_down_requests"] and
            current_replicas > self.scaling_config["min_replicas"]
        )
        
        if scale_up_needed and current_replicas < self.scaling_config["max_replicas"]:
            action = "scale_up"
            target_replicas = min(
                current_replicas + self.scaling_config["scale_up_step"],
                self.scaling_config["max_replicas"]
            )
            reasoning_parts.append(
                f"Predicted CPU: {prediction.predicted_cpu:.2%} > {self.scaling_thresholds['scale_up_cpu']:.2%}"
            )
            reasoning_parts.append(
                f"Predicted Memory: {prediction.predicted_memory:.2%} > {self.scaling_thresholds['scale_up_memory']:.2%}"
            )
            reasoning_parts.append(
                f"Predicted Requests: {prediction.predicted_requests:.1f}/s > {self.scaling_thresholds['scale_up_requests']}"
            )
        elif scale_down_safe:
            action = "scale_down"
            target_replicas = max(
                current_replicas - self.scaling_config["scale_down_step"],
                self.scaling_config["min_replicas"]
            )
            reasoning_parts.append(
                f"Predicted CPU: {prediction.predicted_cpu:.2%} < {self.scaling_thresholds['scale_down_cpu']:.2%}"
            )
            reasoning_parts.append(
                f"Predicted Memory: {prediction.predicted_memory:.2%} < {self.scaling_thresholds['scale_down_memory']:.2%}"
            )
            reasoning_parts.append("Safe to scale down")
        else:
            reasoning_parts.append("Load within optimal range")
            reasoning_parts.append(f"Current replicas: {current_replicas} (optimal)")
        
        reasoning = "; ".join(reasoning_parts)
        
        decision = ScalingDecision(
            timestamp=time.time(),
            action=action,
            current_cpu=current_cpu,
            current_memory=current_memory,
            predicted_cpu=prediction.predicted_cpu,
            predicted_memory=prediction.predicted_memory,
            target_replicas=target_replicas,
            reasoning=reasoning,
            confidence=prediction.confidence
        )
        
        self.decision_history.append(decision)
        
        logger.info(
            f"Scaling decision - Action: {action}, "
            f"Current: {current_replicas} replicas, "
            f"Target: {target_replicas} replicas, "
            f"Confidence: {prediction.confidence:.2%}"
        )
        
        return decision
    
    def update_thresholds_from_feedback(self, feedback: List[Dict]):
        """Update scaling thresholds based on feedback"""
        if not feedback:
            return
        
        logger.info("Updating scaling thresholds from feedback...")
        
        # Analyze successful scaling decisions
        successful_scale_ups = [
            f for f in feedback
            if f.get("action") == "scale_up" and f.get("outcome") == "success"
        ]
        successful_scale_downs = [
            f for f in feedback
            if f.get("action") == "scale_down" and f.get("outcome") == "success"
        ]
        
        # Adjust thresholds based on successful decisions
        if successful_scale_ups:
            avg_cpu = np.mean([f.get("cpu_usage", 0.75) for f in successful_scale_ups])
            self.scaling_thresholds["scale_up_cpu"] = avg_cpu * 0.95  # Slightly lower for earlier scaling
        
        if successful_scale_downs:
            avg_cpu = np.mean([f.get("cpu_usage", 0.30) for f in successful_scale_downs])
            self.scaling_thresholds["scale_down_cpu"] = avg_cpu * 1.05  # Slightly higher for safer scaling
        
        logger.info(f"Updated thresholds: {self.scaling_thresholds}")
    
    def get_scaling_summary(self) -> Dict:
        """Get summary of scaling decisions"""
        if not self.decision_history:
            return {"status": "no_data"}
        
        recent_decisions = list(self.decision_history)[-100:]
        
        scale_up_count = sum(1 for d in recent_decisions if d.action == "scale_up")
        scale_down_count = sum(1 for d in recent_decisions if d.action == "scale_down")
        maintain_count = sum(1 for d in recent_decisions if d.action == "maintain")
        
        avg_confidence = np.mean([d.confidence for d in recent_decisions])
        
        return {
            "total_decisions": len(self.decision_history),
            "recent_decisions": len(recent_decisions),
            "scale_up_count": scale_up_count,
            "scale_down_count": scale_down_count,
            "maintain_count": maintain_count,
            "average_confidence": avg_confidence,
            "current_thresholds": self.scaling_thresholds
        }
    
    def save_decisions(self):
        """Save scaling decisions to disk"""
        if not self.decision_history:
            return
        
        timestamp = int(time.time())
        file_path = self.storage_path / f"scaling_decisions_{timestamp}.json"
        
        decisions_data = {
            "decisions": [
                {
                    "timestamp": d.timestamp,
                    "action": d.action,
                    "current_cpu": d.current_cpu,
                    "current_memory": d.current_memory,
                    "predicted_cpu": d.predicted_cpu,
                    "predicted_memory": d.predicted_memory,
                    "target_replicas": d.target_replicas,
                    "reasoning": d.reasoning,
                    "confidence": d.confidence
                }
                for d in list(self.decision_history)[-1000:]
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(decisions_data, f, indent=2)
        
        logger.info(f"Saved {len(decisions_data['decisions'])} scaling decisions to {file_path}")

