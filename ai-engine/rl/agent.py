"""
Reinforcement Learning Agent
Implements a Deep Q-Network (DQN) agent for learning optimal healing and scaling strategies
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DQNNetwork(nn.Module):
    """Deep Q-Network for action-value estimation"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [128, 128, 64]):
        super(DQNNetwork, self).__init__()
        
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        return self.network(state)


class RLAgent:
    """
    Reinforcement Learning Agent for Self-Healing and Scaling
    
    Uses Deep Q-Learning to learn optimal actions based on system state
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        learning_rate: float = 0.001,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_size: int = 10000,
        batch_size: int = 64,
        target_update_freq: int = 100,
        device: str = "cpu"
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.device = torch.device(device)
        
        # Neural networks
        self.q_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.target_network = DQNNetwork(state_dim, action_dim).to(self.device)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Initialize target network with same weights
        self.update_target_network()
        
        # Experience replay buffer
        self.memory = deque(maxlen=memory_size)
        
        # Training statistics
        self.training_step = 0
        self.loss_history = []
        
        logger.info(f"RL Agent initialized: state_dim={state_dim}, action_dim={action_dim}")
    
    def choose_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Choose action using epsilon-greedy policy
        
        Args:
            state: Current system state
            training: Whether in training mode (uses epsilon-greedy)
        
        Returns:
            Selected action index
        """
        if training and random.random() < self.epsilon:
            # Exploration: random action
            action = random.randrange(self.action_dim)
            logger.debug(f"Random action selected: {action}")
            return action
        
        # Exploitation: select best action
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax().item()
            logger.debug(f"Greedy action selected: {action}, Q-value: {q_values.max().item():.4f}")
            return action
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """Alias for choose_action for backward compatibility"""
        return self.choose_action(state, training)
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                 next_state: np.ndarray, done: bool):
        """
        Store experience in replay buffer
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def update_policy(self) -> Optional[float]:
        """
        Update policy by training on a batch of experiences
        
        Returns:
            Loss value if training occurred, None otherwise
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # Current Q values
        q_values = self.q_network(states)
        q_value = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states)
            next_q_value = next_q_values.max(1)[0]
            target_q_value = rewards + (self.gamma * next_q_value * ~dones)
        
        # Compute loss
        loss = nn.MSELoss()(q_value, target_q_value)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        # Update epsilon
        if self.epsilon > self.epsilon_end:
            self.epsilon *= self.epsilon_decay
        
        # Update target network periodically
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.update_target_network()
        
        loss_value = loss.item()
        self.loss_history.append(loss_value)
        
        logger.debug(f"Policy updated: step {self.training_step}, Loss: {loss_value:.4f}, Epsilon: {self.epsilon:.4f}")
        
        return loss_value
    
    def replay(self) -> Optional[float]:
        """Alias for update_policy for backward compatibility"""
        return self.update_policy()
    
    def update_target_network(self):
        """Copy weights from main network to target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())
        logger.debug("Target network updated")
    
    def predict(self, state: np.ndarray) -> Tuple[int, float]:
        """
        Predict best action and confidence
        
        Args:
            state: Current system state
        
        Returns:
            Tuple of (action, confidence/Q-value)
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax().item()
            confidence = q_values.max().item()
            
            return action, confidence
    
    def get_action_confidence(self, state: np.ndarray, action: int) -> float:
        """
        Get confidence/Q-value for a specific action
        
        Args:
            state: Current system state
            action: Action index
        
        Returns:
            Q-value (confidence) for the action
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values[0][action].item()
    
    def save_checkpoint(self, filepath: str):
        """
        Save agent checkpoint
        
        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'loss_history': self.loss_history,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma
        }
        torch.save(checkpoint, filepath)
        logger.info(f"Checkpoint saved to {filepath}")
    
    def load_checkpoint(self, filepath: str):
        """
        Load agent checkpoint
        
        Args:
            filepath: Path to load checkpoint from
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon_end)
        self.training_step = checkpoint.get('training_step', 0)
        self.loss_history = checkpoint.get('loss_history', [])
        logger.info(f"Checkpoint loaded from {filepath}")
    
    def save(self, filepath: str):
        """Alias for save_checkpoint for backward compatibility"""
        self.save_checkpoint(filepath)
    
    def load(self, filepath: str):
        """Alias for load_checkpoint for backward compatibility"""
        self.load_checkpoint(filepath)
    
    def get_statistics(self) -> Dict:
        """Get training statistics"""
        return {
            'epsilon': self.epsilon,
            'training_steps': self.training_step,
            'memory_size': len(self.memory),
            'avg_loss': np.mean(self.loss_history[-100:]) if self.loss_history else 0.0,
            'recent_losses': self.loss_history[-10:] if self.loss_history else []
        }

