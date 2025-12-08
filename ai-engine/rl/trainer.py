"""
RL Trainer
Trains RL agent using synthetic simulation + metrics from Phase 4
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging
from pathlib import Path
import json
import os

from .agent import RLAgent
from .environment import RLEnvironment, SystemState
from .reward_functions import RewardFunction, RewardFunctionFactory, RewardType

logger = logging.getLogger(__name__)


class RLTrainer:
    """
    Trainer for RL Agent
    
    Handles:
    - Training loop with synthetic simulation
    - Integration with Phase 4 metrics
    - Episode management
    - Model checkpointing
    - Performance tracking
    """
    
    def __init__(
        self,
        agent: RLAgent,
        environment: RLEnvironment,
        reward_function: Optional[RewardFunction] = None,
        checkpoint_dir: str = "./checkpoints",
        log_interval: int = 100,
        use_phase4_metrics: bool = False,
        phase4_metrics_path: Optional[str] = None
    ):
        self.agent = agent
        self.environment = environment
        self.reward_function = reward_function or RewardFunctionFactory.create(RewardType.BALANCED)
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.log_interval = log_interval
        self.use_phase4_metrics = use_phase4_metrics
        self.phase4_metrics_path = phase4_metrics_path
        
        # Phase 4 metrics integration
        self.phase4_metrics = []
        if use_phase4_metrics and phase4_metrics_path:
            self._load_phase4_metrics(phase4_metrics_path)
        
        # Training statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.training_losses = []
        self.episode_count = 0
        
        logger.info(f"RL Trainer initialized: use_phase4_metrics={use_phase4_metrics}")
    
    def _load_phase4_metrics(self, metrics_path: str):
        """
        Load metrics from Phase 4 cloud simulation
        
        Args:
            metrics_path: Path to metrics file or directory
        """
        try:
            if os.path.isdir(metrics_path):
                # Load from directory (e.g., Prometheus metrics)
                logger.info(f"Loading Phase 4 metrics from directory: {metrics_path}")
                # In practice, this would parse Prometheus metrics
                # For now, we'll use a placeholder
                self.phase4_metrics = self._parse_metrics_directory(metrics_path)
            elif os.path.isfile(metrics_path):
                # Load from JSON file
                logger.info(f"Loading Phase 4 metrics from file: {metrics_path}")
                with open(metrics_path, 'r') as f:
                    data = json.load(f)
                    self.phase4_metrics = data.get('metrics', [])
            else:
                logger.warning(f"Phase 4 metrics path not found: {metrics_path}")
                self.phase4_metrics = []
        except Exception as e:
            logger.error(f"Failed to load Phase 4 metrics: {e}")
            self.phase4_metrics = []
    
    def _parse_metrics_directory(self, metrics_dir: str) -> List[Dict]:
        """
        Parse metrics from directory (e.g., Prometheus export)
        
        Args:
            metrics_dir: Directory containing metrics
        
        Returns:
            List of metric dictionaries
        """
        # Placeholder implementation
        # In practice, this would parse Prometheus metrics format
        metrics = []
        
        # Look for common metric files
        metric_files = ['cpu_metrics.json', 'memory_metrics.json', 'error_metrics.json']
        for metric_file in metric_files:
            filepath = os.path.join(metrics_dir, metric_file)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        metrics.extend(data.get('data', []))
                except Exception as e:
                    logger.warning(f"Failed to load {metric_file}: {e}")
        
        return metrics
    
    def _convert_phase4_metrics_to_state(self, metrics: Dict[str, Any]) -> SystemState:
        """
        Convert Phase 4 metrics to SystemState
        
        Args:
            metrics: Metrics dictionary from Phase 4
        
        Returns:
            SystemState object
        """
        state = SystemState()
        
        # Map Phase 4 metrics to state
        state.cpu_usage = metrics.get('cpu_usage', metrics.get('cpu', 50.0))
        state.memory_usage = metrics.get('memory_usage', metrics.get('memory', 50.0))
        state.error_rate = metrics.get('error_rate', metrics.get('errors', 0.0))
        state.network_latency = metrics.get('network_latency', metrics.get('latency', 50.0))
        state.replicas = metrics.get('replicas', metrics.get('pod_count', 2))
        state.dependency_health = metrics.get('dependency_health', 1.0)
        
        # Additional metrics
        state.pod_crashes = metrics.get('pod_crashes', 0)
        state.uptime = metrics.get('uptime', 100.0)
        state.response_time = metrics.get('response_time', 200.0)
        state.cost = metrics.get('cost', 0.0)
        state.has_crash = metrics.get('has_crash', False)
        
        return state
    
    def train(self, num_episodes: int, max_steps_per_episode: int = 1000, 
              use_synthetic: bool = True, use_phase4: bool = False) -> Dict:
        """
        Train the agent
        
        Args:
            num_episodes: Number of training episodes
            max_steps_per_episode: Maximum steps per episode
            use_synthetic: Whether to use synthetic simulation
            use_phase4: Whether to use Phase 4 metrics
        
        Returns:
            Training statistics
        """
        logger.info(f"Starting training for {num_episodes} episodes")
        logger.info(f"use_synthetic={use_synthetic}, use_phase4={use_phase4}")
        
        for episode in range(num_episodes):
            # Alternate between synthetic and Phase 4 if both enabled
            if use_synthetic and use_phase4:
                use_phase4_this_episode = (episode % 2 == 1)
            else:
                use_phase4_this_episode = use_phase4
            
            if use_phase4_this_episode and self.phase4_metrics:
                episode_reward, episode_length, episode_loss = self._train_episode_phase4(max_steps_per_episode)
            else:
                episode_reward, episode_length, episode_loss = self._train_episode(max_steps_per_episode)
            
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(episode_length)
            if episode_loss is not None:
                self.training_losses.append(episode_loss)
            
            self.episode_count += 1
            
            # Logging
            if (episode + 1) % self.log_interval == 0:
                self._log_progress(episode + 1)
            
            # Checkpointing
            if (episode + 1) % (self.log_interval * 5) == 0:
                self._save_checkpoint(episode + 1)
        
        # Final checkpoint
        self._save_checkpoint(num_episodes, final=True)
        
        return self._get_training_statistics()
    
    def _train_episode(self, max_steps: int) -> Tuple[float, int, Optional[float]]:
        """
        Train for one episode using synthetic simulation
        
        Args:
            max_steps: Maximum steps in episode
        
        Returns:
            Tuple of (total_reward, episode_length, avg_loss)
        """
        state = self.environment.reset()
        total_reward = 0.0
        episode_losses = []
        
        for step in range(max_steps):
            # Select action
            action = self.agent.choose_action(state, training=True)
            
            # Execute action
            next_state, env_reward, done, info = self.environment.step(action)
            
            # Compute reward using reward function
            state_dict = self.environment.get_state_dict()
            next_state_dict = self.environment.get_state_dict()
            reward = self.reward_function.compute(state_dict, action, next_state_dict, done)
            
            # Store experience
            self.agent.remember(state, action, reward, next_state, done)
            
            # Update policy
            loss = self.agent.update_policy()
            if loss is not None:
                episode_losses.append(loss)
            
            total_reward += reward
            state = next_state
            
            if done:
                break
        
        avg_loss = np.mean(episode_losses) if episode_losses else None
        
        return total_reward, step + 1, avg_loss
    
    def _train_episode_phase4(self, max_steps: int) -> Tuple[float, int, Optional[float]]:
        """
        Train for one episode using Phase 4 metrics
        
        Args:
            max_steps: Maximum steps in episode
        
        Returns:
            Tuple of (total_reward, episode_length, avg_loss)
        """
        if not self.phase4_metrics:
            logger.warning("No Phase 4 metrics available, falling back to synthetic")
            return self._train_episode(max_steps)
        
        # Select a random starting point in metrics
        start_idx = np.random.randint(0, max(1, len(self.phase4_metrics) - max_steps))
        metrics_sequence = self.phase4_metrics[start_idx:start_idx + max_steps]
        
        total_reward = 0.0
        episode_losses = []
        
        # Initialize state from first metric
        if metrics_sequence:
            initial_state_obj = self._convert_phase4_metrics_to_state(metrics_sequence[0])
            self.environment.set_state(initial_state_obj)
            state = self.environment.get_state()
        else:
            state = self.environment.reset()
        
        for step, metrics in enumerate(metrics_sequence):
            if step >= max_steps:
                break
            
            # Select action
            action = self.agent.choose_action(state, training=True)
            
            # Update environment state from metrics
            state_obj = self._convert_phase4_metrics_to_state(metrics)
            self.environment.set_state(state_obj)
            
            # Simulate action effect
            self.environment._execute_action(action)
            self.environment._update_state_dynamics()
            
            # Get next state
            next_state = self.environment.get_state()
            next_state_dict = self.environment.get_state_dict()
            
            # Compute reward
            state_dict = self.environment.get_state_dict()
            reward = self.reward_function.compute(state_dict, action, next_state_dict, False)
            
            # Store experience
            self.agent.remember(state, action, reward, next_state, False)
            
            # Update policy
            loss = self.agent.update_policy()
            if loss is not None:
                episode_losses.append(loss)
            
            total_reward += reward
            state = next_state
        
        avg_loss = np.mean(episode_losses) if episode_losses else None
        
        return total_reward, len(metrics_sequence), avg_loss
    
    def _log_progress(self, episode: int):
        """Log training progress"""
        recent_rewards = self.episode_rewards[-self.log_interval:]
        recent_lengths = self.episode_lengths[-self.log_interval:]
        
        avg_reward = np.mean(recent_rewards)
        avg_length = np.mean(recent_lengths)
        avg_loss = np.mean(self.training_losses[-self.log_interval:]) if self.training_losses else 0.0
        
        logger.info(
            f"Episode {episode} | "
            f"Avg Reward: {avg_reward:.2f} | "
            f"Avg Length: {avg_length:.1f} | "
            f"Avg Loss: {avg_loss:.4f} | "
            f"Epsilon: {self.agent.epsilon:.4f}"
        )
    
    def _save_checkpoint(self, episode: int, final: bool = False):
        """Save training checkpoint"""
        suffix = "_final" if final else f"_ep{episode}"
        checkpoint_path = self.checkpoint_dir / f"agent{suffix}.pth"
        stats_path = self.checkpoint_dir / f"stats{suffix}.json"
        
        # Save agent
        self.agent.save_checkpoint(str(checkpoint_path))
        
        # Save statistics
        stats = self._get_training_statistics()
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def _get_training_statistics(self) -> Dict:
        """Get training statistics"""
        return {
            'episode_count': self.episode_count,
            'total_episodes': len(self.episode_rewards),
            'avg_reward': float(np.mean(self.episode_rewards)) if self.episode_rewards else 0.0,
            'std_reward': float(np.std(self.episode_rewards)) if self.episode_rewards else 0.0,
            'max_reward': float(np.max(self.episode_rewards)) if self.episode_rewards else 0.0,
            'min_reward': float(np.min(self.episode_rewards)) if self.episode_rewards else 0.0,
            'avg_episode_length': float(np.mean(self.episode_lengths)) if self.episode_lengths else 0.0,
            'avg_loss': float(np.mean(self.training_losses)) if self.training_losses else 0.0,
            'agent_stats': self.agent.get_statistics(),
            'phase4_metrics_used': self.use_phase4_metrics and len(self.phase4_metrics) > 0
        }
    
    def evaluate(self, num_episodes: int = 10) -> Dict:
        """
        Evaluate agent performance
        
        Args:
            num_episodes: Number of evaluation episodes
        
        Returns:
            Evaluation statistics
        """
        logger.info(f"Evaluating agent for {num_episodes} episodes")
        
        eval_rewards = []
        eval_lengths = []
        
        for episode in range(num_episodes):
            state = self.environment.reset()
            total_reward = 0.0
            steps = 0
            
            while steps < self.environment.max_steps:
                action = self.agent.choose_action(state, training=False)
                next_state, reward, done, info = self.environment.step(action)
                
                # Compute reward using reward function
                state_dict = self.environment.get_state_dict()
                next_state_dict = self.environment.get_state_dict()
                computed_reward = self.reward_function.compute(state_dict, action, next_state_dict, done)
                
                total_reward += computed_reward
                state = next_state
                steps += 1
                
                if done:
                    break
            
            eval_rewards.append(total_reward)
            eval_lengths.append(steps)
        
        stats = {
            'num_episodes': num_episodes,
            'avg_reward': float(np.mean(eval_rewards)),
            'std_reward': float(np.std(eval_rewards)),
            'avg_length': float(np.mean(eval_lengths)),
            'success_rate': float(sum(1 for r in eval_rewards if r > 0) / len(eval_rewards))
        }
        
        logger.info(f"Evaluation complete: Avg Reward={stats['avg_reward']:.2f}, Success Rate={stats['success_rate']:.2%}")
        
        return stats
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load training checkpoint"""
        self.agent.load_checkpoint(checkpoint_path)
        logger.info(f"Checkpoint loaded from {checkpoint_path}")
