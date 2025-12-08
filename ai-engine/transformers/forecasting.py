"""
Forecasting Module
Predict CPU, Latency, Memory risk, Error burst 5 min ahead
Output used by Scaling Agent
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from .model import TimeSeriesForecaster, AnomalyTrendDetector, ResourceSaturationPredictor
from .dataset import SlidingWindowDataset, MetricsDataset

logger = logging.getLogger(__name__)


class ScalingForecastEngine:
    """
    Forecasting engine for Scaling Agent
    
    Predicts:
    - CPU 5 min ahead
    - Latency 5 min ahead
    - Memory risk
    - Error burst window
    """
    
    def __init__(
        self,
        forecaster: Optional[TimeSeriesForecaster] = None,
        anomaly_detector: Optional[AnomalyTrendDetector] = None,
        saturation_predictor: Optional[ResourceSaturationPredictor] = None,
        input_dim: int = 5,
        device: str = "cpu"
    ):
        self.device = torch.device(device)
        self.input_dim = input_dim
        
        # Initialize forecaster
        if forecaster is None:
            forecaster = TimeSeriesForecaster(
                input_dim=input_dim,
                output_dim=4,  # [cpu_forecast, latency_forecast, memory_risk, error_burst]
                d_model=128,
                nhead=8,
                num_encoder_layers=4,
                num_decoder_layers=4,
                seq_len=60,
                pred_len=5  # 5 minutes ahead
            )
        self.forecaster = forecaster.to(self.device)
        self.forecaster.eval()
        
        # Initialize anomaly detector
        if anomaly_detector is None:
            anomaly_detector = AnomalyTrendDetector(
                input_dim=input_dim,
                d_model=128,
                nhead=8,
                num_layers=4,
                seq_len=60
            )
        self.anomaly_detector = anomaly_detector.to(self.device)
        self.anomaly_detector.eval()
        
        # Initialize saturation predictor
        if saturation_predictor is None:
            saturation_predictor = ResourceSaturationPredictor(
                input_dim=input_dim,
                d_model=128,
                nhead=8,
                num_layers=4,
                seq_len=60,
                pred_len=5
            )
        self.saturation_predictor = saturation_predictor.to(self.device)
        self.saturation_predictor.eval()
        
        logger.info("ScalingForecastEngine initialized")
    
    def forecast_5min(
        self,
        historical_metrics: np.ndarray,
        seq_len: int = 60
    ) -> Dict[str, np.ndarray]:
        """
        Forecast metrics 5 minutes ahead
        
        Args:
            historical_metrics: Historical metrics [time_steps, features]
                Features: [cpu, memory, latency, error_rate, request_rate]
            seq_len: Input sequence length
        
        Returns:
            Dictionary with forecasts:
            - cpu_forecast: CPU usage 5 min ahead [5]
            - latency_forecast: Latency 5 min ahead [5]
            - memory_risk: Memory risk indicators [5]
            - error_burst: Error burst indicators [5]
        """
        # Prepare input
        if len(historical_metrics) < seq_len:
            # Pad if necessary
            padding = np.zeros((seq_len - len(historical_metrics), historical_metrics.shape[1]))
            historical_metrics = np.vstack([padding, historical_metrics])
        
        input_seq = historical_metrics[-seq_len:]
        input_tensor = torch.FloatTensor(input_seq).unsqueeze(1).to(self.device)  # [seq_len, 1, input_dim]
        
        # Forecast
        with torch.no_grad():
            forecast = self.forecaster.forecast(input_tensor)  # [5, 1, 4]
        
        # Extract forecasts
        forecast_np = forecast.squeeze(1).cpu().numpy()  # [5, 4]
        
        results = {
            'cpu_forecast': forecast_np[:, 0],  # CPU 5 min ahead
            'latency_forecast': forecast_np[:, 1],  # Latency 5 min ahead
            'memory_risk': forecast_np[:, 2],  # Memory risk [0, 1]
            'error_burst': forecast_np[:, 3]  # Error burst [0, 1]
        }
        
        logger.info(f"Forecasted 5 minutes ahead: CPU avg={np.mean(results['cpu_forecast']):.2f}, "
                   f"Latency avg={np.mean(results['latency_forecast']):.2f}")
        
        return results
    
    def detect_anomaly_trends(
        self,
        historical_metrics: np.ndarray,
        seq_len: int = 60
    ) -> Dict[str, Any]:
        """
        Detect anomaly trends
        
        Args:
            historical_metrics: Historical metrics [time_steps, features]
            seq_len: Input sequence length
        
        Returns:
            Dictionary with anomaly trend information
        """
        # Prepare input
        if len(historical_metrics) < seq_len:
            padding = np.zeros((seq_len - len(historical_metrics), historical_metrics.shape[1]))
            historical_metrics = np.vstack([padding, historical_metrics])
        
        input_seq = historical_metrics[-seq_len:]
        input_tensor = torch.FloatTensor(input_seq).unsqueeze(1).to(self.device)
        
        # Detect trends
        with torch.no_grad():
            trend_logits, severity = self.anomaly_detector(input_tensor)
            trend_probs = torch.softmax(trend_logits, dim=1)
        
        trend_labels = ['normal', 'increasing_anomaly', 'decreasing_anomaly']
        trend_idx = trend_probs.argmax(dim=1).item()
        
        results = {
            'trend': trend_labels[trend_idx],
            'trend_probability': trend_probs[0, trend_idx].item(),
            'severity': severity.item(),
            'all_probabilities': {
                label: prob.item() for label, prob in zip(trend_labels, trend_probs[0])
            }
        }
        
        logger.info(f"Anomaly trend detected: {results['trend']} (severity: {results['severity']:.2f})")
        
        return results
    
    def predict_resource_saturation(
        self,
        historical_metrics: np.ndarray,
        seq_len: int = 60
    ) -> Dict[str, np.ndarray]:
        """
        Predict resource saturation
        
        Args:
            historical_metrics: Historical metrics [time_steps, features]
            seq_len: Input sequence length
        
        Returns:
            Dictionary with saturation predictions:
            - cpu_saturation: CPU saturation [5] (0-1, where 1 = saturated)
            - memory_saturation: Memory saturation [5] (0-1)
        """
        # Prepare input
        if len(historical_metrics) < seq_len:
            padding = np.zeros((seq_len - len(historical_metrics), historical_metrics.shape[1]))
            historical_metrics = np.vstack([padding, historical_metrics])
        
        input_seq = historical_metrics[-seq_len:]
        input_tensor = torch.FloatTensor(input_seq).unsqueeze(1).to(self.device)
        
        # Predict saturation
        with torch.no_grad():
            saturation = self.saturation_predictor(input_tensor)  # [1, 5, 2]
        
        saturation_np = saturation.squeeze(0).cpu().numpy()  # [5, 2]
        
        results = {
            'cpu_saturation': saturation_np[:, 0],  # CPU saturation 5 min ahead
            'memory_saturation': saturation_np[:, 1]  # Memory saturation 5 min ahead
        }
        
        logger.info(f"Resource saturation predicted: CPU max={np.max(results['cpu_saturation']):.2f}, "
                   f"Memory max={np.max(results['memory_saturation']):.2f}")
        
        return results
    
    def get_scaling_recommendation(
        self,
        historical_metrics: np.ndarray,
        current_replicas: int = 2,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        latency_threshold: float = 500.0
    ) -> Dict[str, Any]:
        """
        Get scaling recommendation for Scaling Agent
        
        Args:
            historical_metrics: Historical metrics [time_steps, features]
            current_replicas: Current number of replicas
            cpu_threshold: CPU threshold for scaling
            memory_threshold: Memory threshold for scaling
            latency_threshold: Latency threshold for scaling
        
        Returns:
            Scaling recommendation dictionary
        """
        # Forecast 5 min ahead
        forecast = self.forecast_5min(historical_metrics)
        
        # Predict saturation
        saturation = self.predict_resource_saturation(historical_metrics)
        
        # Analyze forecasts
        avg_cpu = np.mean(forecast['cpu_forecast'])
        max_cpu = np.max(forecast['cpu_forecast'])
        avg_latency = np.mean(forecast['latency_forecast'])
        max_latency = np.max(forecast['latency_forecast'])
        memory_risk_any = np.any(forecast['memory_risk'] > 0.5)
        error_burst_any = np.any(forecast['error_burst'] > 0.5)
        
        # Determine scaling action
        scale_up = False
        scale_down = False
        urgency = "low"
        
        # Scale up conditions
        if (max_cpu > cpu_threshold or 
            max_latency > latency_threshold or 
            memory_risk_any or
            np.max(saturation['cpu_saturation']) > 0.8 or
            np.max(saturation['memory_saturation']) > 0.8):
            scale_up = True
            if max_cpu > 90 or max_latency > 1000 or error_burst_any:
                urgency = "high"
            else:
                urgency = "medium"
        
        # Scale down conditions
        elif (avg_cpu < 30 and 
              avg_latency < latency_threshold * 0.5 and
              not memory_risk_any and
              current_replicas > 1):
            scale_down = True
            urgency = "low"
        
        # Calculate target replicas
        if scale_up:
            # Aggressive scaling if urgent
            if urgency == "high":
                target_replicas = min(current_replicas + 3, 20)
            else:
                target_replicas = min(current_replicas + 2, 20)
        elif scale_down:
            target_replicas = max(current_replicas - 1, 1)
        else:
            target_replicas = current_replicas
        
        # Generate reasoning
        reasoning_parts = []
        if scale_up:
            if max_cpu > cpu_threshold:
                reasoning_parts.append(f"CPU forecasted to reach {max_cpu:.1f}% (threshold: {cpu_threshold}%)")
            if max_latency > latency_threshold:
                reasoning_parts.append(f"Latency forecasted to reach {max_latency:.1f}ms (threshold: {latency_threshold}ms)")
            if memory_risk_any:
                reasoning_parts.append("Memory risk detected in forecast")
            if error_burst_any:
                reasoning_parts.append("Error burst window detected")
        elif scale_down:
            reasoning_parts.append(f"Low resource usage forecasted (CPU: {avg_cpu:.1f}%, Latency: {avg_latency:.1f}ms)")
        
        recommendation = {
            'action': 'scale_up' if scale_up else ('scale_down' if scale_down else 'no_action'),
            'target_replicas': target_replicas,
            'current_replicas': current_replicas,
            'urgency': urgency,
            'confidence': self._calculate_confidence(forecast, saturation),
            'reasoning': " | ".join(reasoning_parts) if reasoning_parts else "No scaling needed",
            'forecast': {
                'cpu_5min': forecast['cpu_forecast'].tolist(),
                'latency_5min': forecast['latency_forecast'].tolist(),
                'memory_risk': forecast['memory_risk'].tolist(),
                'error_burst': forecast['error_burst'].tolist()
            },
            'saturation': {
                'cpu_saturation': saturation['cpu_saturation'].tolist(),
                'memory_saturation': saturation['memory_saturation'].tolist()
            }
        }
        
        logger.info(f"Scaling recommendation: {recommendation['action']} to {target_replicas} replicas (urgency: {urgency})")
        
        return recommendation
    
    def _calculate_confidence(
        self,
        forecast: Dict[str, np.ndarray],
        saturation: Dict[str, np.ndarray]
    ) -> float:
        """
        Calculate confidence in forecast
        
        Args:
            forecast: Forecast dictionary
            saturation: Saturation dictionary
        
        Returns:
            Confidence score [0, 1]
        """
        # Higher confidence if forecasts are consistent
        cpu_std = np.std(forecast['cpu_forecast'])
        latency_std = np.std(forecast['latency_forecast'])
        
        # Lower std = higher confidence
        confidence = 1.0 - min(1.0, (cpu_std + latency_std) / 2.0)
        
        return float(confidence)
    
    def load_models(self, checkpoint_dir: str):
        """Load trained models"""
        from pathlib import Path
        
        checkpoint_path = Path(checkpoint_dir)
        
        forecaster_path = checkpoint_path / "forecaster.pth"
        if forecaster_path.exists():
            self.forecaster.load_state_dict(torch.load(forecaster_path, map_location=self.device))
            logger.info(f"Loaded forecaster from {forecaster_path}")
        
        anomaly_path = checkpoint_path / "anomaly_detector.pth"
        if anomaly_path.exists():
            self.anomaly_detector.load_state_dict(torch.load(anomaly_path, map_location=self.device))
            logger.info(f"Loaded anomaly detector from {anomaly_path}")
        
        saturation_path = checkpoint_path / "saturation_predictor.pth"
        if saturation_path.exists():
            self.saturation_predictor.load_state_dict(torch.load(saturation_path, map_location=self.device))
            logger.info(f"Loaded saturation predictor from {saturation_path}")
    
    def save_models(self, checkpoint_dir: str):
        """Save trained models"""
        from pathlib import Path
        
        checkpoint_path = Path(checkpoint_dir)
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        torch.save(self.forecaster.state_dict(), checkpoint_path / "forecaster.pth")
        torch.save(self.anomaly_detector.state_dict(), checkpoint_path / "anomaly_detector.pth")
        torch.save(self.saturation_predictor.state_dict(), checkpoint_path / "saturation_predictor.pth")
        
        logger.info(f"Models saved to {checkpoint_dir}")
