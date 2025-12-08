"""
RL Environment for Self-Healing Cloud System
Simulated environment using CPU load, error rate, pod crashes, network latency, service dependencies
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions the agent can take"""
    SCALE_UP = 0
    SCALE_DOWN = 1
    RESTART_POD = 2
    REBUILD_DEPLOYMENT = 3
    TRIGGER_HEAL = 4
    TRIGGER_CODE_FIX = 5
    DO_NOTHING = 6


class SystemState:
    """Represents the current state of the system with simplified state vector"""
    
    def __init__(self):
        # Core metrics for state vector: [cpu%, memory%, errors, latency, replicas, dependency_health]
        self.cpu_usage = 50.0  # CPU load percentage
        self.memory_usage = 50.0  # Memory usage percentage
        self.error_rate = 0.0  # Error rate (errors per second or percentage)
        self.network_latency = 50.0  # Network latency in milliseconds
        self.replicas = 2  # Number of replicas
        self.dependency_health = 1.0  # Dependency health score [0, 1]
        
        # Additional tracking metrics
        self.pod_crashes = 0  # Number of pod crashes
        self.uptime = 100.0  # Uptime percentage
        self.response_time = 200.0  # Average response time in ms
        self.recovery_time = 0.0  # Time to recover from failures
        self.cost = 0.0  # Current cost (normalized)
        
        # Failure indicators
        self.has_crash = False
        self.has_timeout = False
        self.has_resource_exhaustion = False
        
        # Service dependencies (simplified)
        self.dependencies = {}  # service_id -> health_score
    
    def to_array(self) -> np.ndarray:
        """
        Convert state to numpy array for neural network input
        State vector: [cpu%, memory%, errors, latency, replicas, dependency_health]
        """
        return np.array([
            self.cpu_usage,
            self.memory_usage,
            self.error_rate,
            self.network_latency,
            float(self.replicas),
            self.dependency_health
        ], dtype=np.float32)
    
    def normalize(self, state_array: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Normalize state array to [0, 1] range
        
        Args:
            state_array: Optional state array, if None uses current state
        
        Returns:
            Normalized state array
        """
        if state_array is None:
            state_array = self.to_array()
        
        # Normalization ranges
        max_values = np.array([
            100.0,  # cpu_usage (%)
            100.0,  # memory_usage (%)
            100.0,  # error_rate (errors/sec or %)
            1000.0, # network_latency (ms)
            20.0,   # replicas (max expected)
            1.0     # dependency_health [0, 1]
        ], dtype=np.float32)
        
        normalized = state_array / (max_values + 1e-8)  # Avoid division by zero
        return np.clip(normalized, 0.0, 1.0)
    
    def update_dependency_health(self, dependencies: Dict[str, float]):
        """
        Update dependency health based on dependent services
        
        Args:
            dependencies: Dictionary of service_id -> health_score [0, 1]
        """
        self.dependencies = dependencies
        if dependencies:
            self.dependency_health = np.mean(list(dependencies.values()))
        else:
            self.dependency_health = 1.0


class RLEnvironment:
    """
    Reinforcement Learning Environment
    
    Simulates cloud system with:
    - CPU load
    - Error rate
    - Pod crashes
    - Network latency
    - Service dependencies
    """
    
    def __init__(
        self,
        initial_state: Optional[SystemState] = None,
        max_steps: int = 1000,
        normalize_state: bool = True,
        synthetic_mode: bool = True
    ):
        self.current_state = initial_state or SystemState()
        self.initial_state = SystemState()
        self.max_steps = max_steps
        self.normalize_state = normalize_state
        self.synthetic_mode = synthetic_mode
        self.step_count = 0
        self.episode_count = 0
        
        # Action space
        self.action_space_size = len(ActionType)
        
        # State dimension: [cpu%, memory%, errors, latency, replicas, dependency_health]
        self.state_dim = 6
        
        # Track episode history
        self.episode_rewards = []
        self.episode_actions = []
        self.episode_metrics = []
        
        # Service dependencies (simulated)
        self.service_dependencies = {
            "compute-service": {"storage-service": 0.9, "logging-service": 0.8},
            "storage-service": {},
            "logging-service": {}
        }
        
        logger.info(f"RL Environment initialized: state_dim={self.state_dim}, action_space={self.action_space_size}")
    
    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        self.current_state = SystemState()
        self.step_count = 0
        self.episode_rewards = []
        self.episode_actions = []
        self.episode_metrics = []
        self.episode_count += 1
        
        # Initialize with some random variation
        self.current_state.cpu_usage = random.uniform(30, 70)
        self.current_state.memory_usage = random.uniform(30, 70)
        self.current_state.error_rate = random.uniform(0, 5)
        self.current_state.network_latency = random.uniform(20, 100)
        self.current_state.replicas = 2
        self.current_state.dependency_health = 1.0
        
        state = self.current_state.to_array()
        if self.normalize_state:
            state = self.current_state.normalize(state)
        
        logger.debug(f"Environment reset, episode {self.episode_count}")
        return state
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute action and return next state, reward, done, info
        
        Args:
            action: Action index to execute
        
        Returns:
            Tuple of (next_state, reward, done, info)
        """
        self.step_count += 1
        
        # Store previous state for reward calculation
        prev_state = SystemState()
        prev_state.__dict__.update(self.current_state.__dict__)
        
        # Execute action
        action_success = self._execute_action(action)
        
        # Update state based on system dynamics
        self._update_state_dynamics()
        
        # Calculate reward (will be computed by reward function)
        reward = 0.0  # Placeholder, actual reward computed by reward function
        
        # Check if episode is done
        done = self._is_done()
        
        # Get next state
        next_state = self.current_state.to_array()
        if self.normalize_state:
            next_state = self.current_state.normalize(next_state)
        
        # Update dependency health
        self._update_dependencies()
        
        # Info dictionary
        info = {
            'action': ActionType(action).name,
            'action_success': action_success,
            'step': self.step_count,
            'cpu_usage': self.current_state.cpu_usage,
            'error_rate': self.current_state.error_rate,
            'pod_crashes': self.current_state.pod_crashes,
            'latency': self.current_state.network_latency,
            'replicas': self.current_state.replicas,
            'dependency_health': self.current_state.dependency_health,
            'uptime': self.current_state.uptime,
            'response_time': self.current_state.response_time
        }
        
        self.episode_actions.append(action)
        self.episode_metrics.append(info.copy())
        
        logger.debug(f"Step {self.step_count}: Action={ActionType(action).name}, CPU={self.current_state.cpu_usage:.1f}%, Errors={self.current_state.error_rate:.2f}")
        
        return next_state, reward, done, info
    
    def _execute_action(self, action: int) -> bool:
        """
        Execute action and update system state
        
        Args:
            action: Action index
        
        Returns:
            Whether action was successful
        """
        action_type = ActionType(action)
        success = True
        
        if action_type == ActionType.SCALE_UP:
            if self.current_state.replicas < 20:
                self.current_state.replicas += 1
                # Reduce CPU and memory load
                self.current_state.cpu_usage = max(0, self.current_state.cpu_usage - 10)
                self.current_state.memory_usage = max(0, self.current_state.memory_usage - 10)
                self.current_state.cost += 0.1  # Cost increases
            else:
                success = False
        
        elif action_type == ActionType.SCALE_DOWN:
            if self.current_state.replicas > 1:
                self.current_state.replicas -= 1
                # Increase CPU and memory load
                self.current_state.cpu_usage = min(100, self.current_state.cpu_usage + 10)
                self.current_state.memory_usage = min(100, self.current_state.memory_usage + 10)
                self.current_state.cost -= 0.1  # Cost decreases
            else:
                success = False
        
        elif action_type == ActionType.RESTART_POD:
            if self.current_state.pod_crashes > 0:
                self.current_state.pod_crashes = max(0, self.current_state.pod_crashes - 1)
                self.current_state.has_crash = False
                self.current_state.recovery_time = 5.0  # Recovery time in seconds
            else:
                success = False
        
        elif action_type == ActionType.REBUILD_DEPLOYMENT:
            # Rebuild fixes crashes and reduces errors
            self.current_state.pod_crashes = 0
            self.current_state.error_rate = max(0, self.current_state.error_rate * 0.5)
            self.current_state.has_crash = False
            self.current_state.recovery_time = 30.0  # Longer recovery time
            self.current_state.cost += 0.2  # Rebuild costs more
        
        elif action_type == ActionType.TRIGGER_HEAL:
            # Generic healing action
            if self.current_state.has_crash or self.current_state.error_rate > 10:
                self.current_state.pod_crashes = max(0, self.current_state.pod_crashes - 1)
                self.current_state.error_rate = max(0, self.current_state.error_rate * 0.7)
                self.current_state.has_crash = False
                self.current_state.recovery_time = 10.0
            else:
                success = False
        
        elif action_type == ActionType.TRIGGER_CODE_FIX:
            # Code fix reduces errors significantly
            self.current_state.error_rate = max(0, self.current_state.error_rate * 0.3)
            self.current_state.recovery_time = 60.0  # Code fix takes longer
            self.current_state.cost += 0.3  # Code fix is expensive
        
        elif action_type == ActionType.DO_NOTHING:
            # No action taken
            pass
        
        return success
    
    def _update_state_dynamics(self):
        """Update system state based on natural dynamics"""
        # CPU and memory fluctuate
        self.current_state.cpu_usage += np.random.normal(0, 2)
        self.current_state.cpu_usage = np.clip(self.current_state.cpu_usage, 0, 100)
        
        self.current_state.memory_usage += np.random.normal(0, 1.5)
        self.current_state.memory_usage = np.clip(self.current_state.memory_usage, 0, 100)
        
        # Random pod crashes (10% chance per step)
        if random.random() < 0.1:
            self.current_state.pod_crashes += 1
            self.current_state.has_crash = True
            self.current_state.error_rate += 5
            self.current_state.uptime = max(0, self.current_state.uptime - 2)
        
        # Error rate changes
        if self.current_state.has_crash:
            self.current_state.error_rate = min(100, self.current_state.error_rate + 2)
        else:
            self.current_state.error_rate = max(0, self.current_state.error_rate - 0.5)
        
        # Network latency fluctuates
        self.current_state.network_latency += np.random.normal(0, 5)
        self.current_state.network_latency = np.clip(self.current_state.network_latency, 10, 1000)
        
        # Response time correlates with CPU and latency
        self.current_state.response_time = (
            self.current_state.cpu_usage * 2 + 
            self.current_state.network_latency * 0.5
        )
        
        # Recovery time decreases
        if self.current_state.recovery_time > 0:
            self.current_state.recovery_time = max(0, self.current_state.recovery_time - 1)
        
        # Uptime improves if no crashes
        if not self.current_state.has_crash and self.current_state.error_rate < 5:
            self.current_state.uptime = min(100, self.current_state.uptime + 0.1)
    
    def _update_dependencies(self):
        """Update dependency health based on service dependencies"""
        # Simulate dependency health based on system state
        base_health = 1.0
        
        # Reduce health if errors are high
        if self.current_state.error_rate > 10:
            base_health -= 0.2
        
        # Reduce health if latency is high
        if self.current_state.network_latency > 200:
            base_health -= 0.1
        
        # Reduce health if crashes exist
        if self.current_state.pod_crashes > 0:
            base_health -= 0.3
        
        # Add some noise
        base_health += np.random.normal(0, 0.05)
        self.current_state.dependency_health = np.clip(base_health, 0.0, 1.0)
        
        # Update dependencies dictionary
        for service_id in self.service_dependencies.keys():
            self.current_state.dependencies[service_id] = self.current_state.dependency_health
    
    def _is_done(self) -> bool:
        """Check if episode is done"""
        # Episode ends if:
        # 1. Max steps reached
        if self.step_count >= self.max_steps:
            return True
        
        # 2. System is stable for many steps
        if (self.step_count > 50 and 
            not self.current_state.has_crash and 
            self.current_state.error_rate < 1 and
            self.current_state.cpu_usage < 80 and
            self.current_state.memory_usage < 80):
            return True
        
        # 3. System is completely broken
        if (self.current_state.pod_crashes > 5 or
            self.current_state.error_rate > 90 or
            self.current_state.uptime < 10):
            return True
        
        return False
    
    def get_state(self) -> np.ndarray:
        """Get current state"""
        state = self.current_state.to_array()
        if self.normalize_state:
            state = self.current_state.normalize(state)
        return state
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get current state as dictionary"""
        return {
            'cpu_usage': self.current_state.cpu_usage,
            'memory_usage': self.current_state.memory_usage,
            'error_rate': self.current_state.error_rate,
            'network_latency': self.current_state.network_latency,
            'replicas': self.current_state.replicas,
            'dependency_health': self.current_state.dependency_health,
            'pod_crashes': self.current_state.pod_crashes,
            'uptime': self.current_state.uptime,
            'response_time': self.current_state.response_time,
            'recovery_time': self.current_state.recovery_time,
            'cost': self.current_state.cost,
            'has_crash': self.current_state.has_crash
        }
    
    def set_state(self, state: SystemState):
        """Set environment state (for testing/simulation)"""
        self.current_state = state
    
    def inject_failure(self, failure_type: str):
        """Inject a failure for testing"""
        if failure_type == "crash":
            self.current_state.pod_crashes += 1
            self.current_state.has_crash = True
            self.current_state.error_rate += 10
        elif failure_type == "high_cpu":
            self.current_state.cpu_usage = 95
            self.current_state.has_resource_exhaustion = True
        elif failure_type == "high_latency":
            self.current_state.network_latency = 500
        elif failure_type == "high_errors":
            self.current_state.error_rate = 50
    
    def get_episode_statistics(self) -> Dict:
        """Get statistics for current episode"""
        return {
            'episode': self.episode_count,
            'steps': self.step_count,
            'total_reward': sum(self.episode_rewards),
            'avg_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0,
            'actions_taken': len(self.episode_actions),
            'final_cpu': self.current_state.cpu_usage,
            'final_errors': self.current_state.error_rate,
            'final_uptime': self.current_state.uptime,
            'final_cost': self.current_state.cost,
            'action_distribution': {ActionType(i).name: self.episode_actions.count(i) 
                                   for i in range(self.action_space_size)}
        }
