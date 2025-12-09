"""
Proximal Policy Optimization (PPO) Trainer
Implements PPO algorithm for policy gradient methods
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PPOTrainer:
    """Proximal Policy Optimization trainer for RL agent retraining"""
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
        max_grad_norm: float = 0.5,
        ppo_epochs: int = 4,
        batch_size: int = 64
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.ppo_epochs = ppo_epochs
        self.batch_size = batch_size
        
        # Policy and value networks (simplified - in practice, use neural networks)
        # For this implementation, we'll use a simple policy table
        self.policy_table: Dict[Tuple, np.ndarray] = {}  # State -> action probabilities
        self.value_table: Dict[Tuple, float] = {}  # State -> value estimate
        
        # Training statistics
        self.training_stats = {
            "episodes": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            "policy_loss_history": [],
            "value_loss_history": [],
            "entropy_history": []
        }
    
    def get_state_key(self, state: np.ndarray) -> Tuple:
        """Convert state array to hashable tuple"""
        return tuple(np.round(state, decimals=2))
    
    def get_policy(self, state: np.ndarray) -> np.ndarray:
        """Get action probabilities for state"""
        state_key = self.get_state_key(state)
        
        if state_key not in self.policy_table:
            # Initialize with uniform distribution
            self.policy_table[state_key] = np.ones(self.action_size) / self.action_size
        
        return self.policy_table[state_key]
    
    def get_value(self, state: np.ndarray) -> float:
        """Get value estimate for state"""
        state_key = self.get_state_key(state)
        
        if state_key not in self.value_table:
            self.value_table[state_key] = 0.0
        
        return self.value_table[state_key]
    
    def select_action(self, state: np.ndarray) -> Tuple[int, float]:
        """Select action from policy and return action + log probability"""
        policy = self.get_policy(state)
        action = np.random.choice(self.action_size, p=policy)
        log_prob = np.log(policy[action] + 1e-8)
        
        return action, log_prob
    
    def compute_gae(
        self,
        rewards: List[float],
        values: List[float],
        next_values: List[float],
        dones: List[bool]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute Generalized Advantage Estimation (GAE)"""
        advantages = np.zeros(len(rewards))
        returns = np.zeros(len(rewards))
        
        gae = 0
        for t in reversed(range(len(rewards))):
            if dones[t]:
                delta = rewards[t] - values[t]
                gae = delta
            else:
                delta = rewards[t] + self.gamma * next_values[t] - values[t]
                gae = delta + self.gamma * self.gae_lambda * gae
            
            advantages[t] = gae
            returns[t] = advantages[t] + values[t]
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        return advantages, returns
    
    def update_policy(
        self,
        states: List[np.ndarray],
        actions: List[int],
        old_log_probs: List[float],
        advantages: np.ndarray,
        returns: np.ndarray
    ):
        """Update policy using PPO clipped objective"""
        policy_loss = 0.0
        value_loss = 0.0
        entropy = 0.0
        
        for state, action, old_log_prob, advantage, return_val in zip(
            states, actions, old_log_probs, advantages, returns
        ):
            state_key = self.get_state_key(state)
            
            # Get current policy
            policy = self.get_policy(state)
            new_log_prob = np.log(policy[action] + 1e-8)
            
            # PPO clipped objective
            ratio = np.exp(new_log_prob - old_log_prob)
            clipped_ratio = np.clip(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon)
            
            policy_loss += -min(ratio * advantage, clipped_ratio * advantage)
            
            # Value loss
            current_value = self.get_value(state)
            value_loss += (return_val - current_value) ** 2
            
            # Entropy bonus
            entropy += -np.sum(policy * np.log(policy + 1e-8))
            
            # Update policy (simplified - in practice, use gradient descent)
            # For this implementation, we'll do a simple update
            if advantage > 0:
                # Increase probability of this action
                policy[action] = min(1.0, policy[action] + self.learning_rate * advantage)
                # Renormalize
                policy = policy / policy.sum()
                self.policy_table[state_key] = policy
            
            # Update value estimate
            self.value_table[state_key] = current_value + self.learning_rate * (return_val - current_value)
        
        n = len(states)
        policy_loss = policy_loss / n
        value_loss = value_loss / n
        entropy = entropy / n
        
        total_loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
        
        # Update statistics
        self.training_stats["policy_loss_history"].append(policy_loss)
        self.training_stats["value_loss_history"].append(value_loss)
        self.training_stats["entropy_history"].append(entropy)
        
        logger.info(
            f"PPO Update - Policy Loss: {policy_loss:.4f}, "
            f"Value Loss: {value_loss:.4f}, Entropy: {entropy:.4f}"
        )
        
        return total_loss
    
    def train_episode(
        self,
        states: List[np.ndarray],
        actions: List[int],
        rewards: List[float],
        dones: List[bool]
    ) -> float:
        """Train on a single episode"""
        # Compute values
        values = [self.get_value(state) for state in states]
        next_values = [self.get_value(states[i+1]) if i+1 < len(states) else 0.0 
                      for i in range(len(states))]
        
        # Compute GAE
        advantages, returns = self.compute_gae(rewards, values, next_values, dones)
        
        # Get old log probabilities
        old_log_probs = [np.log(self.get_policy(state)[action] + 1e-8) 
                        for state, action in zip(states, actions)]
        
        # PPO update (multiple epochs)
        for epoch in range(self.ppo_epochs):
            # Shuffle data
            indices = np.random.permutation(len(states))
            
            # Mini-batch updates
            for i in range(0, len(states), self.batch_size):
                batch_indices = indices[i:i+self.batch_size]
                batch_states = [states[j] for j in batch_indices]
                batch_actions = [actions[j] for j in batch_indices]
                batch_old_log_probs = [old_log_probs[j] for j in batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]
                
                self.update_policy(
                    batch_states,
                    batch_actions,
                    batch_old_log_probs,
                    batch_advantages,
                    batch_returns
                )
        
        episode_reward = sum(rewards)
        self.training_stats["episodes"] += 1
        self.training_stats["total_reward"] += episode_reward
        self.training_stats["average_reward"] = self.training_stats["total_reward"] / self.training_stats["episodes"]
        
        return episode_reward
    
    def save_model(self, file_path: str):
        """Save PPO model to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "policy_table": {str(k): v.tolist() for k, v in self.policy_table.items()},
            "value_table": {str(k): v for k, v in self.value_table.items()},
            "state_size": self.state_size,
            "action_size": self.action_size,
            "training_stats": self.training_stats
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Saved PPO model to {file_path}")
    
    def load_model(self, file_path: str):
        """Load PPO model from disk"""
        with open(file_path, 'r') as f:
            model_data = json.load(f)
        
        self.policy_table = {
            eval(k): np.array(v) for k, v in model_data["policy_table"].items()
        }
        self.value_table = {
            eval(k): v for k, v in model_data["value_table"].items()
        }
        self.state_size = model_data["state_size"]
        self.action_size = model_data["action_size"]
        self.training_stats = model_data.get("training_stats", self.training_stats)
        
        logger.info(f"Loaded PPO model from {file_path}")

