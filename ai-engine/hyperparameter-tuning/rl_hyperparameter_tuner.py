"""
RL Model Hyperparameter Tuning
Specialized tuner for Reinforcement Learning models
"""

import time
import logging
from typing import Dict, List, Optional, Callable
from pathlib import Path
import json

from .hyperparameter_tuner import (
    HyperparameterTuner,
    HyperparameterSpace,
    TuningResult,
    RandomSearchTuner,
    GridSearchTuner,
    BayesianOptimizationTuner
)

logger = logging.getLogger(__name__)


class RLHyperparameterTuner:
    """Hyperparameter tuner for RL models"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Default search spaces for different RL algorithms
        self.search_spaces = {
            "q_learning": {
                "learning_rate": HyperparameterSpace(
                    name="learning_rate",
                    param_type="float",
                    min_value=0.001,
                    max_value=0.1,
                    log_scale=True
                ),
                "discount_factor": HyperparameterSpace(
                    name="discount_factor",
                    param_type="float",
                    min_value=0.8,
                    max_value=0.99
                ),
                "epsilon": HyperparameterSpace(
                    name="epsilon",
                    param_type="float",
                    min_value=0.01,
                    max_value=1.0
                ),
                "epsilon_decay": HyperparameterSpace(
                    name="epsilon_decay",
                    param_type="float",
                    min_value=0.9,
                    max_value=0.999
                )
            },
            "ppo": {
                "learning_rate": HyperparameterSpace(
                    name="learning_rate",
                    param_type="float",
                    min_value=1e-5,
                    max_value=1e-2,
                    log_scale=True
                ),
                "gamma": HyperparameterSpace(
                    name="gamma",
                    param_type="float",
                    min_value=0.9,
                    max_value=0.999
                ),
                "gae_lambda": HyperparameterSpace(
                    name="gae_lambda",
                    param_type="float",
                    min_value=0.8,
                    max_value=0.99
                ),
                "clip_epsilon": HyperparameterSpace(
                    name="clip_epsilon",
                    param_type="float",
                    min_value=0.1,
                    max_value=0.3
                ),
                "value_coef": HyperparameterSpace(
                    name="value_coef",
                    param_type="float",
                    min_value=0.1,
                    max_value=1.0
                ),
                "entropy_coef": HyperparameterSpace(
                    name="entropy_coef",
                    param_type="float",
                    min_value=0.001,
                    max_value=0.1,
                    log_scale=True
                )
            },
            "dqn": {
                "learning_rate": HyperparameterSpace(
                    name="learning_rate",
                    param_type="float",
                    min_value=1e-5,
                    max_value=1e-2,
                    log_scale=True
                ),
                "gamma": HyperparameterSpace(
                    name="gamma",
                    param_type="float",
                    min_value=0.9,
                    max_value=0.99
                ),
                "epsilon": HyperparameterSpace(
                    name="epsilon",
                    param_type="float",
                    min_value=0.01,
                    max_value=1.0
                ),
                "epsilon_decay": HyperparameterSpace(
                    name="epsilon_decay",
                    param_type="float",
                    min_value=0.9,
                    max_value=0.999
                ),
                "target_update_frequency": HyperparameterSpace(
                    name="target_update_frequency",
                    param_type="int",
                    min_value=10,
                    max_value=1000
                )
            }
        }
    
    def get_search_space(self, algorithm: str) -> Dict[str, HyperparameterSpace]:
        """Get search space for an algorithm"""
        if algorithm not in self.search_spaces:
            logger.warning(f"Unknown algorithm {algorithm}, using default search space")
            return self.search_spaces["q_learning"]
        
        return self.search_spaces[algorithm]
    
    def tune_rl_model(
        self,
        algorithm: str,
        objective_function: Callable[[Dict[str, Any]], float],
        method: str = "bayesian",
        n_trials: int = 100,
        maximize: bool = True
    ) -> TuningResult:
        """Tune hyperparameters for an RL model"""
        logger.info(f"Tuning {algorithm} hyperparameters for {self.agent_name}...")
        
        search_space = self.get_search_space(algorithm)
        
        # Select tuning method
        if method == "bayesian":
            tuner = BayesianOptimizationTuner(
                search_space=search_space,
                objective_function=objective_function,
                maximize=maximize,
                n_trials=n_trials
            )
        elif method == "random":
            tuner = RandomSearchTuner(
                search_space=search_space,
                objective_function=objective_function,
                maximize=maximize,
                n_trials=n_trials
            )
        elif method == "grid":
            tuner = GridSearchTuner(
                search_space=search_space,
                objective_function=objective_function,
                maximize=maximize,
                grid_size=5
            )
        else:
            raise ValueError(f"Unknown tuning method: {method}")
        
        # Run tuning
        result = tuner.tune()
        
        # Save results
        timestamp = int(time.time())
        result_file = Path("data/hyperparameter-tuning") / f"{self.agent_name}_{algorithm}_{method}_{timestamp}.json"
        tuner.save_results(result, str(result_file))
        
        return result


class OptimizationAgentHyperparameterTuner:
    """Hyperparameter tuner for Optimization Agent"""
    
    def __init__(self):
        # Search space for optimization agent
        self.search_space = {
            "cpu_weight": HyperparameterSpace(
                name="cpu_weight",
                param_type="float",
                min_value=0.5,
                max_value=2.0
            ),
            "memory_weight": HyperparameterSpace(
                name="memory_weight",
                param_type="float",
                min_value=0.5,
                max_value=2.0
            ),
            "response_time_weight": HyperparameterSpace(
                name="response_time_weight",
                param_type="float",
                min_value=0.1,
                max_value=1.0
            ),
            "over_provision_penalty": HyperparameterSpace(
                name="over_provision_penalty",
                param_type="float",
                min_value=1.0,
                max_value=3.0
            ),
            "under_provision_penalty": HyperparameterSpace(
                name="under_provision_penalty",
                param_type="float",
                min_value=2.0,
                max_value=5.0
            ),
            "scale_up_cpu_threshold": HyperparameterSpace(
                name="scale_up_cpu_threshold",
                param_type="float",
                min_value=0.6,
                max_value=0.9
            ),
            "scale_down_cpu_threshold": HyperparameterSpace(
                name="scale_down_cpu_threshold",
                param_type="float",
                min_value=0.2,
                max_value=0.4
            )
        }
    
    def tune_optimization_agent(
        self,
        objective_function: Callable[[Dict[str, Any]], float],
        method: str = "bayesian",
        n_trials: int = 100,
        maximize: bool = False  # Minimize cost
    ) -> TuningResult:
        """Tune hyperparameters for optimization agent"""
        logger.info("Tuning optimization agent hyperparameters...")
        
        # Select tuning method
        if method == "bayesian":
            tuner = BayesianOptimizationTuner(
                search_space=self.search_space,
                objective_function=objective_function,
                maximize=maximize,
                n_trials=n_trials
            )
        elif method == "random":
            tuner = RandomSearchTuner(
                search_space=self.search_space,
                objective_function=objective_function,
                maximize=maximize,
                n_trials=n_trials
            )
        elif method == "grid":
            tuner = GridSearchTuner(
                search_space=self.search_space,
                objective_function=objective_function,
                maximize=maximize,
                grid_size=5
            )
        else:
            raise ValueError(f"Unknown tuning method: {method}")
        
        # Run tuning
        result = tuner.tune()
        
        # Save results
        timestamp = int(time.time())
        result_file = Path("data/hyperparameter-tuning") / f"optimization_{method}_{timestamp}.json"
        tuner.save_results(result, str(result_file))
        
        return result

