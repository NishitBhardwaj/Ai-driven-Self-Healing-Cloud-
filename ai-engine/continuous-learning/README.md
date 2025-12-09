# Continuous Learning Framework

This directory contains the continuous learning framework that enables the AI-Driven Self-Healing Cloud system to learn from real-world operations and improve over time.

## Overview

The continuous learning framework provides:
- **Data Collection**: Collects operational data from all agents
- **Reinforcement Learning Feedback**: Updates agent policies based on outcomes
- **Model Retraining**: Triggers model retraining when needed
- **Performance Optimization**: Continuously optimizes agent behaviors

## Components

### 1. Data Collector (`data_collector.py`)

Collects real-world operational data:
- **Agent Actions**: Action types, inputs, outputs, success/failure
- **Performance Metrics**: CPU, memory, response time, throughput
- **Task Results**: Task execution outcomes and errors

**Usage**:
```python
from ai_engine.continuous_learning import DataCollector

collector = DataCollector()

# Collect an action
collector.collect_action(
    agent_name="self-healing",
    action_type="restart_service",
    input_data={"service": "api-server"},
    output_data={"status": "restarted"},
    success=True,
    execution_time=2.5,
    confidence=0.95,
    explanation="Service restarted successfully"
)

# Collect metrics
collector.collect_metric(
    agent_name="self-healing",
    cpu_usage=45.2,
    memory_usage=60.1,
    response_time=0.5,
    throughput=100.0,
    error_rate=0.01,
    success_rate=0.98
)
```

### 2. RL Feedback Loop (`rl_feedback_loop.py`)

Implements reinforcement learning feedback for policy updates:

**Base RL Feedback Loop**:
```python
from ai_engine.continuous_learning import RLFeedbackLoop

feedback_loop = RLFeedbackLoop("self-healing")

# Update reward based on action outcome
reward = feedback_loop.update_reward(
    success=True,
    recovery_time=2.5,
    action_type="restart_service"
)

# Get success rate
success_rate = feedback_loop.get_success_rate()

# Get policy recommendations
recommendations = feedback_loop.get_policy_recommendations()
```

**Self-Healing Agent Feedback**:
```python
from ai_engine.continuous_learning import SelfHealingRLFeedback

healing_feedback = SelfHealingRLFeedback()

reward = healing_feedback.update_healing_feedback(
    success=True,
    recovery_time=2.5,
    healing_action="restart_service",
    failure_type="service_crash"
)
```

**Scaling Agent Feedback**:
```python
from ai_engine.continuous_learning import ScalingRLFeedback

scaling_feedback = ScalingRLFeedback()

reward = scaling_feedback.update_scaling_feedback(
    success=True,
    recovery_time=10.0,
    scaling_action="scale_up",
    resource_utilization=0.75
)
```

### 3. Learning Pipeline (`learning_pipeline.py`)

Orchestrates the continuous learning process:

```python
from ai_engine.continuous_learning import LearningPipeline

# Initialize pipeline
pipeline = LearningPipeline()

# Start continuous learning
pipeline.start()

# Record actions (automatically triggers feedback)
pipeline.record_action(
    agent_name="self-healing",
    action_type="restart_service",
    input_data={"service": "api-server"},
    output_data={"status": "restarted"},
    success=True,
    execution_time=2.5,
    confidence=0.95,
    explanation="Service restarted successfully"
)

# Get performance summary
summary = pipeline.get_performance_summary()
```

## Reward Configuration

Customize reward calculation:

```python
from ai_engine.continuous_learning import RewardConfig, RLFeedbackLoop

# Custom reward configuration
reward_config = RewardConfig(
    success_reward=10.0,
    failure_penalty=-10.0,
    slow_recovery_penalty=-2.0,
    fast_recovery_bonus=2.0,
    recovery_time_threshold=5.0,
    repeated_failure_penalty=-5.0
)

feedback_loop = RLFeedbackLoop("self-healing", reward_config)
```

## Integration with Agents

### Example: Self-Healing Agent Integration

```python
from ai_engine.continuous_learning import LearningPipeline

# Initialize pipeline (singleton pattern recommended)
pipeline = LearningPipeline()
pipeline.start()

class SelfHealingAgent:
    def __init__(self):
        self.pipeline = pipeline
    
    def perform_healing(self, service_name: str):
        start_time = time.time()
        
        try:
            # Perform healing action
            result = self.restart_service(service_name)
            success = result is not None
            execution_time = time.time() - start_time
            
            # Record action for learning
            self.pipeline.record_action(
                agent_name="self-healing",
                action_type="restart_service",
                input_data={"service": service_name},
                output_data={"result": result},
                success=success,
                execution_time=execution_time,
                confidence=0.9,
                explanation=f"Service {service_name} restarted",
                context={"failure_type": "service_crash"}
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure for learning
            self.pipeline.record_action(
                agent_name="self-healing",
                action_type="restart_service",
                input_data={"service": service_name},
                output_data={"error": str(e)},
                success=False,
                execution_time=execution_time,
                confidence=0.0,
                explanation=f"Failed to restart {service_name}: {e}",
                context={"failure_type": "service_crash", "error": str(e)}
            )
            
            raise
```

## Data Storage

Data is stored in JSONL format:
- `actions_YYYYMMDD_HHMMSS.jsonl`: Agent actions
- `metrics_YYYYMMDD_HHMMSS.jsonl`: Performance metrics
- `tasks_YYYYMMDD_HHMMSS.jsonl`: Task results
- `{agent_name}_feedback_TIMESTAMP.json`: Feedback history

## Performance Monitoring

Monitor learning progress:

```python
# Get performance summary
summary = pipeline.get_performance_summary()

for agent_name, metrics in summary["agents"].items():
    print(f"{agent_name}:")
    print(f"  Success Rate: {metrics['success_rate']:.2%}")
    print(f"  Average Reward: {metrics['average_reward']:.2f}")
    print(f"  Total Actions: {metrics['total_actions']}")
    
    if metrics['recommendations']:
        print("  Recommendations:")
        for rec in metrics['recommendations']:
            print(f"    - {rec['suggestion']}")
```

## Model Retraining

The pipeline automatically checks if models need retraining:

- **Minimum Episodes**: 1000 actions
- **Success Rate Threshold**: 80%
- **Retrain Interval**: 1 hour (configurable)

Retraining triggers are saved to `retrain_{agent_name}_{timestamp}.json`.

## Best Practices

1. **Record All Actions**: Record both successful and failed actions
2. **Include Context**: Provide rich context for better learning
3. **Monitor Performance**: Regularly check performance summaries
4. **Adjust Rewards**: Tune reward configuration based on domain
5. **Review Recommendations**: Act on policy recommendations

## Next Steps

1. **Integrate with Agents**: Add learning pipeline to all agents
2. **Implement Model Retraining**: Create model retraining system
3. **Set Up Monitoring**: Monitor learning progress
4. **Tune Rewards**: Adjust reward configuration
5. **Review Feedback**: Analyze feedback data regularly

