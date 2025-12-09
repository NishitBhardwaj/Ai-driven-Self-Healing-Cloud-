"""
Automatic Hyperparameter Adjustment
Automatically adjusts hyperparameters based on performance
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
import json
import threading

from .rl_hyperparameter_tuner import RLHyperparameterTuner, OptimizationAgentHyperparameterTuner
from ..continuous_learning.data_collector import DataCollector
from ..retrain.model_retrainer import ModelRetrainer

logger = logging.getLogger(__name__)


class AutomaticHyperparameterAdjustment:
    """Automatically adjusts hyperparameters based on performance"""
    
    def __init__(
        self,
        data_collector: DataCollector,
        model_retrainer: ModelRetrainer,
        adjustment_interval: int = 86400  # 24 hours
    ):
        self.data_collector = data_collector
        self.model_retrainer = model_retrainer
        
        # Tuning intervals
        self.adjustment_interval = adjustment_interval
        self.last_adjustment: Dict[str, float] = {}
        
        # Performance thresholds
        self.performance_thresholds = {
            "min_success_rate": 0.8,
            "max_latency_p95": 1.0,
            "min_improvement": 0.05  # 5% improvement required
        }
        
        # Running state
        self.running = False
        self.adjustment_thread: Optional[threading.Thread] = None
        
        # Storage
        self.storage_path = Path("data/hyperparameter-tuning/auto-adjustments")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Start automatic adjustment system"""
        if self.running:
            logger.warning("Automatic adjustment system is already running")
            return
        
        self.running = True
        self.adjustment_thread = threading.Thread(target=self._adjustment_loop, daemon=True)
        self.adjustment_thread.start()
        logger.info("Automatic hyperparameter adjustment system started")
    
    def stop(self):
        """Stop automatic adjustment system"""
        self.running = False
        if self.adjustment_thread:
            self.adjustment_thread.join(timeout=10)
        logger.info("Automatic hyperparameter adjustment system stopped")
    
    def _adjustment_loop(self):
        """Main adjustment loop"""
        while self.running:
            try:
                current_time = time.time()
                
                # Check if adjustment is needed for each agent
                agents = [
                    "self-healing",
                    "scaling",
                    "task-solving",
                    "optimization"
                ]
                
                for agent_name in agents:
                    last_adj_time = self.last_adjustment.get(agent_name, 0)
                    
                    if current_time - last_adj_time >= self.adjustment_interval:
                        if self._should_adjust(agent_name):
                            self._adjust_hyperparameters(agent_name)
                            self.last_adjustment[agent_name] = current_time
                
                # Sleep for a short interval
                time.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in adjustment loop: {e}", exc_info=True)
                time.sleep(3600)
    
    def _should_adjust(self, agent_name: str) -> bool:
        """Determine if hyperparameters should be adjusted"""
        # Get recent performance
        actions = self.data_collector.get_recent_actions(agent_name=agent_name, limit=1000)
        
        if len(actions) < 100:
            logger.debug(f"Insufficient data for {agent_name}")
            return False
        
        # Calculate success rate
        # Actions are dictionaries with 'success' field
        successful = sum(1 for a in actions if isinstance(a, dict) and a.get("success", False))
        success_rate = successful / len(actions) if actions else 0.0
        
        # Check if performance is below threshold
        if success_rate < self.performance_thresholds["min_success_rate"]:
            logger.info(
                f"Performance below threshold for {agent_name}: "
                f"Success rate {success_rate:.2%} < {self.performance_thresholds['min_success_rate']:.2%}"
            )
            return True
        
        return False
    
    def _adjust_hyperparameters(self, agent_name: str):
        """Adjust hyperparameters for an agent"""
        logger.info(f"Adjusting hyperparameters for {agent_name}...")
        
        # Determine algorithm
        algorithm = self._get_algorithm(agent_name)
        
        # Create objective function
        objective_function = self._create_objective_function(agent_name)
        
        # Create tuner
        tuner = RLHyperparameterTuner(agent_name)
        
        # Run tuning
        try:
            result = tuner.tune_rl_model(
                algorithm=algorithm,
                objective_function=objective_function,
                method="bayesian",
                n_trials=50,  # Fewer trials for automatic adjustment
                maximize=True
            )
            
            # Apply best hyperparameters
            self._apply_hyperparameters(agent_name, result.best_config.params)
            
            logger.info(
                f"Hyperparameter adjustment completed for {agent_name}: "
                f"Best score = {result.best_score:.4f}"
            )
            
        except Exception as e:
            logger.error(f"Error adjusting hyperparameters for {agent_name}: {e}", exc_info=True)
    
    def _get_algorithm(self, agent_name: str) -> str:
        """Get algorithm for an agent"""
        algorithm_map = {
            "self-healing": "ppo",
            "scaling": "q_learning",
            "task-solving": "dqn",
            "optimization": "optimization"
        }
        return algorithm_map.get(agent_name, "q_learning")
    
    def _create_objective_function(self, agent_name: str) -> Callable[[Dict[str, Any]], float]:
        """Create objective function for hyperparameter tuning"""
        def objective(params: Dict[str, Any]) -> float:
            # In production, this would:
            # 1. Create model with these hyperparameters
            # 2. Train on recent data
            # 3. Evaluate on validation set
            # 4. Return performance score
            
            # For now, simplified evaluation based on current performance
            actions = self.data_collector.get_recent_actions(agent_name, limit=100)
            
            if not actions:
                return 0.0
            
            # Calculate success rate
            successful = sum(1 for a in actions if a.get("success", False))
            success_rate = successful / len(actions)
            
            # Simulate improvement based on hyperparameters (simplified)
            # In production, actually train and evaluate
            improvement_factor = 1.0
            
            # Learning rate impact (simplified)
            if "learning_rate" in params:
                lr = params["learning_rate"]
                # Optimal learning rate around 0.01
                if 0.005 <= lr <= 0.05:
                    improvement_factor *= 1.1
                elif lr < 0.001 or lr > 0.1:
                    improvement_factor *= 0.9
            
            # Discount factor impact
            if "discount_factor" in params or "gamma" in params:
                gamma = params.get("discount_factor") or params.get("gamma", 0.95)
                if 0.9 <= gamma <= 0.99:
                    improvement_factor *= 1.05
            
            # Simulated score
            score = success_rate * improvement_factor
            
            return score
        
        return objective
    
    def _apply_hyperparameters(self, agent_name: str, params: Dict[str, Any]):
        """Apply hyperparameters to agent model"""
        logger.info(f"Applying hyperparameters to {agent_name}: {params}")
        
        # In production, this would:
        # 1. Update model configuration
        # 2. Retrain model with new hyperparameters
        # 3. Deploy updated model
        
        # For now, save configuration
        timestamp = int(time.time())
        config_file = self.storage_path / f"{agent_name}_hyperparameters_{timestamp}.json"
        
        config_data = {
            "agent_name": agent_name,
            "hyperparameters": params,
            "timestamp": timestamp,
            "applied": False  # Would be True after actual application
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Hyperparameters saved to {config_file}")
    
    def manual_tune(
        self,
        agent_name: str,
        algorithm: str,
        method: str = "bayesian",
        n_trials: int = 100
    ) -> Dict[str, Any]:
        """Manually trigger hyperparameter tuning"""
        logger.info(f"Manual tuning requested for {agent_name} ({algorithm})...")
        
        tuner = RLHyperparameterTuner(agent_name)
        objective_function = self._create_objective_function(agent_name)
        
        result = tuner.tune_rl_model(
            algorithm=algorithm,
            objective_function=objective_function,
            method=method,
            n_trials=n_trials,
            maximize=True
        )
        
        # Apply best hyperparameters
        self._apply_hyperparameters(agent_name, result.best_config.params)
        
        return {
            "best_hyperparameters": result.best_config.params,
            "best_score": result.best_score,
            "total_trials": result.total_trials,
            "tuning_time": result.tuning_time
        }
    
    def tune_optimization_agent(
        self,
        method: str = "bayesian",
        n_trials: int = 100
    ) -> Dict[str, Any]:
        """Tune optimization agent hyperparameters"""
        logger.info("Tuning optimization agent hyperparameters...")
        
        # Create objective function (minimize cost)
        def objective(params: Dict[str, Any]) -> float:
            # In production, evaluate on historical data
            # For now, simplified
            return -100.0  # Negative cost (to maximize)
        
        tuner = OptimizationAgentHyperparameterTuner()
        result = tuner.tune_optimization_agent(
            objective_function=objective,
            method=method,
            n_trials=n_trials,
            maximize=False
        )
        
        return {
            "best_hyperparameters": result.best_config.params,
            "best_score": result.best_score,
            "total_trials": result.total_trials,
            "tuning_time": result.tuning_time
        }

