"""
Confidence Estimator
Compute decision confidence based on:
- Model agreement
- Historical accuracy
- Situation complexity
- Risk score
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ConfidenceEstimator:
    """
    Estimates confidence in decisions based on multiple factors:
    - Model agreement
    - Historical accuracy
    - Situation complexity
    - Risk score
    """
    
    def __init__(self):
        self.component_history = {}  # Track component performance
        self.decision_history = []  # Track decision outcomes
        logger.info("ConfidenceEstimator initialized")
    
    def estimate_confidence(
        self,
        recommendations: List[Dict[str, Any]],
        situation_complexity: float = 0.5,
        risk_score: float = 0.5,
        component_weights: Optional[Dict[str, float]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Estimate overall confidence from multiple factors
        
        Args:
            recommendations: List of recommendations from different components
            situation_complexity: Complexity of situation [0, 1]
            risk_score: Risk score [0, 1]
            component_weights: Weights for each component
        
        Returns:
            Tuple of (confidence, details)
        """
        if not recommendations:
            return 0.0, {"reason": "No recommendations"}
        
        # Factor 1: Model agreement
        agreement_score = self._calculate_model_agreement(recommendations)
        
        # Factor 2: Historical accuracy
        historical_accuracy = self._get_historical_accuracy(recommendations)
        
        # Factor 3: Situation complexity (inverse - lower complexity = higher confidence)
        complexity_factor = 1.0 - situation_complexity
        
        # Factor 4: Risk score (inverse - lower risk = higher confidence)
        risk_factor = 1.0 - risk_score
        
        # Factor 5: Individual component confidences
        weighted_confidence = self._calculate_weighted_confidence(
            recommendations,
            component_weights
        )
        
        # Combine factors
        confidence = (
            agreement_score * 0.3 +
            historical_accuracy * 0.3 +
            complexity_factor * 0.2 +
            risk_factor * 0.1 +
            weighted_confidence * 0.1
        )
        
        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        details = {
            "agreement_score": agreement_score,
            "historical_accuracy": historical_accuracy,
            "complexity_factor": complexity_factor,
            "risk_factor": risk_factor,
            "weighted_confidence": weighted_confidence,
            "final_confidence": confidence,
            "situation_complexity": situation_complexity,
            "risk_score": risk_score
        }
        
        logger.debug(f"Confidence estimated: {confidence:.2f} (agreement: {agreement_score:.2f}, "
                    f"historical: {historical_accuracy:.2f})")
        
        return confidence, details
    
    def _calculate_model_agreement(self, recommendations: List[Dict[str, Any]]) -> float:
        """
        Calculate agreement between models
        
        Args:
            recommendations: List of recommendations
        
        Returns:
            Agreement score [0, 1]
        """
        if len(recommendations) <= 1:
            return 1.0
        
        # Extract actions
        actions = [r.get("action", "unknown") for r in recommendations]
        
        # Count most common action
        from collections import Counter
        action_counts = Counter(actions)
        most_common_count = action_counts.most_common(1)[0][1]
        
        # Agreement = proportion of models agreeing
        agreement = most_common_count / len(actions)
        
        # Also consider confidence alignment
        confidences = [r.get("confidence", 0.0) for r in recommendations]
        if confidences:
            confidence_std = np.std(confidences)
            # Lower std = higher alignment
            alignment_factor = 1.0 - min(1.0, confidence_std)
            agreement = (agreement + alignment_factor) / 2.0
        
        return agreement
    
    def _get_historical_accuracy(self, recommendations: List[Dict[str, Any]]) -> float:
        """
        Get historical accuracy of components
        
        Args:
            recommendations: List of recommendations
        
        Returns:
            Historical accuracy score [0, 1]
        """
        if not recommendations:
            return 0.5
        
        accuracies = []
        for rec in recommendations:
            component = rec.get("source", "unknown")
            if component in self.component_history:
                hist = self.component_history[component]
                if hist["count"] > 0:
                    accuracy = hist["successes"] / hist["count"]
                    accuracies.append(accuracy)
        
        if accuracies:
            return np.mean(accuracies)
        else:
            return 0.5  # Default if no history
    
    def _calculate_weighted_confidence(
        self,
        recommendations: List[Dict[str, Any]],
        component_weights: Optional[Dict[str, float]]
    ) -> float:
        """
        Calculate weighted average confidence
        
        Args:
            recommendations: List of recommendations
            component_weights: Weights for components
        
        Returns:
            Weighted confidence [0, 1]
        """
        if not recommendations:
            return 0.0
        
        if component_weights:
            weighted_sum = sum(
                r.get("confidence", 0.0) * component_weights.get(r.get("source", "unknown"), 1.0)
                for r in recommendations
            )
            total_weight = sum(
                component_weights.get(r.get("source", "unknown"), 1.0)
                for r in recommendations
            )
            if total_weight > 0:
                return weighted_sum / total_weight
        
        # Simple average if no weights
        return np.mean([r.get("confidence", 0.0) for r in recommendations])
    
    def update_component_performance(
        self,
        component: str,
        success: bool,
        confidence: float
    ):
        """
        Update component performance history
        
        Args:
            component: Component name
            success: Whether decision was successful
            confidence: Confidence of decision
        """
        if component not in self.component_history:
            self.component_history[component] = {
                "successes": 0,
                "failures": 0,
                "count": 0,
                "total_confidence": 0.0
            }
        
        hist = self.component_history[component]
        hist["count"] += 1
        hist["total_confidence"] += confidence
        
        if success:
            hist["successes"] += 1
        else:
            hist["failures"] += 1
    
    def update_decision_outcome(
        self,
        decision_id: str,
        success: bool,
        actual_confidence: float
    ):
        """
        Update decision outcome
        
        Args:
            decision_id: Decision identifier
            success: Whether decision was successful
            actual_confidence: Actual confidence achieved
        """
        self.decision_history.append({
            "decision_id": decision_id,
            "success": success,
            "actual_confidence": actual_confidence,
            "timestamp": np.datetime64('now')
        })
        
        # Keep only recent history
        if len(self.decision_history) > 10000:
            self.decision_history = self.decision_history[-10000:]
    
    def get_component_reliability(self, component: str) -> float:
        """
        Get reliability score for a component
        
        Args:
            component: Component name
        
        Returns:
            Reliability score [0, 1]
        """
        if component not in self.component_history:
            return 0.5
        
        hist = self.component_history[component]
        if hist["count"] == 0:
            return 0.5
        
        success_rate = hist["successes"] / hist["count"]
        avg_confidence = hist["total_confidence"] / hist["count"]
        
        # Combine success rate and confidence
        reliability = 0.7 * success_rate + 0.3 * avg_confidence
        
        return reliability
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get confidence estimation statistics"""
        return {
            "components_tracked": len(self.component_history),
            "decisions_tracked": len(self.decision_history),
            "component_reliabilities": {
                comp: self.get_component_reliability(comp)
                for comp in self.component_history.keys()
            }
        }
