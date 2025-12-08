# Reinforcement Learning Module

This module implements a Deep Q-Network (DQN) agent for learning optimal healing and scaling strategies in the self-healing cloud system.

## Overview

The RL module uses reinforcement learning to:
- Learn optimal actions for system recovery
- Adapt to different failure scenarios
- Optimize resource allocation
- Balance multiple objectives (availability, cost, performance)

## Components

### `agent.py` - RL Agent
- **DQNNetwork**: Deep Q-Network for action-value estimation
- **RLAgent**: Main agent class with epsilon-greedy policy
- Features:
  - Experience replay buffer
  - Target network for stable learning
  - Epsilon-greedy exploration
  - Action confidence estimation

### `environment.py` - RL Environment
- **SystemState**: Represents system state
- **RLEnvironment**: Simulates cloud system
- Features:
  - State representation
  - Action execution
  - Reward calculation
  - Episode management

### `reward_functions.py` - Reward Functions
- **BasicRewardFunction**: Simple reward for fixing failures
- **ShapedRewardFunction**: Intermediate rewards for guidance
- **SparseRewardFunction**: End-of-episode rewards
- **MultiObjectiveRewardFunction**: Balances multiple goals

### `state_encoder.py` - State Encoding
- **StateEncoder**: Encodes system state into feature vectors
- Features:
  - Feature extraction
  - Normalization
  - Feature engineering
  - Importance scoring

### `trainer.py` - Training
- **RLTrainer**: Trains the RL agent
- Features:
  - Training loop
  - Checkpointing
  - Evaluation
  - Statistics tracking

## Usage

### Basic Training

```python
from ai_engine.rl.agent import RLAgent
from ai_engine.rl.environment import RLEnvironment
from ai_engine.rl.trainer import RLTrainer
from ai_engine.rl.reward_functions import RewardFunctionFactory, RewardType

# Create agent
agent = RLAgent(
    state_dim=19,
    action_dim=6,
    learning_rate=0.001,
    gamma=0.99
)

# Create environment
env = RLEnvironment(max_steps=1000)

# Create trainer
trainer = RLTrainer(
    agent=agent,
    environment=env,
    reward_function=RewardFunctionFactory.create(RewardType.SHAPED)
)

# Train
stats = trainer.train(num_episodes=1000)
```

### Using Trained Agent

```python
# Load trained agent
agent.load("checkpoints/agent_final.pth")

# Get action for current state
state = env.get_state()
action, confidence = agent.predict(state)

# Execute action
next_state, reward, done, info = env.step(action)
```

## Action Space

- `RESTART_POD` (0): Restart a failed pod
- `ROLLBACK_DEPLOYMENT` (1): Rollback deployment to previous version
- `REPLACE_POD` (2): Replace a failed pod
- `SCALE_UP` (3): Scale up deployment
- `SCALE_DOWN` (4): Scale down deployment
- `NO_ACTION` (5): Take no action

## State Features

The state includes:
- Pod metrics (count, health, failures)
- Resource metrics (CPU, memory, network)
- Service metrics (request rate, error rate, response time)
- Deployment metrics (replicas, availability)
- Failure indicators (crash, timeout, resource exhaustion)
- Temporal features (time since last action, episode step)

## Training Tips

1. **Start with shaped rewards** for faster learning
2. **Use experience replay** to break correlation
3. **Update target network** periodically for stability
4. **Monitor epsilon decay** to balance exploration/exploitation
5. **Checkpoint regularly** to save progress

## Dependencies

- PyTorch
- NumPy
- Python 3.8+

## Related Modules

- GNN module for dependency modeling
- Transformers module for forecasting
- LLM reasoning for high-level decisions
- Meta-Agent for orchestration

