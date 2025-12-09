# Hyperparameter Tuning Framework

This directory contains the hyperparameter tuning framework that automatically optimizes hyperparameters for RL models and Optimization Agents.

## Overview

The hyperparameter tuning framework provides:
- **Automatic Tuning**: Automatically tunes hyperparameters based on performance
- **Multiple Methods**: Bayesian optimization, random search, grid search
- **RL Model Tuning**: Specialized tuners for Q-Learning, PPO, DQN
- **Optimization Agent Tuning**: Tunes cost function weights and thresholds
- **Continuous Adjustment**: Automatically adjusts hyperparameters over time

## Components

### 1. Hyperparameter Tuner (`hyperparameter_tuner.py`)

Base framework for hyperparameter tuning:

**Base Classes**:
- `HyperparameterTuner`: Abstract base class
- `RandomSearchTuner`: Random search implementation
- `GridSearchTuner`: Grid search implementation
- `BayesianOptimizationTuner`: Bayesian optimization implementation

**Usage**:
```python
from ai_engine.hyperparameter_tuning import HyperparameterSpace, RandomSearchTuner

# Define search space
search_space = {
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
    )
}

# Define objective function
def objective(params):
    # Train model with params and return score
    return score

# Create tuner
tuner = RandomSearchTuner(
    search_space=search_space,
    objective_function=objective,
    maximize=True,
    n_trials=100
)

# Run tuning
result = tuner.tune()
print(f"Best score: {result.best_score}")
print(f"Best params: {result.best_config.params}")
```

### 2. RL Hyperparameter Tuner (`rl_hyperparameter_tuner.py`)

Specialized tuner for RL models:

**Supported Algorithms**:
- Q-Learning
- PPO (Proximal Policy Optimization)
- DQN (Deep Q-Network)

**Usage**:
```python
from ai_engine.hyperparameter_tuning import RLHyperparameterTuner

tuner = RLHyperparameterTuner("self-healing")

# Define objective function
def objective(params):
    # Train RL model with params
    # Return performance score
    return score

# Tune using Bayesian optimization
result = tuner.tune_rl_model(
    algorithm="ppo",
    objective_function=objective,
    method="bayesian",
    n_trials=100,
    maximize=True
)
```

### 3. Optimization Agent Tuner (`rl_hyperparameter_tuner.py`)

Tuner for Optimization Agent:

**Tuned Parameters**:
- Cost weights (CPU, memory, response time)
- Provision penalties
- Scaling thresholds

**Usage**:
```python
from ai_engine.hyperparameter_tuning import OptimizationAgentHyperparameterTuner

tuner = OptimizationAgentHyperparameterTuner()

# Define objective (minimize cost)
def objective(params):
    # Evaluate cost with params
    return -cost  # Negative for maximization

# Tune
result = tuner.tune_optimization_agent(
    objective_function=objective,
    method="bayesian",
    n_trials=100,
    maximize=False
)
```

### 4. Automatic Adjustment (`auto_adjustment.py`)

Automatically adjusts hyperparameters based on performance:

**Features**:
- Continuous monitoring
- Performance-based triggering
- Automatic tuning
- Hyperparameter application

**Usage**:
```python
from ai_engine.hyperparameter_tuning import AutomaticHyperparameterAdjustment
from ai_engine.continuous_learning import DataCollector
from ai_engine.retrain import ModelRetrainer

data_collector = DataCollector()
model_retrainer = ModelRetrainer(data_collector)

auto_adjust = AutomaticHyperparameterAdjustment(
    data_collector=data_collector,
    model_retrainer=model_retrainer,
    adjustment_interval=86400  # 24 hours
)

# Start automatic adjustment
auto_adjust.start()

# Manual tuning
result = auto_adjust.manual_tune(
    agent_name="self-healing",
    algorithm="ppo",
    method="bayesian",
    n_trials=100
)
```

## Tuning Methods

### Random Search

**Use Case**: Quick exploration, large search spaces
- Randomly samples from search space
- No assumptions about objective function
- Good for initial exploration

**Pros**:
- Simple and fast
- No assumptions
- Parallelizable

**Cons**:
- May miss optimal regions
- Less efficient than Bayesian

### Grid Search

**Use Case**: Small search spaces, exhaustive search
- Systematically explores all combinations
- Guaranteed to find best in grid

**Pros**:
- Exhaustive
- Reproducible
- Good for small spaces

**Cons**:
- Exponential complexity
- May miss optimal values between grid points

### Bayesian Optimization

**Use Case**: Expensive evaluations, limited trials
- Uses probabilistic model to guide search
- Balances exploration and exploitation
- Efficient for expensive evaluations

**Pros**:
- Efficient sample usage
- Good for expensive evaluations
- Adaptive search

**Cons**:
- More complex
- Requires more implementation

## Search Space Definition

### Float Parameters

```python
HyperparameterSpace(
    name="learning_rate",
    param_type="float",
    min_value=0.001,
    max_value=0.1,
    log_scale=True  # Use log scale for wide ranges
)
```

### Integer Parameters

```python
HyperparameterSpace(
    name="batch_size",
    param_type="int",
    min_value=16,
    max_value=128
)
```

### Categorical Parameters

```python
HyperparameterSpace(
    name="optimizer",
    param_type="categorical",
    choices=["adam", "sgd", "rmsprop"]
)
```

## RL Model Hyperparameters

### Q-Learning

- `learning_rate`: 0.001 - 0.1 (log scale)
- `discount_factor`: 0.8 - 0.99
- `epsilon`: 0.01 - 1.0
- `epsilon_decay`: 0.9 - 0.999

### PPO

- `learning_rate`: 1e-5 - 1e-2 (log scale)
- `gamma`: 0.9 - 0.999
- `gae_lambda`: 0.8 - 0.99
- `clip_epsilon`: 0.1 - 0.3
- `value_coef`: 0.1 - 1.0
- `entropy_coef`: 0.001 - 0.1 (log scale)

### DQN

- `learning_rate`: 1e-5 - 1e-2 (log scale)
- `gamma`: 0.9 - 0.99
- `epsilon`: 0.01 - 1.0
- `epsilon_decay`: 0.9 - 0.999
- `target_update_frequency`: 10 - 1000

## Optimization Agent Hyperparameters

- `cpu_weight`: 0.5 - 2.0
- `memory_weight`: 0.5 - 2.0
- `response_time_weight`: 0.1 - 1.0
- `over_provision_penalty`: 1.0 - 3.0
- `under_provision_penalty`: 2.0 - 5.0
- `scale_up_cpu_threshold`: 0.6 - 0.9
- `scale_down_cpu_threshold`: 0.2 - 0.4

## Automatic Adjustment

The automatic adjustment system:

1. **Monitors Performance**: Tracks success rates and metrics
2. **Detects Issues**: Identifies when performance is below threshold
3. **Triggers Tuning**: Automatically runs hyperparameter tuning
4. **Applies Best**: Updates model with best hyperparameters
5. **Validates**: Monitors improvement after adjustment

**Adjustment Triggers**:
- Success rate < 80%
- Performance degradation detected
- Periodic adjustment (every 24 hours)

## Best Practices

1. **Start with Random Search**: Use random search for initial exploration
2. **Use Bayesian for Expensive**: Use Bayesian optimization for expensive evaluations
3. **Set Appropriate Ranges**: Define search spaces based on domain knowledge
4. **Use Log Scale**: Use log scale for parameters with wide ranges
5. **Validate Results**: Always validate tuned hyperparameters
6. **Monitor Performance**: Track performance after applying new hyperparameters

## Integration Example

```python
from ai_engine.hyperparameter_tuning import AutomaticHyperparameterAdjustment
from ai_engine.continuous_learning import LearningPipeline, DataCollector
from ai_engine.retrain import ModelRetrainer

# Initialize components
data_collector = DataCollector()
learning_pipeline = LearningPipeline()
model_retrainer = ModelRetrainer(data_collector)

# Start learning pipeline
learning_pipeline.start()

# Start automatic adjustment
auto_adjust = AutomaticHyperparameterAdjustment(
    data_collector=data_collector,
    model_retrainer=model_retrainer
)
auto_adjust.start()

# System will automatically:
# 1. Monitor performance
# 2. Detect when tuning is needed
# 3. Run hyperparameter tuning
# 4. Apply best hyperparameters
# 5. Retrain models
```

## Next Steps

1. **Integrate with Models**: Connect to actual model training
2. **Implement Advanced BO**: Use scikit-optimize or Optuna
3. **Add Early Stopping**: Stop tuning if no improvement
4. **Parallel Tuning**: Run multiple trials in parallel
5. **Validation Framework**: Validate tuned hyperparameters

