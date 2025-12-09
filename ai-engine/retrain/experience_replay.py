"""
Experience Replay Buffer for RL Model Retraining
Stores and samples past decisions and outcomes for training
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from collections import deque
import random
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Experience:
    """Single experience tuple (state, action, reward, next_state, done)"""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    info: Dict[str, Any]


class ExperienceReplayBuffer:
    """Experience replay buffer for storing and sampling experiences"""
    
    def __init__(self, capacity: int = 100000):
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self.position = 0
    
    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        info: Optional[Dict[str, Any]] = None
    ):
        """Add experience to buffer"""
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            info=info or {}
        )
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample a batch of experiences"""
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(self.buffer, batch_size)
    
    def sample_batch(
        self,
        batch_size: int
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Sample a batch and return as numpy arrays"""
        experiences = self.sample(batch_size)
        
        states = np.array([e.state for e in experiences])
        actions = np.array([e.action for e in experiences])
        rewards = np.array([e.reward for e in experiences])
        next_states = np.array([e.next_state for e in experiences])
        dones = np.array([e.done for e in experiences], dtype=np.float32)
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self) -> int:
        return len(self.buffer)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer.clear()
    
    def save(self, file_path: str):
        """Save buffer to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(list(self.buffer), f)
        
        logger.info(f"Saved {len(self.buffer)} experiences to {file_path}")
    
    def load(self, file_path: str):
        """Load buffer from disk"""
        with open(file_path, 'rb') as f:
            experiences = pickle.load(f)
        
        self.buffer.clear()
        self.buffer.extend(experiences)
        
        logger.info(f"Loaded {len(self.buffer)} experiences from {file_path}")


class PrioritizedExperienceReplay:
    """Prioritized Experience Replay (PER) for importance sampling"""
    
    def __init__(self, capacity: int = 100000, alpha: float = 0.6, beta: float = 0.4):
        self.capacity = capacity
        self.alpha = alpha  # Prioritization exponent
        self.beta = beta    # Importance sampling exponent
        self.beta_increment = 0.001
        
        self.buffer: deque = deque(maxlen=capacity)
        self.priorities: deque = deque(maxlen=capacity)
        self.max_priority = 1.0
    
    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        td_error: Optional[float] = None,
        info: Optional[Dict[str, Any]] = None
    ):
        """Add experience with priority"""
        experience = Experience(
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            info=info or {}
        )
        
        # Priority based on TD error if available, else use max priority
        priority = abs(td_error) ** self.alpha if td_error is not None else self.max_priority
        priority = max(priority, 1e-6)  # Ensure non-zero
        
        self.buffer.append(experience)
        self.priorities.append(priority)
    
    def sample(self, batch_size: int) -> Tuple[List[Experience], np.ndarray, np.ndarray]:
        """Sample a batch with importance sampling weights"""
        if len(self.buffer) < batch_size:
            indices = list(range(len(self.buffer)))
            experiences = list(self.buffer)
        else:
            # Calculate sampling probabilities
            priorities = np.array(self.priorities)
            probabilities = priorities / priorities.sum()
            
            # Sample indices
            indices = np.random.choice(len(self.buffer), batch_size, p=probabilities)
            experiences = [self.buffer[i] for i in indices]
        
        # Calculate importance sampling weights
        priorities = np.array([self.priorities[i] for i in indices])
        probabilities = priorities / np.array(self.priorities).sum()
        weights = (len(self.buffer) * probabilities) ** (-self.beta)
        weights = weights / weights.max()  # Normalize
        
        # Update beta
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        return experiences, indices, weights
    
    def update_priorities(self, indices: np.ndarray, td_errors: np.ndarray):
        """Update priorities based on TD errors"""
        for idx, td_error in zip(indices, td_errors):
            priority = abs(td_error) ** self.alpha
            priority = max(priority, 1e-6)
            
            if idx < len(self.priorities):
                self.priorities[idx] = priority
                self.max_priority = max(self.max_priority, priority)
    
    def __len__(self) -> int:
        return len(self.buffer)

