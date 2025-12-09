"""
Q-Learning Retraining for RL Agents
Implements Q-Learning algorithm for policy improvement
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging
from pathlib import Path
import json

from .experience_replay import ExperienceReplayBuffer

logger = logging.getLogger(__name__)


class QLearningTrainer:
    """Q-Learning trainer for RL agent retraining"""
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.01,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: state -> action -> Q-value
        self.q_table: Dict[Tuple, np.ndarray] = {}
        
        # Experience replay buffer
        self.replay_buffer = ExperienceReplayBuffer(capacity=100000)
        
        # Training statistics
        self.training_stats = {
            "episodes": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            "loss_history": []
        }
    
    def get_state_key(self, state: np.ndarray) -> Tuple:
        """Convert state array to hashable tuple (discretized)"""
        # Discretize state for Q-table (simple approach)
        # In practice, you might use function approximation
        discretized = tuple(np.round(state, decimals=2))
        return discretized
    
    def get_q_value(self, state: np.ndarray, action: int) -> float:
        """Get Q-value for state-action pair"""
        state_key = self.get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        return self.q_table[state_key][action]
    
    def update_q_value(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """Update Q-value using Q-Learning update rule"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        
        # Initialize Q-table entries if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_size)
        
        # Q-Learning update: Q(s,a) = Q(s,a) + α[r + γ * max(Q(s',a')) - Q(s,a)]
        current_q = self.q_table[state_key][action]
        
        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        self.q_table[state_key][action] = current_q + self.learning_rate * (target_q - current_q)
        
        # Add to replay buffer
        self.replay_buffer.add(state, action, reward, next_state, done)
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""
        state_key = self.get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        
        # Epsilon-greedy exploration
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        else:
            return np.argmax(self.q_table[state_key])
    
    def train_from_replay(self, batch_size: int = 32, epochs: int = 1):
        """Train using experience replay"""
        if len(self.replay_buffer) < batch_size:
            logger.warning(f"Insufficient experiences: {len(self.replay_buffer)} < {batch_size}")
            return
        
        total_loss = 0.0
        
        for epoch in range(epochs):
            # Sample batch
            states, actions, rewards, next_states, dones = self.replay_buffer.sample_batch(batch_size)
            
            # Update Q-values for each experience
            for i in range(batch_size):
                self.update_q_value(
                    states[i],
                    actions[i],
                    rewards[i],
                    next_states[i],
                    bool(dones[i])
                )
            
            # Calculate loss (TD error)
            batch_loss = 0.0
            for i in range(batch_size):
                current_q = self.get_q_value(states[i], actions[i])
                
                if dones[i]:
                    target_q = rewards[i]
                else:
                    next_state_key = self.get_state_key(next_states[i])
                    if next_state_key in self.q_table:
                        target_q = rewards[i] + self.gamma * np.max(self.q_table[next_state_key])
                    else:
                        target_q = rewards[i]
                
                batch_loss += abs(target_q - current_q)
            
            total_loss += batch_loss / batch_size
        
        avg_loss = total_loss / epochs
        self.training_stats["loss_history"].append(avg_loss)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        logger.info(f"Training completed: Loss={avg_loss:.4f}, Epsilon={self.epsilon:.4f}")
    
    def train_episode(self, experiences: List[Tuple]) -> float:
        """Train on a single episode of experiences"""
        episode_reward = 0.0
        
        for state, action, reward, next_state, done in experiences:
            self.update_q_value(state, action, reward, next_state, done)
            episode_reward += reward
        
        self.training_stats["episodes"] += 1
        self.training_stats["total_reward"] += episode_reward
        
        # Update average reward
        episodes = self.training_stats["episodes"]
        self.training_stats["average_reward"] = self.training_stats["total_reward"] / episodes
        
        return episode_reward
    
    def save_model(self, file_path: str):
        """Save Q-table to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert Q-table to serializable format
        q_table_serializable = {
            str(k): v.tolist() for k, v in self.q_table.items()
        }
        
        model_data = {
            "q_table": q_table_serializable,
            "state_size": self.state_size,
            "action_size": self.action_size,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "training_stats": self.training_stats
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Saved Q-Learning model to {file_path}")
    
    def load_model(self, file_path: str):
        """Load Q-table from disk"""
        with open(file_path, 'r') as f:
            model_data = json.load(f)
        
        # Restore Q-table
        self.q_table = {
            eval(k): np.array(v) for k, v in model_data["q_table"].items()
        }
        
        self.state_size = model_data["state_size"]
        self.action_size = model_data["action_size"]
        self.learning_rate = model_data["learning_rate"]
        self.gamma = model_data["gamma"]
        self.epsilon = model_data.get("epsilon", self.epsilon)
        self.training_stats = model_data.get("training_stats", self.training_stats)
        
        logger.info(f"Loaded Q-Learning model from {file_path}")

