"""
Time-Series Forecasting for Performance Prediction
Uses time-series models to predict and optimize future performance
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class Forecast:
    """Performance forecast"""
    metric_name: str
    agent_name: str
    timestamp: float
    forecast_horizon: float  # seconds into future
    predicted_value: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence: float
    trend: str  # "increasing", "decreasing", "stable"
    recommendation: str


class TimeSeriesForecaster:
    """Forecasts future performance using time-series models"""
    
    def __init__(self, lookback_window: int = 100):
        self.lookback_window = lookback_window
        
        # Historical data storage
        self.metric_history: Dict[str, Dict[str, List[Tuple[float, float]]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
        # Forecasts storage
        self.forecasts: Dict[str, List[Forecast]] = defaultdict(list)
    
    def add_data_point(
        self,
        agent_name: str,
        metric_name: str,
        value: float,
        timestamp: Optional[float] = None
    ):
        """Add a data point for forecasting"""
        if timestamp is None:
            timestamp = time.time()
        
        history = self.metric_history[agent_name][metric_name]
        history.append((timestamp, value))
        
        # Keep only recent data
        if len(history) > self.lookback_window:
            history.pop(0)
    
    def forecast_simple_moving_average(
        self,
        agent_name: str,
        metric_name: str,
        horizon_seconds: int = 3600,
        window_size: int = 10
    ) -> Optional[Forecast]:
        """Forecast using simple moving average"""
        history = self.metric_history[agent_name][metric_name]
        
        if len(history) < window_size:
            logger.warning(f"Insufficient data for forecasting {metric_name} for {agent_name}")
            return None
        
        # Get recent values
        recent_values = [v for _, v in history[-window_size:]]
        
        # Calculate moving average
        moving_avg = np.mean(recent_values)
        
        # Calculate trend
        if len(recent_values) >= 2:
            trend_value = recent_values[-1] - recent_values[0]
            if trend_value > 0.1:
                trend = "increasing"
            elif trend_value < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Calculate confidence interval (simplified)
        std = np.std(recent_values)
        confidence_interval_lower = moving_avg - 1.96 * std
        confidence_interval_upper = moving_avg + 1.96 * std
        confidence = max(0.0, 1.0 - std / (moving_avg + 1e-6))
        
        # Generate recommendation
        recommendation = self._generate_recommendation(metric_name, moving_avg, trend)
        
        forecast = Forecast(
            metric_name=metric_name,
            agent_name=agent_name,
            timestamp=time.time(),
            forecast_horizon=horizon_seconds,
            predicted_value=moving_avg,
            confidence_interval_lower=confidence_interval_lower,
            confidence_interval_upper=confidence_interval_upper,
            confidence=confidence,
            trend=trend,
            recommendation=recommendation
        )
        
        self.forecasts[agent_name].append(forecast)
        
        logger.debug(
            f"Forecast for {agent_name}/{metric_name}: {moving_avg:.2f} "
            f"(confidence: {confidence:.2%}, trend: {trend})"
        )
        
        return forecast
    
    def forecast_exponential_smoothing(
        self,
        agent_name: str,
        metric_name: str,
        horizon_seconds: int = 3600,
        alpha: float = 0.3
    ) -> Optional[Forecast]:
        """Forecast using exponential smoothing"""
        history = self.metric_history[agent_name][metric_name]
        
        if len(history) < 2:
            logger.warning(f"Insufficient data for exponential smoothing forecast")
            return None
        
        # Exponential smoothing
        values = [v for _, v in history]
        smoothed = [values[0]]
        
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])
        
        predicted_value = smoothed[-1]
        
        # Calculate trend
        if len(smoothed) >= 2:
            trend_value = smoothed[-1] - smoothed[-2]
            if trend_value > 0.1:
                trend = "increasing"
            elif trend_value < -0.1:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Confidence interval
        std = np.std(values)
        confidence_interval_lower = predicted_value - 1.96 * std
        confidence_interval_upper = predicted_value + 1.96 * std
        confidence = max(0.0, 1.0 - std / (predicted_value + 1e-6))
        
        recommendation = self._generate_recommendation(metric_name, predicted_value, trend)
        
        forecast = Forecast(
            metric_name=metric_name,
            agent_name=agent_name,
            timestamp=time.time(),
            forecast_horizon=horizon_seconds,
            predicted_value=predicted_value,
            confidence_interval_lower=confidence_interval_lower,
            confidence_interval_upper=confidence_interval_upper,
            confidence=confidence,
            trend=trend,
            recommendation=recommendation
        )
        
        self.forecasts[agent_name].append(forecast)
        
        return forecast
    
    def forecast_linear_trend(
        self,
        agent_name: str,
        metric_name: str,
        horizon_seconds: int = 3600
    ) -> Optional[Forecast]:
        """Forecast using linear trend"""
        history = self.metric_history[agent_name][metric_name]
        
        if len(history) < 3:
            logger.warning(f"Insufficient data for linear trend forecast")
            return None
        
        # Extract timestamps and values
        timestamps = np.array([t for t, _ in history])
        values = np.array([v for _, v in history])
        
        # Normalize timestamps
        timestamps = timestamps - timestamps[0]
        
        # Linear regression
        coeffs = np.polyfit(timestamps, values, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # Predict future value
        future_time = timestamps[-1] + horizon_seconds
        predicted_value = slope * future_time + intercept
        
        # Calculate trend
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # Confidence interval
        residuals = values - (slope * timestamps + intercept)
        std = np.std(residuals)
        confidence_interval_lower = predicted_value - 1.96 * std
        confidence_interval_upper = predicted_value + 1.96 * std
        confidence = max(0.0, 1.0 - std / (predicted_value + 1e-6))
        
        recommendation = self._generate_recommendation(metric_name, predicted_value, trend)
        
        forecast = Forecast(
            metric_name=metric_name,
            agent_name=agent_name,
            timestamp=time.time(),
            forecast_horizon=horizon_seconds,
            predicted_value=predicted_value,
            confidence_interval_lower=confidence_interval_lower,
            confidence_interval_upper=confidence_interval_upper,
            confidence=confidence,
            trend=trend,
            recommendation=recommendation
        )
        
        self.forecasts[agent_name].append(forecast)
        
        return forecast
    
    def _generate_recommendation(
        self,
        metric_name: str,
        predicted_value: float,
        trend: str
    ) -> str:
        """Generate recommendation based on forecast"""
        recommendations = []
        
        if metric_name == "cpu_usage":
            if predicted_value > 0.8:
                recommendations.append("CPU usage predicted to exceed 80%, consider scaling up")
            elif predicted_value < 0.3 and trend == "decreasing":
                recommendations.append("CPU usage predicted to be low, consider scaling down")
        
        elif metric_name == "memory_usage":
            if predicted_value > 0.8:
                recommendations.append("Memory usage predicted to exceed 80%, increase allocation")
            elif predicted_value < 0.3 and trend == "decreasing":
                recommendations.append("Memory usage predicted to be low, reduce allocation")
        
        elif metric_name == "error_rate":
            if predicted_value > 0.05:
                recommendations.append("Error rate predicted to be high, investigate issues")
        
        elif metric_name == "latency_p95":
            if predicted_value > 1.0:
                recommendations.append("Latency predicted to be high, optimize performance")
        
        elif metric_name == "success_rate":
            if predicted_value < 0.8:
                recommendations.append("Success rate predicted to be low, review agent logic")
        
        if not recommendations:
            recommendations.append("Performance predicted to be within acceptable range")
        
        return "; ".join(recommendations)
    
    def forecast_all_metrics(
        self,
        agent_name: str,
        horizon_seconds: int = 3600,
        method: str = "linear"
    ) -> List[Forecast]:
        """Forecast all metrics for an agent"""
        forecasts = []
        
        metric_names = list(self.metric_history[agent_name].keys())
        
        for metric_name in metric_names:
            if method == "linear":
                forecast = self.forecast_linear_trend(agent_name, metric_name, horizon_seconds)
            elif method == "smoothing":
                forecast = self.forecast_exponential_smoothing(agent_name, metric_name, horizon_seconds)
            else:
                forecast = self.forecast_simple_moving_average(agent_name, metric_name, horizon_seconds)
            
            if forecast:
                forecasts.append(forecast)
        
        return forecasts
    
    def get_recent_forecasts(self, agent_name: str, limit: int = 100) -> List[Forecast]:
        """Get recent forecasts for an agent"""
        return list(self.forecasts[agent_name])[-limit:]

