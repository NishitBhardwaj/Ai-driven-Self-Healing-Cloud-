"""
Reward Functions for RL Agent
Rewards based on: +uptime, +response time, +recovery speed, -errors, -cost
"""

import numpy as np
from typing import Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RewardType(Enum):
    """Types of reward functions"""
    BASIC = "basic"
    UPTIME_FOCUSED = "uptime_focused"
    PERFORMANCE_FOCUSED = "performance_focused"
    COST_AWARE = "cost_aware"
    BALANCED = "balanced"


class RewardFunction:
    """Base class for reward functions"""
    
    def compute(self, state: Dict[str, Any], action: int, 
                next_state: Dict[str, Any], done: bool) -> float:
        """
        Compute reward
        
        Args:
            state: Current state
            action: Action taken
            next_state: Next state
            done: Whether episode is done
        
        Returns:
            Reward value
        """
        raise NotImplementedError


class BasicRewardFunction(RewardFunction):
    """
    Basic reward function:
    - Positive reward for uptime
    - Positive reward for good response time
    - Positive reward for fast recovery
    - Negative reward for errors
    - Negative reward for cost
    """
    
    def compute(self, state: Dict[str, Any], action: int,
                next_state: Dict[str, Any], done: bool) -> float:
        reward = 0.0
        
        # + Uptime (higher is better, normalized to [0, 1])
        uptime_reward = next_state.get('uptime', 0) / 100.0
        reward += uptime_reward * 2.0  # Weight: 2.0
        
        # + Response time (lower is better, inverted)
        response_time = next_state.get('response_time', 200)
        # Normalize: 0ms = 1.0, 1000ms = 0.0
        response_reward = max(0, 1.0 - (response_time / 1000.0))
        reward += response_reward * 1.5  # Weight: 1.5
        
        # + Recovery speed (faster recovery = higher reward)
        recovery_time = next_state.get('recovery_time', 0)
        if recovery_time > 0:
            # Faster recovery = higher reward (inverse relationship)
            recovery_reward = max(0, 1.0 - (recovery_time / 60.0))
            reward += recovery_reward * 1.0  # Weight: 1.0
        elif state.get('recovery_time', 0) > 0 and recovery_time == 0:
            # Just recovered
            reward += 1.0
        
        # - Errors (lower is better)
        error_rate = next_state.get('error_rate', 0)
        error_penalty = (error_rate / 100.0) * 2.0  # Weight: 2.0
        reward -= error_penalty
        
        # - Cost (lower is better)
        cost = next_state.get('cost', 0)
        cost_penalty = cost * 0.5  # Weight: 0.5
        reward -= cost_penalty
        
        # Bonus for fixing crashes
        if state.get('has_crash', False) and not next_state.get('has_crash', False):
            reward += 2.0
        
        # Penalty for new crashes
        if not state.get('has_crash', False) and next_state.get('has_crash', False):
            reward -= 2.0
        
        return reward


class UptimeFocusedRewardFunction(RewardFunction):
    """
    Reward function focused on maximizing uptime
    """
    
    def compute(self, state: Dict[str, Any], action: int,
                next_state: Dict[str, Any], done: bool) -> float:
        reward = 0.0
        
        # Heavy weight on uptime
        uptime = next_state.get('uptime', 0)
        reward += (uptime / 100.0) * 5.0
        
        # Penalty for downtime
        if next_state.get('has_crash', False):
            reward -= 3.0
        
        # Penalty for errors (affects uptime)
        error_rate = next_state.get('error_rate', 0)
        reward -= (error_rate / 100.0) * 2.0
        
        # Small penalty for cost
        cost = next_state.get('cost', 0)
        reward -= cost * 0.2
        
        return reward


class PerformanceFocusedRewardFunction(RewardFunction):
    """
    Reward function focused on performance (response time, recovery speed)
    """
    
    def compute(self, state: Dict[str, Any], action: int,
                next_state: Dict[str, Any], done: bool) -> float:
        reward = 0.0
        
        # Response time (lower is better)
        response_time = next_state.get('response_time', 200)
        response_reward = max(0, 1.0 - (response_time / 1000.0))
        reward += response_reward * 3.0
        
        # Recovery speed (faster is better)
        recovery_time = next_state.get('recovery_time', 0)
        if recovery_time > 0:
            recovery_reward = max(0, 1.0 - (recovery_time / 60.0))
            reward += recovery_reward * 2.0
        elif state.get('recovery_time', 0) > 0:
            # Just recovered
            reward += 2.0
        
        # Latency (lower is better)
        latency = next_state.get('network_latency', 50)
        latency_reward = max(0, 1.0 - (latency / 500.0))
        reward += latency_reward * 1.0
        
        # Penalty for errors (affects performance)
        error_rate = next_state.get('error_rate', 0)
        reward -= (error_rate / 100.0) * 1.5
        
        return reward


class CostAwareRewardFunction(RewardFunction):
    """
    Reward function that balances performance with cost
    """
    
    def compute(self, state: Dict[str, Any], action: int,
                next_state: Dict[str, Any], done: bool) -> float:
        reward = 0.0
        
        # Uptime (moderate weight)
        uptime = next_state.get('uptime', 0)
        reward += (uptime / 100.0) * 2.0
        
        # Response time (moderate weight)
        response_time = next_state.get('response_time', 200)
        response_reward = max(0, 1.0 - (response_time / 1000.0))
        reward += response_reward * 1.5
        
        # Heavy penalty for cost
        cost = next_state.get('cost', 0)
        reward -= cost * 2.0
        
        # Penalty for over-provisioning (too many replicas)
        replicas = next_state.get('replicas', 2)
        if replicas > 10:
            reward -= (replicas - 10) * 0.1
        
        # Reward for cost optimization (scaling down when appropriate)
        if action == 1:  # SCALE_DOWN
            if state.get('cpu_usage', 0) < 50 and state.get('memory_usage', 0) < 50:
                reward += 0.5
        
        # Penalty for errors
        error_rate = next_state.get('error_rate', 0)
        reward -= (error_rate / 100.0) * 1.0
        
        return reward


class BalancedRewardFunction(RewardFunction):
    """
    Balanced reward function considering all factors
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            'uptime': 0.3,
            'response_time': 0.25,
            'recovery_speed': 0.2,
            'errors': 0.15,
            'cost': 0.1
        }
    
    def compute(self, state: Dict[str, Any], action: int,
                next_state: Dict[str, Any], done: bool) -> float:
        reward = 0.0
        
        # + Uptime
        uptime = next_state.get('uptime', 0)
        reward += (uptime / 100.0) * self.weights['uptime'] * 10.0
        
        # + Response time (inverted - lower is better)
        response_time = next_state.get('response_time', 200)
        response_reward = max(0, 1.0 - (response_time / 1000.0))
        reward += response_reward * self.weights['response_time'] * 10.0
        
        # + Recovery speed (inverted - faster is better)
        recovery_time = next_state.get('recovery_time', 0)
        if recovery_time > 0:
            recovery_reward = max(0, 1.0 - (recovery_time / 60.0))
            reward += recovery_reward * self.weights['recovery_speed'] * 10.0
        elif state.get('recovery_time', 0) > 0:
            # Just recovered
            reward += self.weights['recovery_speed'] * 10.0
        
        # - Errors
        error_rate = next_state.get('error_rate', 0)
        reward -= (error_rate / 100.0) * self.weights['errors'] * 10.0
        
        # - Cost
        cost = next_state.get('cost', 0)
        reward -= cost * self.weights['cost'] * 10.0
        
        # Bonus for maintaining good state
        if (uptime > 95 and response_time < 300 and error_rate < 5):
            reward += 1.0
        
        # Penalty for critical failures
        if next_state.get('has_crash', False) or error_rate > 50:
            reward -= 3.0
        
        return reward


class RewardFunctionFactory:
    """Factory for creating reward functions"""
    
    @staticmethod
    def create(reward_type: RewardType, **kwargs) -> RewardFunction:
        """
        Create a reward function
        
        Args:
            reward_type: Type of reward function
            **kwargs: Additional arguments for specific reward functions
        
        Returns:
            Reward function instance
        """
        if reward_type == RewardType.BASIC:
            return BasicRewardFunction()
        elif reward_type == RewardType.UPTIME_FOCUSED:
            return UptimeFocusedRewardFunction()
        elif reward_type == RewardType.PERFORMANCE_FOCUSED:
            return PerformanceFocusedRewardFunction()
        elif reward_type == RewardType.COST_AWARE:
            return CostAwareRewardFunction()
        elif reward_type == RewardType.BALANCED:
            weights = kwargs.get('weights', None)
            return BalancedRewardFunction(weights=weights)
        else:
            raise ValueError(f"Unknown reward type: {reward_type}")
