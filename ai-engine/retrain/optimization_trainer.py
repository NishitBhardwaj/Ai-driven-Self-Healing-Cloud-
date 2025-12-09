"""
Optimization Agent Retraining
Uses historical performance data to optimize resource management strategies
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from pathlib import Path
import json
from scipy.optimize import minimize
import random

logger = logging.getLogger(__name__)


@dataclass
class PerformanceData:
    """Historical performance data point"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    cost: float
    response_time: float
    scaling_action: str
    resource_allocation: Dict[str, float]
    outcome: str  # "optimal", "over-provisioned", "under-provisioned"


class OptimizationTrainer:
    """Trainer for optimization agent using historical data"""
    
    def __init__(
        self,
        learning_rate: float = 0.01,
        use_evolutionary: bool = False,
        population_size: int = 50,
        mutation_rate: float = 0.1
    ):
        self.learning_rate = learning_rate
        self.use_evolutionary = use_evolutionary
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        
        # Cost model parameters (to be learned)
        self.cost_weights = {
            "cpu_weight": 1.0,
            "memory_weight": 1.0,
            "response_time_weight": 0.5,
            "over_provision_penalty": 2.0,
            "under_provision_penalty": 3.0
        }
        
        # Scaling thresholds (to be optimized)
        self.scaling_thresholds = {
            "scale_up_cpu": 0.8,
            "scale_up_memory": 0.8,
            "scale_down_cpu": 0.3,
            "scale_down_memory": 0.3
        }
        
        # Historical data
        self.performance_history: List[PerformanceData] = []
        
        # Training statistics
        self.training_stats = {
            "iterations": 0,
            "cost_history": [],
            "optimal_actions": 0,
            "over_provisioned": 0,
            "under_provisioned": 0
        }
    
    def add_performance_data(
        self,
        cpu_usage: float,
        memory_usage: float,
        cost: float,
        response_time: float,
        scaling_action: str,
        resource_allocation: Dict[str, float],
        outcome: str
    ):
        """Add performance data point"""
        import time
        
        data = PerformanceData(
            timestamp=time.time(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            cost=cost,
            response_time=response_time,
            scaling_action=scaling_action,
            resource_allocation=resource_allocation,
            outcome=outcome
        )
        
        self.performance_history.append(data)
        
        # Update statistics
        if outcome == "optimal":
            self.training_stats["optimal_actions"] += 1
        elif outcome == "over-provisioned":
            self.training_stats["over_provisioned"] += 1
        elif outcome == "under-provisioned":
            self.training_stats["under_provisioned"] += 1
    
    def cost_function(self, params: np.ndarray) -> float:
        """Cost function to minimize"""
        # Unpack parameters
        cpu_weight, memory_weight, rt_weight, over_penalty, under_penalty = params
        
        total_cost = 0.0
        
        for data in self.performance_history[-1000:]:  # Use last 1000 data points
            # Base cost
            base_cost = (
                cpu_weight * data.cpu_usage +
                memory_weight * data.memory_usage +
                rt_weight * data.response_time
            )
            
            # Outcome penalties
            if data.outcome == "over-provisioned":
                base_cost *= (1 + over_penalty)
            elif data.outcome == "under-provisioned":
                base_cost *= (1 + under_penalty)
            
            total_cost += base_cost
        
        return total_cost / len(self.performance_history[-1000:])
    
    def train_gradient_descent(self, iterations: int = 100):
        """Train using gradient-based optimization"""
        logger.info("Training optimization model using gradient descent...")
        
        # Initial parameters
        initial_params = np.array([
            self.cost_weights["cpu_weight"],
            self.cost_weights["memory_weight"],
            self.cost_weights["response_time_weight"],
            self.cost_weights["over_provision_penalty"],
            self.cost_weights["under_provision_penalty"]
        ])
        
        # Optimize using scipy
        result = minimize(
            self.cost_function,
            initial_params,
            method='L-BFGS-B',
            options={'maxiter': iterations}
        )
        
        # Update cost weights
        self.cost_weights["cpu_weight"] = result.x[0]
        self.cost_weights["memory_weight"] = result.x[1]
        self.cost_weights["response_time_weight"] = result.x[2]
        self.cost_weights["over_provision_penalty"] = result.x[3]
        self.cost_weights["under_provision_penalty"] = result.x[4]
        
        self.training_stats["iterations"] += iterations
        self.training_stats["cost_history"].append(result.fun)
        
        logger.info(f"Gradient descent completed: Final cost = {result.fun:.4f}")
        logger.info(f"Updated weights: {self.cost_weights}")
    
    def train_evolutionary(self, generations: int = 50):
        """Train using evolutionary algorithm"""
        logger.info("Training optimization model using evolutionary algorithm...")
        
        # Initialize population
        population = []
        for _ in range(self.population_size):
            individual = {
                "cpu_weight": random.uniform(0.5, 2.0),
                "memory_weight": random.uniform(0.5, 2.0),
                "response_time_weight": random.uniform(0.1, 1.0),
                "over_provision_penalty": random.uniform(1.0, 3.0),
                "under_provision_penalty": random.uniform(2.0, 5.0)
            }
            population.append(individual)
        
        best_cost = float('inf')
        best_individual = None
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                # Temporarily set weights
                old_weights = self.cost_weights.copy()
                self.cost_weights.update(individual)
                
                # Evaluate
                cost = self.cost_function(np.array([
                    individual["cpu_weight"],
                    individual["memory_weight"],
                    individual["response_time_weight"],
                    individual["over_provision_penalty"],
                    individual["under_provision_penalty"]
                ]))
                
                fitness_scores.append((individual, cost))
                self.cost_weights = old_weights
            
            # Sort by fitness (lower cost is better)
            fitness_scores.sort(key=lambda x: x[1])
            
            # Update best
            if fitness_scores[0][1] < best_cost:
                best_cost = fitness_scores[0][1]
                best_individual = fitness_scores[0][0]
            
            # Selection: Keep top 50%
            elite_size = self.population_size // 2
            elite = [ind for ind, _ in fitness_scores[:elite_size]]
            
            # Crossover and mutation
            new_population = elite.copy()
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = random.choice(elite)
                parent2 = random.choice(elite)
                
                # Crossover
                child = {}
                for key in parent1:
                    child[key] = random.choice([parent1[key], parent2[key]])
                
                # Mutation
                if random.random() < self.mutation_rate:
                    key = random.choice(list(child.keys()))
                    if "penalty" in key:
                        child[key] = random.uniform(1.0, 5.0)
                    else:
                        child[key] = random.uniform(0.1, 2.0)
                
                new_population.append(child)
            
            population = new_population
            
            if generation % 10 == 0:
                logger.info(f"Generation {generation}: Best cost = {best_cost:.4f}")
        
        # Update with best individual
        if best_individual:
            self.cost_weights.update(best_individual)
            self.training_stats["iterations"] += generations
            self.training_stats["cost_history"].append(best_cost)
            
            logger.info(f"Evolutionary training completed: Best cost = {best_cost:.4f}")
            logger.info(f"Best weights: {self.cost_weights}")
    
    def optimize_scaling_thresholds(self):
        """Optimize scaling thresholds based on historical data"""
        logger.info("Optimizing scaling thresholds...")
        
        optimal_thresholds = {
            "scale_up_cpu": 0.8,
            "scale_up_memory": 0.8,
            "scale_down_cpu": 0.3,
            "scale_down_memory": 0.3
        }
        
        # Analyze historical data
        if len(self.performance_history) < 100:
            logger.warning("Insufficient data for threshold optimization")
            return
        
        # Find optimal thresholds that minimize over/under-provisioning
        scale_up_cpu_values = []
        scale_up_memory_values = []
        scale_down_cpu_values = []
        scale_down_memory_values = []
        
        for data in self.performance_history[-1000:]:
            if data.outcome == "optimal":
                if data.scaling_action == "scale_up":
                    scale_up_cpu_values.append(data.cpu_usage)
                    scale_up_memory_values.append(data.memory_usage)
                elif data.scaling_action == "scale_down":
                    scale_down_cpu_values.append(data.cpu_usage)
                    scale_down_memory_values.append(data.memory_usage)
        
        # Update thresholds based on optimal actions
        if scale_up_cpu_values:
            optimal_thresholds["scale_up_cpu"] = np.percentile(scale_up_cpu_values, 75)
        if scale_up_memory_values:
            optimal_thresholds["scale_up_memory"] = np.percentile(scale_up_memory_values, 75)
        if scale_down_cpu_values:
            optimal_thresholds["scale_down_cpu"] = np.percentile(scale_down_cpu_values, 25)
        if scale_down_memory_values:
            optimal_thresholds["scale_down_memory"] = np.percentile(scale_down_memory_values, 25)
        
        self.scaling_thresholds = optimal_thresholds
        logger.info(f"Updated scaling thresholds: {self.scaling_thresholds}")
    
    def train(self, method: str = "gradient", iterations: int = 100):
        """Train optimization model"""
        if method == "gradient":
            self.train_gradient_descent(iterations)
        elif method == "evolutionary":
            self.train_evolutionary(iterations)
        else:
            raise ValueError(f"Unknown training method: {method}")
        
        # Optimize scaling thresholds
        self.optimize_scaling_thresholds()
    
    def get_optimal_action(
        self,
        cpu_usage: float,
        memory_usage: float,
        current_cost: float
    ) -> Tuple[str, Dict[str, float]]:
        """Get optimal scaling action based on learned model"""
        # Check thresholds
        if cpu_usage > self.scaling_thresholds["scale_up_cpu"] or \
           memory_usage > self.scaling_thresholds["scale_up_memory"]:
            action = "scale_up"
        elif cpu_usage < self.scaling_thresholds["scale_down_cpu"] and \
             memory_usage < self.scaling_thresholds["scale_down_memory"]:
            action = "scale_down"
        else:
            action = "maintain"
        
        # Calculate resource allocation
        resource_allocation = {
            "cpu": max(0.5, cpu_usage * 1.2) if action == "scale_up" else cpu_usage,
            "memory": max(0.5, memory_usage * 1.2) if action == "scale_up" else memory_usage
        }
        
        return action, resource_allocation
    
    def save_model(self, file_path: str):
        """Save optimization model to disk"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "cost_weights": self.cost_weights,
            "scaling_thresholds": self.scaling_thresholds,
            "training_stats": self.training_stats
        }
        
        with open(path, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        logger.info(f"Saved optimization model to {file_path}")
    
    def load_model(self, file_path: str):
        """Load optimization model from disk"""
        with open(file_path, 'r') as f:
            model_data = json.load(f)
        
        self.cost_weights = model_data["cost_weights"]
        self.scaling_thresholds = model_data["scaling_thresholds"]
        self.training_stats = model_data.get("training_stats", self.training_stats)
        
        logger.info(f"Loaded optimization model from {file_path}")

