"""
Deep Q-Network (DQN) Trainer
Implements DQN algorithm with neural network function approximation
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import json

from .experience_replay import ExperienceReplayBuffer, PrioritizedExperienceReplay

logger = logging.getLogger(__name__)


class DQNTrainer:
    """Deep Q-Network trainer for RL agent retraining"""
    
    def __init__(
        self,
        state_size: int,
        action_size: int,
        learning_rate: float = 0.001,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        target_update_frequency: int = 100,
        use_prioritized_replay: bool = False
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.target_update_frequency = target_update_frequency
        self.update_counter = 0
        
        # Experience replay buffer
        if use_prioritized_replay:
            self.replay_buffer = PrioritizedExperienceReplay(capacity=100000)
        else:
            self.replay_buffer = ExperienceReplayBuffer(capacity=100000)
        
        # Q-networks (simplified - in practice, use neural networks)
        # For this implementation, we'll use a function approximation table
        self.q_network: Dict[Tuple, np.ndarray] = {}  # State -> Q-values for all actions
        self.target_network: Dict[Tuple, np.ndarray] = {}  # Target network
        
        # Training statistics
        self.training_stats = {
            "episodes": 0,
            "total_reward": 0.0,
            "average_reward": 0.0,
            "loss_history": [],
            "q_value_history": []
        }
    
    def get_state_key(self, state: np.ndarray) -> Tuple:
        """Convert state array to hashable tuple"""
        return tuple(np.round(state, decimals=2))
    
    def get_q_values(self, state: np.ndarray, network: str = "main") -> np.ndarray:
        """Get Q-values for all actions in a state"""
        state_key = self.get_state_key(state)
        
        if network == "main":
            if state_key not in self.q_network:
                self.q_network[state_key] = np.zeros(self.action_size)
            return self.q_network[state_key]
        else:  # target
            if state_key not in self.target_network:
                self.target_network[state_key] = np.zeros(self.action_size)
            return self.target_network[state_key]
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Select action using epsilon-greedy policy"""
        if training and np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        else:
            q_values = self.get_q_values(state, network="main")
            return np.argmax(q_values)
    
    def update_target_network(self):
        """Copy main network to target network"""
        self.target_network = {
            k: v.copy() for k, v in self.q_network.items()
        }
        logger.debug("Target network updated")
    
    def train_step(self, batch_size: int = 32) -> float:
        """Perform one training step"""
        if len(self.replay_buffer) < batch_size:
            return 0.0
        
        # Sample batch
        if isinstance(self.replay_buffer, PrioritizedExperienceReplay):
            experiences, indices, weights = self.replay_buffer.sample(batch_size)
            states = np.array([e.state for e in experiences])
            actions = np.array([e.action for e in experiences])
            rewards = np.array([e.reward for e in experiences])
            next_states = np.array([e.next_state for e in experiences])
            dones = np.array([e.done for e in experiences], dtype=np.float32)
        else:
            states, actions, rewards, next_states, dones = self.replay_buffer.sample_batch(batch_size)
            weights = np.ones(batch_size)
        
        # Compute target Q-values
        target_q_values = np.zeros(batch_size)
        td_errors = np.zeros(batch_size)
        
        for i in range(batch_size):
            current_q = self.get_q_values(states[i], network="main")[actions[i]]
            
            if dones[i]:
                target_q = rewards[i]
            else:
                next_q_values = self.get_q_values(next_states[i], network="target")
                target_q = rewards[i] + self.gamma * np.max(next_q_values)
            
            target_q_values[i] = target_q
            td_errors[i] = abs(target_q - current_q)
            
            # Update Q-value
            state_key = self.get_state_key(states[i])
            if state_key not in self.q_network:
                self.q_network[state_key] = np.zeros(self.action_size)
            
            # DQN update: Q(s,a) = Q(s,a) + α * (target - Q(s,a))
            self.q_network[state_key][actions[i]] = (
                current_q + self.learning_rate * (target_q - current_q)
            )
        
        # Update priorities if using prioritized replay
        if isinstance(self.replay_buffer, PrioritizedExperienceReplay):
            self.replay_buffer.update_priorities(indices, td_errors)
        
        # Calculate loss
        loss = np.mean(td_errors ** 2)
        self.training_stats["loss_history"].append(loss)
        
        # Update target network periodically
        self.update_counter += 1
        if self.update_counter % self.target_update_frequency == 0:
            self.update_target_network()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def train_from_replay(self, batch_size: int = 32, steps: int = 100):
        """Train using experience replay for multiple steps"""
        total_loss = 0.0
        
        for step in range(steps):
            loss = self.train_step(batch_size)
            total_loss += loss
        
        avg_loss = total_loss / steps if steps > 0 else 0.0
        logger.info(f"DQN Training - Steps: {steps}, Avg Loss: {avg_loss:.4f}, Epsilon: {self.epsilon:.4f}")
        
        return avg_loss
    
    def add_experience(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        td_error: Optional[float] = None
    ):
        """Add experience to replay buffer"""
        if isinstance(self.replay_buffer, PrioritizedExperienceReplay):
            self.replay_buffer.add(state, action, reward, next_state, done, td_error)
        else:
            self.replay_buffer.add(state, action, reward, next_state, done)
    
    def save_model(self, file_path: str):
        """Save DQN model to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "q_network": {str(k): v.tolist() for k, v in self.q_network.items()},
            "target_network": {str(k): v.tolist() for k, v in self.target_network.items()},
            "state_size": self.state_size,
            "action_size": self.action_size,
            "learning_rate": self.learning_rate,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "training_stats": self.training_stats
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Saved DQN model to {file_path}")
    
    def load_model(self, file_path: str):
        """Load DQN model from disk"""
        with open(file_path, 'r') as f:
            model_data = json.load(f)
        
        self.q_network = {
            eval(k): np.array(v) for k, v in model_data["q_network"].items()
        }
        self.target_network = {
            eval(k): np.array(v) for k, v in model_data["target_network"].items()
        }
        self.state_size = model_data["state_size"]
        self.action_size = model_data["action_size"]
        self.learning_rate = model_data["learning_rate"]
        self.gamma = model_data["gamma"]
        self.epsilon = model_data.get("epsilon", self.epsilon)
        self.training_stats = model_data.get("training_stats", self.training_stats)
        
        logger.info(f"Loaded DQN model from {file_path}")

