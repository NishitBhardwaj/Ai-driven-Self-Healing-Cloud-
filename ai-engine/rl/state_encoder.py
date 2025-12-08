"""
State Encoder for RL Agent
Encodes system state into feature vectors for neural network input
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class StateEncoder:
    """
    Encodes system state into feature vectors
    
    Handles:
    - Feature extraction
    - Normalization
    - Feature engineering
    - Categorical encoding
    """
    
    def __init__(self, feature_config: Optional[Dict] = None):
        """
        Initialize state encoder
        
        Args:
            feature_config: Configuration for feature extraction
        """
        self.feature_config = feature_config or self._default_config()
        self.feature_names = self._get_feature_names()
        self.feature_dim = len(self.feature_names)
        
        # Normalization parameters
        self.mean_values = None
        self.std_values = None
        self.max_values = None
        self.min_values = None
        
        logger.info(f"StateEncoder initialized with {self.feature_dim} features")
    
    def _default_config(self) -> Dict:
        """Default feature configuration"""
        return {
            'include_pod_metrics': True,
            'include_resource_metrics': True,
            'include_service_metrics': True,
            'include_deployment_metrics': True,
            'include_failure_indicators': True,
            'include_temporal_features': True,
            'include_derived_features': True,
            'normalize': True
        }
    
    def _get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        features = []
        config = self.feature_config
        
        if config.get('include_pod_metrics', True):
            features.extend(['pod_count', 'healthy_pods', 'failed_pods', 'restart_count'])
        
        if config.get('include_resource_metrics', True):
            features.extend(['cpu_usage', 'memory_usage', 'network_latency'])
        
        if config.get('include_service_metrics', True):
            features.extend(['request_rate', 'error_rate', 'response_time'])
        
        if config.get('include_deployment_metrics', True):
            features.extend(['deployment_replicas', 'desired_replicas', 'available_replicas'])
        
        if config.get('include_failure_indicators', True):
            features.extend(['has_crash', 'has_timeout', 'has_resource_exhaustion'])
        
        if config.get('include_temporal_features', True):
            features.extend(['time_since_last_action', 'episode_step'])
        
        if config.get('include_derived_features', True):
            features.extend([
                'health_ratio',
                'replica_ratio',
                'resource_pressure',
                'system_stability_score'
            ])
        
        return features
    
    def encode(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Encode state dictionary into feature vector
        
        Args:
            state: State dictionary
        
        Returns:
            Feature vector as numpy array
        """
        features = []
        config = self.feature_config
        
        # Pod metrics
        if config.get('include_pod_metrics', True):
            features.extend([
                state.get('pod_count', 0),
                state.get('healthy_pods', 0),
                state.get('failed_pods', 0),
                state.get('restart_count', 0)
            ])
        
        # Resource metrics
        if config.get('include_resource_metrics', True):
            features.extend([
                state.get('cpu_usage', 0.0),
                state.get('memory_usage', 0.0),
                state.get('network_latency', 0.0)
            ])
        
        # Service metrics
        if config.get('include_service_metrics', True):
            features.extend([
                state.get('request_rate', 0.0),
                state.get('error_rate', 0.0),
                state.get('response_time', 0.0)
            ])
        
        # Deployment metrics
        if config.get('include_deployment_metrics', True):
            features.extend([
                state.get('deployment_replicas', 0),
                state.get('desired_replicas', 0),
                state.get('available_replicas', 0)
            ])
        
        # Failure indicators
        if config.get('include_failure_indicators', True):
            features.extend([
                float(state.get('has_crash', False)),
                float(state.get('has_timeout', False)),
                float(state.get('has_resource_exhaustion', False))
            ])
        
        # Temporal features
        if config.get('include_temporal_features', True):
            features.extend([
                state.get('time_since_last_action', 0),
                state.get('episode_step', 0)
            ])
        
        # Derived features
        if config.get('include_derived_features', True):
            pod_count = max(state.get('pod_count', 1), 1)
            healthy_pods = state.get('healthy_pods', 0)
            desired_replicas = max(state.get('desired_replicas', 1), 1)
            available_replicas = state.get('available_replicas', 0)
            
            features.extend([
                healthy_pods / pod_count,  # health_ratio
                available_replicas / desired_replicas,  # replica_ratio
                (state.get('cpu_usage', 0) + state.get('memory_usage', 0)) / 200.0,  # resource_pressure
                self._compute_stability_score(state)  # system_stability_score
            ])
        
        feature_vector = np.array(features, dtype=np.float32)
        
        # Normalize if configured
        if config.get('normalize', True):
            feature_vector = self.normalize(feature_vector)
        
        return feature_vector
    
    def _compute_stability_score(self, state: Dict[str, Any]) -> float:
        """
        Compute system stability score
        
        Args:
            state: State dictionary
        
        Returns:
            Stability score [0, 1]
        """
        score = 1.0
        
        # Penalize failures
        if state.get('has_crash', False):
            score -= 0.3
        if state.get('has_timeout', False):
            score -= 0.2
        if state.get('has_resource_exhaustion', False):
            score -= 0.2
        
        # Penalize high error rate
        error_rate = state.get('error_rate', 0)
        score -= min(error_rate / 100.0, 0.3)
        
        # Penalize resource pressure
        cpu = state.get('cpu_usage', 0)
        memory = state.get('memory_usage', 0)
        if cpu > 90 or memory > 90:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def normalize(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize feature vector
        
        Args:
            features: Feature vector
        
        Returns:
            Normalized feature vector
        """
        if self.mean_values is not None and self.std_values is not None:
            # Z-score normalization
            normalized = (features - self.mean_values) / (self.std_values + 1e-8)
            return normalized
        elif self.max_values is not None and self.min_values is not None:
            # Min-max normalization
            normalized = (features - self.min_values) / (self.max_values - self.min_values + 1e-8)
            return normalized
        else:
            # Default normalization (assume reasonable ranges)
            return self._default_normalize(features)
    
    def _default_normalize(self, features: np.ndarray) -> np.ndarray:
        """Default normalization using assumed ranges"""
        normalized = features.copy()
        idx = 0
        
        # Pod metrics [0, 100]
        if self.feature_config.get('include_pod_metrics', True):
            for i in range(4):
                if idx < len(normalized):
                    normalized[idx] = normalized[idx] / 100.0
                    idx += 1
        
        # Resource metrics [0, 100] for CPU/Memory, [0, 1000] for latency
        if self.feature_config.get('include_resource_metrics', True):
            normalized[idx] = normalized[idx] / 100.0  # cpu
            idx += 1
            normalized[idx] = normalized[idx] / 100.0  # memory
            idx += 1
            normalized[idx] = normalized[idx] / 1000.0  # latency
            idx += 1
        
        # Service metrics
        if self.feature_config.get('include_service_metrics', True):
            normalized[idx] = normalized[idx] / 10000.0  # request_rate
            idx += 1
            normalized[idx] = normalized[idx] / 100.0  # error_rate
            idx += 1
            normalized[idx] = normalized[idx] / 5000.0  # response_time
            idx += 1
        
        # Deployment metrics [0, 50]
        if self.feature_config.get('include_deployment_metrics', True):
            for i in range(3):
                if idx < len(normalized):
                    normalized[idx] = normalized[idx] / 50.0
                    idx += 1
        
        # Failure indicators [0, 1] - already normalized
        if self.feature_config.get('include_failure_indicators', True):
            idx += 3
        
        # Temporal features
        if self.feature_config.get('include_temporal_features', True):
            normalized[idx] = normalized[idx] / 3600.0  # time_since_last_action
            idx += 1
            normalized[idx] = normalized[idx] / 1000.0  # episode_step
            idx += 1
        
        # Derived features [0, 1] - already normalized
        if self.feature_config.get('include_derived_features', True):
            idx += 4
        
        return normalized
    
    def fit(self, states: List[Dict[str, Any]]):
        """
        Fit normalization parameters on training data
        
        Args:
            states: List of state dictionaries
        """
        if not states:
            return
        
        # Encode all states
        encoded_states = np.array([self.encode(state) for state in states])
        
        # Compute statistics
        self.mean_values = np.mean(encoded_states, axis=0)
        self.std_values = np.std(encoded_states, axis=0)
        self.max_values = np.max(encoded_states, axis=0)
        self.min_values = np.min(encoded_states, axis=0)
        
        logger.info("State encoder fitted on training data")
    
    def get_feature_importance(self, state: Dict[str, Any]) -> Dict[str, float]:
        """
        Get importance of each feature for current state
        
        Args:
            state: State dictionary
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        importance = {}
        encoded = self.encode(state)
        
        for i, feature_name in enumerate(self.feature_names):
            if i < len(encoded):
                # Importance based on absolute value (normalized)
                importance[feature_name] = abs(encoded[i])
        
        # Normalize importance scores
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        
        return importance
    
    def get_feature_dim(self) -> int:
        """Get feature dimension"""
        return self.feature_dim
    
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self.feature_names.copy()

