# Model Retraining Framework

This directory contains the model retraining system that enables RL agents and optimization models to learn from real-world data and improve over time.

## Overview

The retraining framework provides:
- **Experience Replay**: Store and sample past decisions for training
- **Q-Learning**: Tabular Q-learning for discrete state-action spaces
- **PPO (Proximal Policy Optimization)**: Policy gradient method for continuous improvement
- **DQN (Deep Q-Network)**: Deep learning-based Q-learning
- **Optimization Training**: Gradient-based and evolutionary optimization for resource management

## Components

### 1. Experience Replay (`experience_replay.py`)

Stores past experiences for training:

```python
from ai_engine.retrain import ExperienceReplayBuffer

buffer = ExperienceReplayBuffer(capacity=100000)

# Add experience
buffer.add(state, action, reward, next_state, done)

# Sample batch
states, actions, rewards, next_states, dones = buffer.sample_batch(32)
```

**Prioritized Experience Replay**:
- Importance sampling based on TD errors
- Better sample efficiency

### 2. Q-Learning (`q_learning.py`)

Tabular Q-learning for discrete problems:

```python
from ai_engine.retrain import QLearningTrainer

trainer = QLearningTrainer(
    state_size=10,
    action_size=5,
    learning_rate=0.01,
    discount_factor=0.95
)

# Update Q-value
trainer.update_q_value(state, action, reward, next_state, done)

# Train from replay
trainer.train_from_replay(batch_size=32, epochs=10)

# Save model
trainer.save_model("models/q_learning_model.json")
```

### 3. PPO (`ppo_trainer.py`)

Proximal Policy Optimization for policy gradient methods:

```python
from ai_engine.retrain import PPOTrainer

trainer = PPOTrainer(
    state_size=10,
    action_size=5,
    learning_rate=3e-4,
    clip_epsilon=0.2
)

# Train on episode
trainer.train_episode(states, actions, rewards, dones)

# Save model
trainer.save_model("models/ppo_model.json")
```

### 4. DQN (`dqn_trainer.py`)

Deep Q-Network with experience replay:

```python
from ai_engine.retrain import DQNTrainer

trainer = DQNTrainer(
    state_size=10,
    action_size=5,
    use_prioritized_replay=True
)

# Add experience
trainer.add_experience(state, action, reward, next_state, done)

# Train
trainer.train_from_replay(batch_size=32, steps=100)

# Save model
trainer.save_model("models/dqn_model.json")
```

### 5. Optimization Trainer (`optimization_trainer.py`)

Optimizes resource management strategies:

**Gradient-Based Optimization**:
```python
from ai_engine.retrain import OptimizationTrainer

trainer = OptimizationTrainer(use_evolutionary=False)

# Add performance data
trainer.add_performance_data(
    cpu_usage=0.75,
    memory_usage=0.65,
    cost=100.0,
    response_time=0.5,
    scaling_action="scale_up",
    resource_allocation={"cpu": 0.8, "memory": 0.7},
    outcome="optimal"
)

# Train using gradient descent
trainer.train(method="gradient", iterations=100)
```

**Evolutionary Algorithm**:
```python
trainer = OptimizationTrainer(use_evolutionary=True)

# Train using evolutionary algorithm
trainer.train(method="evolutionary", iterations=50)
```

### 6. Model Retrainer (`model_retrainer.py`)

Orchestrates retraining for all agents:

```python
from ai_engine.retrain import ModelRetrainer
from ai_engine.continuous_learning import DataCollector

data_collector = DataCollector()
retrainer = ModelRetrainer(data_collector)

# Retrain specific agent
retrainer.retrain_agent("self-healing", batch_size=32, epochs=10)

# Retrain all ready agents
retrainer.retrain_all_ready_agents()
```

## Algorithm Selection

### When to Use Q-Learning

- **Discrete state-action spaces**
- **Small to medium state spaces**
- **Tabular representation sufficient**
- **Fast training needed**

**Best for**: Scaling agent, simple decision-making

### When to Use PPO

- **Continuous or large discrete spaces**
- **Policy gradient methods preferred**
- **Stable learning important**
- **On-policy learning acceptable**

**Best for**: Self-healing agent, complex decision-making

### When to Use DQN

- **Large state spaces**
- **Function approximation needed**
- **Off-policy learning preferred**
- **Neural network representation**

**Best for**: Task-solving agent, complex environments

### When to Use Optimization Training

- **Resource management optimization**
- **Cost optimization**
- **Scaling strategy tuning**
- **Historical data available**

**Best for**: Optimization agent, scaling decisions

## Training Workflow

1. **Collect Data**: Use `DataCollector` to gather experiences
2. **Check Readiness**: Verify sufficient data for training
3. **Initialize Trainer**: Create appropriate trainer for algorithm
4. **Train Model**: Run training with experience replay
5. **Save Model**: Persist trained model to disk
6. **Deploy Model**: Load and use updated model in agent

## Integration Example

```python
from ai_engine.continuous_learning import LearningPipeline, DataCollector
from ai_engine.retrain import ModelRetrainer

# Initialize components
data_collector = DataCollector()
pipeline = LearningPipeline()
pipeline.start()

retrainer = ModelRetrainer(data_collector)

# In agent code - record actions
pipeline.record_action(
    agent_name="self-healing",
    action_type="restart_service",
    input_data={"service": "api"},
    output_data={"status": "restarted"},
    success=True,
    execution_time=2.5,
    confidence=0.95,
    explanation="Service restarted"
)

# Periodically retrain
if retrainer.check_retraining_ready("self-healing"):
    retrainer.retrain_agent("self-healing")
```

## Model Storage

Models are saved to `models/retrained/`:
- `{agent_name}_model.json`: Trained model
- Training statistics included
- Can be loaded for deployment

## Best Practices

1. **Sufficient Data**: Ensure minimum experiences before training
2. **Regular Retraining**: Retrain periodically (e.g., daily)
3. **Validation**: Validate models before deployment
4. **Monitoring**: Track training metrics and model performance
5. **Backup**: Keep backups of previous models
6. **A/B Testing**: Test new models alongside old ones

## Next Steps

1. **Integrate Retraining**: Add retraining to learning pipeline
2. **Implement State Encoding**: Proper state representation
3. **Add Neural Networks**: For DQN and advanced PPO
4. **Validation Framework**: Test model improvements
5. **Deployment Pipeline**: Automated model deployment

