"""
Model Retrainer
Orchestrates retraining of RL and optimization models
"""

import logging
from typing import Dict, Optional, List
from pathlib import Path
import time

from .q_learning import QLearningTrainer
from .ppo_trainer import PPOTrainer
from .dqn_trainer import DQNTrainer
from .optimization_trainer import OptimizationTrainer
from ..continuous_learning.data_collector import DataCollector

logger = logging.getLogger(__name__)


class ModelRetrainer:
    """Orchestrates model retraining for all agents"""
    
    def __init__(
        self,
        data_collector: DataCollector,
        model_storage_path: str = "models/retrained"
    ):
        self.data_collector = data_collector
        self.model_storage_path = Path(model_storage_path)
        self.model_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Trainers for each agent
        self.trainers: Dict[str, any] = {}
        
        # Retraining configuration
        self.retraining_config = {
            "self-healing": {
                "algorithm": "ppo",  # or "q_learning", "dqn"
                "state_size": 10,
                "action_size": 5,
                "min_experiences": 1000
            },
            "scaling": {
                "algorithm": "q_learning",
                "state_size": 8,
                "action_size": 3,
                "min_experiences": 1000
            },
            "task-solving": {
                "algorithm": "dqn",
                "state_size": 12,
                "action_size": 10,
                "min_experiences": 2000
            },
            "optimization": {
                "algorithm": "optimization",
                "method": "gradient",  # or "evolutionary"
                "min_data_points": 500
            }
        }
    
    def initialize_trainer(self, agent_name: str):
        """Initialize trainer for an agent"""
        if agent_name not in self.retraining_config:
            logger.warning(f"No retraining config for agent: {agent_name}")
            return
        
        config = self.retraining_config[agent_name]
        
        if config["algorithm"] == "q_learning":
            trainer = QLearningTrainer(
                state_size=config["state_size"],
                action_size=config["action_size"]
            )
        elif config["algorithm"] == "ppo":
            trainer = PPOTrainer(
                state_size=config["state_size"],
                action_size=config["action_size"]
            )
        elif config["algorithm"] == "dqn":
            trainer = DQNTrainer(
                state_size=config["state_size"],
                action_size=config["action_size"]
            )
        elif config["algorithm"] == "optimization":
            trainer = OptimizationTrainer(
                use_evolutionary=(config.get("method") == "evolutionary")
            )
        else:
            logger.error(f"Unknown algorithm: {config['algorithm']}")
            return
        
        self.trainers[agent_name] = trainer
        logger.info(f"Initialized {config['algorithm']} trainer for {agent_name}")
    
    def check_retraining_ready(self, agent_name: str) -> bool:
        """Check if agent has enough data for retraining"""
        if agent_name not in self.retraining_config:
            return False
        
        config = self.retraining_config[agent_name]
        
        if config["algorithm"] == "optimization":
            # Check performance data points
            # This would need to be implemented based on your data structure
            return True  # Simplified
        else:
            # Check action experiences
            actions = self.data_collector.get_recent_actions(agent_name, limit=10000)
            return len(actions) >= config["min_experiences"]
    
    def retrain_agent(self, agent_name: str, batch_size: int = 32, epochs: int = 10):
        """Retrain model for an agent"""
        if agent_name not in self.trainers:
            self.initialize_trainer(agent_name)
        
        if agent_name not in self.trainers:
            logger.error(f"Failed to initialize trainer for {agent_name}")
            return False
        
        logger.info(f"Starting retraining for {agent_name}...")
        
        trainer = self.trainers[agent_name]
        config = self.retraining_config[agent_name]
        
        if config["algorithm"] == "optimization":
            # Train optimization model
            trainer.train(method=config.get("method", "gradient"), iterations=epochs * 10)
        else:
            # Get recent actions
            actions = self.data_collector.get_recent_actions(agent_name, limit=10000)
            
            if len(actions) < config["min_experiences"]:
                logger.warning(f"Insufficient data for {agent_name}: {len(actions)} < {config['min_experiences']}")
                return False
            
            # Convert actions to training format
            # This is simplified - in practice, you'd need proper state/action encoding
            experiences = self._convert_actions_to_experiences(actions, agent_name)
            
            # Train based on algorithm
            if config["algorithm"] == "q_learning":
                trainer.train_from_replay(batch_size=batch_size, epochs=epochs)
            elif config["algorithm"] == "ppo":
                # Train on episodes
                for _ in range(epochs):
                    # Group experiences into episodes (simplified)
                    episodes = self._group_into_episodes(experiences)
                    for episode in episodes:
                        trainer.train_episode(*episode)
            elif config["algorithm"] == "dqn":
                # Add experiences to replay buffer
                for exp in experiences:
                    trainer.add_experience(*exp)
                # Train
                trainer.train_from_replay(batch_size=batch_size, steps=epochs * 10)
        
        # Save model
        model_path = self.model_storage_path / f"{agent_name}_model.json"
        trainer.save_model(str(model_path))
        
        logger.info(f"Retraining completed for {agent_name}, model saved to {model_path}")
        return True
    
    def _convert_actions_to_experiences(self, actions: List[Dict], agent_name: str) -> List:
        """Convert action data to training experiences"""
        # Simplified conversion - in practice, you'd need proper state encoding
        experiences = []
        
        for i, action in enumerate(actions):
            # Extract state, action, reward, next_state, done
            # This is simplified - actual implementation would need proper encoding
            state = self._encode_state(action.get("input_data", {}))
            action_idx = self._encode_action(action.get("action_type", ""))
            reward = 10.0 if action.get("success") else -10.0
            next_state = state  # Simplified
            done = not action.get("success", False)
            
            experiences.append((state, action_idx, reward, next_state, done))
        
        return experiences
    
    def _encode_state(self, input_data: Dict) -> List[float]:
        """Encode input data to state vector"""
        # Simplified encoding - in practice, use proper feature engineering
        return [float(input_data.get("cpu_usage", 0.5)),
                float(input_data.get("memory_usage", 0.5)),
                float(input_data.get("error_rate", 0.0)),
                1.0 if input_data.get("healthy") else 0.0]
    
    def _encode_action(self, action_type: str) -> int:
        """Encode action type to action index"""
        action_map = {
            "restart_service": 0,
            "scale_up": 1,
            "scale_down": 2,
            "maintain": 3,
            "alert": 4
        }
        return action_map.get(action_type, 0)
    
    def _group_into_episodes(self, experiences: List) -> List:
        """Group experiences into episodes"""
        # Simplified - group consecutive experiences
        episodes = []
        current_episode = []
        
        for exp in experiences:
            current_episode.append(exp)
            if exp[4]:  # done
                episodes.append(current_episode)
                current_episode = []
        
        if current_episode:
            episodes.append(current_episode)
        
        return episodes
    
    def retrain_all_ready_agents(self):
        """Retrain all agents that are ready"""
        logger.info("Checking agents for retraining...")
        
        retrained = []
        for agent_name in self.retraining_config.keys():
            if self.check_retraining_ready(agent_name):
                if self.retrain_agent(agent_name):
                    retrained.append(agent_name)
        
        if retrained:
            logger.info(f"Retrained agents: {', '.join(retrained)}")
        else:
            logger.info("No agents ready for retraining")
        
        return retrained

