"""
AI Engine Integration for Scaling Agent
Uses Transformer predictions
"""

import sys
import os
import numpy as np
from typing import Dict, List, Optional, Any
import logging

# Add AI engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_engine.transformers.forecasting import ScalingForecastEngine

logger = logging.getLogger(__name__)


class ScalingAIIntegration:
    """
    AI Engine Integration for Scaling Agent
    
    Uses:
    - Transformer forecasting for workload prediction
    """
    
    def __init__(self, forecast_checkpoint: Optional[str] = None):
        """
        Initialize AI integration
        
        Args:
            forecast_checkpoint: Path to trained forecast model checkpoint
        """
        # Initialize Forecasting Engine
        self.forecast_engine = ScalingForecastEngine()
        if forecast_checkpoint and os.path.exists(forecast_checkpoint):
            self.forecast_engine.load_models(forecast_checkpoint)
        
        logger.info("Scaling AI Integration initialized")
    
    def get_scaling_recommendation(
        self,
        historical_metrics: Dict[str, np.ndarray],
        current_replicas: int = 2,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        latency_threshold: float = 500.0
    ) -> Dict[str, Any]:
        """
        Get scaling recommendation using Transformer forecasts
        
        Args:
            historical_metrics: Historical metrics dictionary
                Keys: 'cpu', 'memory', 'latency', 'error_rate', 'request_rate'
                Values: numpy arrays of time series data
            current_replicas: Current number of replicas
            cpu_threshold: CPU threshold for scaling
            memory_threshold: Memory threshold for scaling
            latency_threshold: Latency threshold for scaling
        
        Returns:
            Scaling recommendation
        """
        try:
            # Convert metrics to array format
            metrics_array = self._prepare_metrics_array(historical_metrics)
            
            # Get scaling recommendation from forecast engine
            recommendation = self.forecast_engine.get_scaling_recommendation(
                historical_metrics=metrics_array,
                current_replicas=current_replicas,
                cpu_threshold=cpu_threshold,
                memory_threshold=memory_threshold,
                latency_threshold=latency_threshold
            )
            
            logger.info(f"Scaling recommendation: {recommendation.get('action')} to {recommendation.get('target_replicas')} replicas")
            
            return recommendation
        
        except Exception as e:
            logger.error(f"Scaling recommendation failed: {e}")
            return {
                "action": "no_action",
                "target_replicas": current_replicas,
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }
    
    def forecast_workload(
        self,
        historical_metrics: Dict[str, np.ndarray],
        forecast_horizon: int = 5
    ) -> Dict[str, np.ndarray]:
        """
        Forecast workload 5 minutes ahead
        
        Args:
            historical_metrics: Historical metrics
            forecast_horizon: Forecast horizon in minutes
        
        Returns:
            Forecast dictionary
        """
        try:
            metrics_array = self._prepare_metrics_array(historical_metrics)
            forecast = self.forecast_engine.forecast_5min(metrics_array)
            
            return forecast
        
        except Exception as e:
            logger.error(f"Workload forecasting failed: {e}")
            return {}
    
    def _prepare_metrics_array(self, metrics: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Prepare metrics array from dictionary
        
        Args:
            metrics: Dictionary of metric_name -> time_series
        
        Returns:
            Array [time_steps, features]
        """
        feature_names = ['cpu', 'memory', 'latency', 'error_rate', 'request_rate']
        data_list = []
        
        for name in feature_names:
            if name in metrics:
                data_list.append(metrics[name])
            else:
                # Fill with zeros if missing
                max_len = max(len(v) for v in metrics.values()) if metrics else 0
                data_list.append(np.zeros(max_len))
        
        # Stack into array
        return np.column_stack(data_list)

