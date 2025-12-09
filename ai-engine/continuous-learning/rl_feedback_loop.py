"""
Reinforcement Learning Feedback Loop
Updates agent policies based on real-world feedback
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class RewardConfig:
    """Configuration for reward calculation"""
    success_reward: float = 10.0
    failure_penalty: float = -10.0
    slow_recovery_penalty: float = -2.0
    fast_recovery_bonus: float = 2.0
    recovery_time_threshold: float = 5.0  # seconds
    repeated_failure_penalty: float = -5.0


@dataclass
class ActionFeedback:
    """Feedback for a single action"""
    agent_name: str
    action_type: str
    success: bool
    recovery_time: float
    reward: float
    timestamp: float
    context: Dict


class RLFeedbackLoop:
    """Reinforcement Learning feedback loop for agent policy updates"""
    
    def __init__(self, agent_name: str, reward_config: Optional[RewardConfig] = None):
        self.agent_name = agent_name
        self.reward_config = reward_config or RewardConfig()
        
        # Track action history for pattern detection
        self.action_history: List[ActionFeedback] = []
        self.failure_count = defaultdict(int)
        self.success_count = defaultdict(int)
        
        # Policy update tracking
        self.policy_updates = []
        self.total_reward = 0.0
        self.episode_count = 0
        
        # Storage for feedback data
        self.storage_path = Path("data/continuous-learning/feedback")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def update_reward(
        self,
        success: bool,
        recovery_time: float,
        action_type: str = "default",
        context: Optional[Dict] = None
    ) -> float:
        """
        Calculate reward based on action outcome and recovery time
        
        Args:
            success: Whether the action was successful
            recovery_time: Time taken to recover (in seconds)
            action_type: Type of action performed
            context: Additional context about the action
        
        Returns:
            Calculated reward value
        """
        import time
        
        # Base reward based on success/failure
        if success:
            reward = self.reward_config.success_reward
            self.success_count[action_type] += 1
        else:
            reward = self.reward_config.failure_penalty
            self.failure_count[action_type] += 1
            
            # Penalize repeated failures
            if self.failure_count[action_type] > 1:
                reward += self.reward_config.repeated_failure_penalty
        
        # Adjust reward based on recovery time
        if recovery_time > self.reward_config.recovery_time_threshold:
            # Penalize slow recovery
            reward += self.reward_config.slow_recovery_penalty
            logger.debug(f"Slow recovery penalty applied: {recovery_time}s > {self.reward_config.recovery_time_threshold}s")
        elif recovery_time > 0 and recovery_time < self.reward_config.recovery_time_threshold / 2:
            # Bonus for fast recovery
            reward += self.reward_config.fast_recovery_bonus
            logger.debug(f"Fast recovery bonus applied: {recovery_time}s")
        
        # Create feedback record
        feedback = ActionFeedback(
            agent_name=self.agent_name,
            action_type=action_type,
            success=success,
            recovery_time=recovery_time,
            reward=reward,
            timestamp=time.time(),
            context=context or {}
        )
        
        # Store feedback
        self.action_history.append(feedback)
        self.total_reward += reward
        
        # Log feedback
        logger.info(
            f"RL Feedback - Agent: {self.agent_name}, "
            f"Action: {action_type}, Success: {success}, "
            f"Recovery Time: {recovery_time:.2f}s, Reward: {reward:.2f}"
        )
        
        # Save feedback to disk periodically
        if len(self.action_history) % 100 == 0:
            self._save_feedback()
        
        return reward
    
    def get_success_rate(self, action_type: Optional[str] = None) -> float:
        """Calculate success rate for actions"""
        if action_type:
            total = self.success_count[action_type] + self.failure_count[action_type]
            if total == 0:
                return 0.0
            return self.success_count[action_type] / total
        else:
            total_success = sum(self.success_count.values())
            total_failure = sum(self.failure_count.values())
            total = total_success + total_failure
            if total == 0:
                return 0.0
            return total_success / total
    
    def get_average_reward(self, window_size: int = 100) -> float:
        """Calculate average reward over recent actions"""
        if not self.action_history:
            return 0.0
        
        recent_feedback = self.action_history[-window_size:]
        if not recent_feedback:
            return 0.0
        
        return np.mean([f.reward for f in recent_feedback])
    
    def get_policy_recommendations(self) -> Dict[str, any]:
        """Generate policy recommendations based on feedback"""
        recommendations = {
            "agent_name": self.agent_name,
            "success_rate": self.get_success_rate(),
            "average_reward": self.get_average_reward(),
            "total_actions": len(self.action_history),
            "recommendations": []
        }
        
        # Analyze failure patterns
        if self.failure_count:
            most_failed_action = max(self.failure_count.items(), key=lambda x: x[1])
            recommendations["recommendations"].append({
                "type": "action_improvement",
                "action": most_failed_action[0],
                "failure_count": most_failed_action[1],
                "suggestion": f"Review and improve {most_failed_action[0]} action logic"
            })
        
        # Check if recovery time is consistently high
        if self.action_history:
            avg_recovery_time = np.mean([f.recovery_time for f in self.action_history[-100:]])
            if avg_recovery_time > self.reward_config.recovery_time_threshold:
                recommendations["recommendations"].append({
                    "type": "performance_optimization",
                    "metric": "recovery_time",
                    "current_avg": avg_recovery_time,
                    "threshold": self.reward_config.recovery_time_threshold,
                    "suggestion": "Optimize action execution to reduce recovery time"
                })
        
        # Check success rate
        success_rate = self.get_success_rate()
        if success_rate < 0.8:
            recommendations["recommendations"].append({
                "type": "policy_update",
                "metric": "success_rate",
                "current_value": success_rate,
                "target_value": 0.8,
                "suggestion": "Consider retraining model or adjusting decision thresholds"
            })
        
        return recommendations
    
    def should_retrain(self, min_episodes: int = 1000, min_success_rate: float = 0.8) -> bool:
        """Determine if model should be retrained"""
        if len(self.action_history) < min_episodes:
            return False
        
        success_rate = self.get_success_rate()
        if success_rate < min_success_rate:
            logger.info(f"Retraining recommended: Success rate {success_rate:.2f} < {min_success_rate}")
            return True
        
        return False
    
    def _save_feedback(self):
        """Save feedback history to disk"""
        if not self.action_history:
            return
        
        import time
        timestamp = int(time.time())
        file_path = self.storage_path / f"{self.agent_name}_feedback_{timestamp}.json"
        
        feedback_data = {
            "agent_name": self.agent_name,
            "total_actions": len(self.action_history),
            "total_reward": self.total_reward,
            "success_rate": self.get_success_rate(),
            "average_reward": self.get_average_reward(),
            "feedback": [
                {
                    "action_type": f.action_type,
                    "success": f.success,
                    "recovery_time": f.recovery_time,
                    "reward": f.reward,
                    "timestamp": f.timestamp,
                    "context": f.context
                }
                for f in self.action_history[-1000:]  # Save last 1000 actions
            ]
        }
        
        with open(file_path, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        logger.debug(f"Saved feedback to {file_path}")
    
    def reset_episode(self):
        """Reset episode counters (call after policy update)"""
        self.episode_count += 1
        logger.info(f"Episode {self.episode_count} completed for {self.agent_name}")


class SelfHealingRLFeedback(RLFeedbackLoop):
    """Specialized RL feedback loop for Self-Healing Agent"""
    
    def __init__(self, reward_config: Optional[RewardConfig] = None):
        super().__init__("self-healing", reward_config)
        # Additional tracking for healing-specific metrics
        self.healing_attempts = 0
        self.successful_healings = 0
        self.failed_healings = 0
    
    def update_healing_feedback(
        self,
        success: bool,
        recovery_time: float,
        healing_action: str,
        failure_type: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> float:
        """Update feedback for healing action"""
        self.healing_attempts += 1
        
        if success:
            self.successful_healings += 1
        else:
            self.failed_healings += 1
        
        # Additional context for healing
        healing_context = {
            "healing_action": healing_action,
            "failure_type": failure_type,
            "healing_attempt": self.healing_attempts,
            **(context or {})
        }
        
        return self.update_reward(
            success=success,
            recovery_time=recovery_time,
            action_type=healing_action,
            context=healing_context
        )
    
    def get_healing_success_rate(self) -> float:
        """Get success rate for healing actions"""
        if self.healing_attempts == 0:
            return 0.0
        return self.successful_healings / self.healing_attempts


class ScalingRLFeedback(RLFeedbackLoop):
    """Specialized RL feedback loop for Scaling Agent"""
    
    def __init__(self, reward_config: Optional[RewardConfig] = None):
        super().__init__("scaling", reward_config)
        self.scaling_actions = 0
        self.optimal_scalings = 0
    
    def update_scaling_feedback(
        self,
        success: bool,
        recovery_time: float,
        scaling_action: str,  # "scale_up", "scale_down", "maintain"
        resource_utilization: float,
        context: Optional[Dict] = None
    ) -> float:
        """Update feedback for scaling action"""
        self.scaling_actions += 1
        
        # Adjust reward based on resource utilization
        scaling_context = {
            "scaling_action": scaling_action,
            "resource_utilization": resource_utilization,
            **(context or {})
        }
        
        reward = self.update_reward(
            success=success,
            recovery_time=recovery_time,
            action_type=scaling_action,
            context=scaling_context
        )
        
        # Bonus for optimal scaling (utilization between 40-80%)
        if success and 0.4 <= resource_utilization <= 0.8:
            reward += 3.0
            self.optimal_scalings += 1
        
        return reward

