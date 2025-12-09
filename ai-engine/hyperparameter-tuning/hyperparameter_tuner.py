"""
Hyperparameter Tuning Framework
Automatically tunes hyperparameters for RL models and Optimization Agents
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import numpy as np
from pathlib import Path
import json
import random

logger = logging.getLogger(__name__)


@dataclass
class HyperparameterSpace:
    """Defines a hyperparameter search space"""
    name: str
    param_type: str  # "float", "int", "categorical"
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List[Any]] = None
    log_scale: bool = False


@dataclass
class HyperparameterConfig:
    """Hyperparameter configuration"""
    params: Dict[str, Any]
    score: float
    timestamp: float
    trial_id: str
    metadata: Dict[str, Any]


@dataclass
class TuningResult:
    """Result of hyperparameter tuning"""
    best_config: HyperparameterConfig
    all_trials: List[HyperparameterConfig]
    optimization_method: str
    total_trials: int
    best_score: float
    tuning_time: float


class HyperparameterTuner(ABC):
    """Base class for hyperparameter tuning methods"""
    
    def __init__(
        self,
        search_space: Dict[str, HyperparameterSpace],
        objective_function: Callable[[Dict[str, Any]], float],
        maximize: bool = True,
        n_trials: int = 100
    ):
        self.search_space = search_space
        self.objective_function = objective_function
        self.maximize = maximize
        self.n_trials = n_trials
        
        # Trial tracking
        self.trials: List[HyperparameterConfig] = []
        self.best_config: Optional[HyperparameterConfig] = None
        self.best_score: float = float('-inf') if maximize else float('inf')
        
        # Storage
        self.storage_path = Path("data/hyperparameter-tuning")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def suggest_parameters(self) -> Dict[str, Any]:
        """Suggest next set of hyperparameters to try"""
        pass
    
    def sample_parameter(self, space: HyperparameterSpace) -> Any:
        """Sample a value from a parameter space"""
        if space.param_type == "float":
            if space.log_scale:
                min_val = np.log10(space.min_value)
                max_val = np.log10(space.max_value)
                value = 10 ** np.random.uniform(min_val, max_val)
            else:
                value = np.random.uniform(space.min_value, space.max_value)
            return value
        
        elif space.param_type == "int":
            return np.random.randint(space.min_value, space.max_value + 1)
        
        elif space.param_type == "categorical":
            return random.choice(space.choices)
        
        else:
            raise ValueError(f"Unknown parameter type: {space.param_type}")
    
    def tune(self) -> TuningResult:
        """Run hyperparameter tuning"""
        logger.info(f"Starting hyperparameter tuning with {self.n_trials} trials...")
        start_time = time.time()
        
        for trial_id in range(self.n_trials):
            # Suggest parameters
            params = self.suggest_parameters()
            
            # Evaluate objective
            try:
                score = self.objective_function(params)
            except Exception as e:
                logger.error(f"Error evaluating parameters: {e}")
                score = float('-inf') if self.maximize else float('inf')
            
            # Create config
            config = HyperparameterConfig(
                params=params,
                score=score,
                timestamp=time.time(),
                trial_id=f"trial_{trial_id}",
                metadata={}
            )
            
            self.trials.append(config)
            
            # Update best
            if (self.maximize and score > self.best_score) or \
               (not self.maximize and score < self.best_score):
                self.best_score = score
                self.best_config = config
            
            if (trial_id + 1) % 10 == 0:
                logger.info(
                    f"Trial {trial_id + 1}/{self.n_trials}: "
                    f"Best score: {self.best_score:.4f}"
                )
        
        tuning_time = time.time() - start_time
        
        result = TuningResult(
            best_config=self.best_config,
            all_trials=self.trials,
            optimization_method=self.__class__.__name__,
            total_trials=self.n_trials,
            best_score=self.best_score,
            tuning_time=tuning_time
        )
        
        logger.info(
            f"Tuning completed: Best score = {self.best_score:.4f} "
            f"in {tuning_time:.2f}s"
        )
        
        return result
    
    def save_results(self, result: TuningResult, file_path: str):
        """Save tuning results to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        result_data = {
            "best_config": asdict(result.best_config),
            "best_score": result.best_score,
            "total_trials": result.total_trials,
            "tuning_time": result.tuning_time,
            "optimization_method": result.optimization_method,
            "all_trials": [asdict(trial) for trial in result.all_trials[:100]]  # Save top 100
        }
        
        with open(path, 'w') as f:
            json.dump(result_data, f, indent=2, default=str)
        
        logger.info(f"Saved tuning results to {file_path}")


class RandomSearchTuner(HyperparameterTuner):
    """Random search hyperparameter tuning"""
    
    def suggest_parameters(self) -> Dict[str, Any]:
        """Suggest random parameters"""
        params = {}
        for param_name, space in self.search_space.items():
            params[param_name] = self.sample_parameter(space)
        return params


class GridSearchTuner(HyperparameterTuner):
    """Grid search hyperparameter tuning"""
    
    def __init__(
        self,
        search_space: Dict[str, HyperparameterSpace],
        objective_function: Callable[[Dict[str, Any]], float],
        maximize: bool = True,
        grid_size: int = 5
    ):
        super().__init__(search_space, objective_function, maximize, n_trials=0)
        self.grid_size = grid_size
        self.grid_points = self._generate_grid()
        self.n_trials = len(self.grid_points)
        self.current_index = 0
    
    def _generate_grid(self) -> List[Dict[str, Any]]:
        """Generate grid of parameter combinations"""
        param_names = list(self.search_space.keys())
        param_spaces = [self.search_space[name] for name in param_names]
        
        # Generate grid for each parameter
        param_grids = []
        for space in param_spaces:
            if space.param_type == "float":
                if space.log_scale:
                    min_val = np.log10(space.min_value)
                    max_val = np.log10(space.max_value)
                    grid = np.logspace(min_val, max_val, self.grid_size)
                else:
                    grid = np.linspace(space.min_value, space.max_value, self.grid_size)
            elif space.param_type == "int":
                grid = np.linspace(space.min_value, space.max_value, self.grid_size, dtype=int)
            elif space.param_type == "categorical":
                grid = space.choices
            else:
                grid = [space.min_value]
            
            param_grids.append(grid)
        
        # Generate all combinations
        from itertools import product
        combinations = list(product(*param_grids))
        
        grid_points = []
        for combo in combinations:
            params = {name: value for name, value in zip(param_names, combo)}
            grid_points.append(params)
        
        return grid_points
    
    def suggest_parameters(self) -> Dict[str, Any]:
        """Suggest next grid point"""
        if self.current_index >= len(self.grid_points):
            raise StopIteration("All grid points exhausted")
        
        params = self.grid_points[self.current_index]
        self.current_index += 1
        return params


class BayesianOptimizationTuner(HyperparameterTuner):
    """Bayesian optimization hyperparameter tuning"""
    
    def __init__(
        self,
        search_space: Dict[str, HyperparameterSpace],
        objective_function: Callable[[Dict[str, Any]], float],
        maximize: bool = True,
        n_trials: int = 100,
        n_initial: int = 10,
        acquisition_function: str = "ucb"
    ):
        super().__init__(search_space, objective_function, maximize, n_trials)
        self.n_initial = n_initial
        self.acquisition_function = acquisition_function
        self.initialized = False
    
    def suggest_parameters(self) -> Dict[str, Any]:
        """Suggest parameters using Bayesian optimization"""
        if len(self.trials) < self.n_initial:
            # Random exploration for initial points
            params = {}
            for param_name, space in self.search_space.items():
                params[param_name] = self.sample_parameter(space)
            return params
        
        # Bayesian optimization (simplified - in production, use scikit-optimize or similar)
        # For now, use improved random search with exploitation
        return self._bayesian_suggest()
    
    def _bayesian_suggest(self) -> Dict[str, Any]:
        """Bayesian suggestion (simplified implementation)"""
        # In production, use Gaussian Process or Tree-structured Parzen Estimator
        # For now, use exploitation-exploration balance
        
        if not self.trials:
            return self._random_sample()
        
        # Get top performing trials
        sorted_trials = sorted(
            self.trials,
            key=lambda x: x.score,
            reverse=self.maximize
        )
        top_trials = sorted_trials[:min(5, len(sorted_trials))]
        
        # With probability 0.7, exploit (sample near good points)
        # With probability 0.3, explore (random sample)
        if random.random() < 0.7 and top_trials:
            # Sample near a good point
            base_trial = random.choice(top_trials)
            params = {}
            for param_name, space in self.search_space.items():
                base_value = base_trial.params[param_name]
                
                if space.param_type == "float":
                    # Add small random perturbation
                    perturbation = (space.max_value - space.min_value) * 0.1
                    new_value = base_value + np.random.uniform(-perturbation, perturbation)
                    params[param_name] = np.clip(new_value, space.min_value, space.max_value)
                elif space.param_type == "int":
                    # Try nearby integer
                    params[param_name] = int(np.clip(
                        base_value + np.random.randint(-2, 3),
                        space.min_value,
                        space.max_value
                    ))
                else:
                    # For categorical, sometimes use same, sometimes random
                    if random.random() < 0.5:
                        params[param_name] = base_value
                    else:
                        params[param_name] = self.sample_parameter(space)
        else:
            # Random exploration
            params = self._random_sample()
        
        return params
    
    def _random_sample(self) -> Dict[str, Any]:
        """Random sample from search space"""
        params = {}
        for param_name, space in self.search_space.items():
            params[param_name] = self.sample_parameter(space)
        return params

