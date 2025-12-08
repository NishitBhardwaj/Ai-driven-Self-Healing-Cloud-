"""
AI Engine Integration for Performance Monitoring Agent
Feeds data to all models
"""

import sys
import os
import numpy as np
from typing import Dict, List, Optional, Any
import logging

# Add AI engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_engine.rl.agent import RLAgent
from ai_engine.gnn.gnn_predictor import GNNPredictor
from ai_engine.gnn.graph_builder import GraphBuilder
from ai_engine.transformers.forecasting import ScalingForecastEngine
from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine

logger = logging.getLogger(__name__)


class MonitoringAIIntegration:
    """
    AI Engine Integration for Performance Monitoring Agent
    
    Feeds data to all models:
    - RL Agent
    - GNN Predictor
    - Transformers (Forecasting)
    - LLM Reasoning
    """
    
    def __init__(
        self,
        rl_checkpoint: Optional[str] = None,
        gnn_checkpoint: Optional[str] = None,
        forecast_checkpoint: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize AI integration
        
        Args:
            rl_checkpoint: Path to RL checkpoint
            gnn_checkpoint: Path to GNN checkpoint
            forecast_checkpoint: Path to forecast checkpoint
            openrouter_api_key: OpenRouter API key
            gemini_api_key: Gemini API key
        """
        # Initialize RL Agent
        self.rl_agent = RLAgent(state_dim=6, action_dim=7)
        if rl_checkpoint and os.path.exists(rl_checkpoint):
            self.rl_agent.load_checkpoint(rl_checkpoint)
        
        # Initialize GNN Predictor
        self.gnn_predictor = GNNPredictor()
        if gnn_checkpoint and os.path.exists(gnn_checkpoint):
            self.gnn_predictor.load_models(gnn_checkpoint)
        
        # Initialize Forecasting Engine
        self.forecast_engine = ScalingForecastEngine()
        if forecast_checkpoint and os.path.exists(forecast_checkpoint):
            self.forecast_engine.load_models(forecast_checkpoint)
        
        # Initialize LLM Reasoning Engine
        self.reasoning_engine = ReasoningEngine(
            openrouter_api_key=openrouter_api_key,
            gemini_api_key=gemini_api_key,
            use_openrouter=True,
            use_gemini=True
        )
        
        logger.info("Monitoring AI Integration initialized")
    
    def feed_metrics_to_models(
        self,
        metrics: Dict[str, Any],
        dependency_graph_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Feed metrics data to all AI models
        
        Args:
            metrics: Metrics data from Prometheus
            dependency_graph_data: Dependency graph data
        
        Returns:
            Analysis results from all models
        """
        results = {}
        
        # Prepare metrics array
        metrics_array = self._prepare_metrics_array(metrics)
        
        # Feed to Transformers (Forecasting)
        try:
            forecast = self.forecast_engine.forecast_5min(metrics_array)
            results["forecast"] = forecast
            
            # Detect anomaly trends
            anomaly_trends = self.forecast_engine.detect_anomaly_trends(metrics_array)
            results["anomaly_trends"] = anomaly_trends
            
            # Predict resource saturation
            saturation = self.forecast_engine.predict_resource_saturation(metrics_array)
            results["saturation"] = saturation
        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")
            results["forecast"] = None
        
        # Feed to RL Agent
        try:
            system_state = {
                "cpu_usage": float(np.mean(metrics.get("cpu", [0]))) if metrics.get("cpu") is not None else 0.0,
                "memory_usage": float(np.mean(metrics.get("memory", [0]))) if metrics.get("memory") is not None else 0.0,
                "error_rate": float(np.mean(metrics.get("error_rate", [0]))) if metrics.get("error_rate") is not None else 0.0,
                "network_latency": float(np.mean(metrics.get("latency", [0]))) if metrics.get("latency") is not None else 0.0,
                "replicas": metrics.get("replicas", 2),
                "dependency_health": 1.0
            }
            
            state_array = self._state_to_array(system_state)
            action, confidence = self.rl_agent.choose_action(state_array, training=False)
            
            results["rl_analysis"] = {
                "recommended_action": action,
                "confidence": float(confidence),
                "system_state": system_state
            }
        except Exception as e:
            logger.error(f"RL analysis failed: {e}")
            results["rl_analysis"] = None
        
        # Feed to GNN (if dependency graph available)
        if dependency_graph_data:
            try:
                dependency_graph = GraphBuilder.build_combined(
                    kubernetes_resources=dependency_graph_data.get("kubernetes", {}),
                    localstack_resources=dependency_graph_data.get("localstack", {})
                )
                
                # Analyze dependencies
                critical_nodes = self.gnn_predictor.get_critical_nodes(dependency_graph, threshold=0.7)
                
                results["gnn_analysis"] = {
                    "critical_nodes": critical_nodes,
                    "dependency_health": self._assess_dependency_health(dependency_graph, metrics)
                }
            except Exception as e:
                logger.error(f"GNN analysis failed: {e}")
                results["gnn_analysis"] = None
        
        # Feed to LLM (for anomaly explanation)
        try:
            if results.get("anomaly_trends", {}).get("trend") != "normal":
                anomaly_info = {
                    "type": "anomaly",
                    "trend": results["anomaly_trends"].get("trend"),
                    "severity": results["anomaly_trends"].get("severity", 0.5)
                }
                
                llm_analysis = self.reasoning_engine.classify_error(
                    error_info=anomaly_info,
                    system_state=system_state
                )
                
                results["llm_analysis"] = llm_analysis
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            results["llm_analysis"] = None
        
        logger.info("Metrics fed to all AI models")
        
        return results
    
    def _prepare_metrics_array(self, metrics: Dict[str, Any]) -> np.ndarray:
        """Prepare metrics array"""
        feature_names = ['cpu', 'memory', 'latency', 'error_rate', 'request_rate']
        data_list = []
        
        for name in feature_names:
            if name in metrics and metrics[name] is not None:
                if isinstance(metrics[name], list):
                    data_list.append(np.array(metrics[name]))
                else:
                    data_list.append(np.array([metrics[name]]))
            else:
                data_list.append(np.array([0.0]))
        
        # Find max length
        max_len = max(len(arr) for arr in data_list)
        
        # Pad arrays to same length
        padded = []
        for arr in data_list:
            if len(arr) < max_len:
                padding = np.zeros(max_len - len(arr))
                arr = np.concatenate([padding, arr])
            padded.append(arr[:max_len])
        
        return np.column_stack(padded)
    
    def _state_to_array(self, state: Dict) -> np.ndarray:
        """Convert state to array"""
        return np.array([
            state.get("cpu_usage", 0.0),
            state.get("memory_usage", 0.0),
            state.get("error_rate", 0.0),
            state.get("network_latency", 0.0),
            float(state.get("replicas", 0)),
            state.get("dependency_health", 1.0)
        ], dtype=np.float32)
    
    def _assess_dependency_health(
        self,
        dependency_graph: Any,
        metrics: Dict[str, Any]
    ) -> float:
        """Assess overall dependency health"""
        # Simplified health assessment
        return 1.0

