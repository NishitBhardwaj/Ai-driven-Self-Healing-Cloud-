# AI Engine - Hybrid AI System for Self-Healing Cloud

## Overview

This is a comprehensive hybrid AI engine that combines multiple AI techniques for intelligent cloud infrastructure management:

- **Reinforcement Learning (RL)**: Learns optimal healing and scaling strategies
- **Graph Neural Networks (GNN)**: Models service dependencies and predicts failure propagation
- **Transformers**: Detects anomalies and forecasts workload
- **LLM Reasoning**: Provides high-level decision-making and explanations
- **Meta-Agent**: Orchestrates all components for unified decision-making

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Meta-Agent                             │
│  (Orchestrator, Router, Confidence, Memory)              │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼──────────┐ ┌───────────┐
│  RL   │ │  GNN  │ │ Transformers │ │ LLM       │
│ Agent │ │       │ │              │ │ Reasoning │
└───────┘ └───────┘ └──────────────┘ └───────────┘
```

## Modules

### 1. Reinforcement Learning (`/rl/`)

**Purpose**: Learn optimal actions through trial and error

**Components**:
- `agent.py`: DQN agent with experience replay
- `environment.py`: Cloud system simulation
- `trainer.py`: Training loop and evaluation
- `reward_functions.py`: Multiple reward function types
- `state_encoder.py`: State feature encoding

**Key Features**:
- Deep Q-Network (DQN) with target network
- Epsilon-greedy exploration
- Experience replay buffer
- Multiple reward functions (basic, shaped, sparse, multi-objective)

### 2. Graph Neural Networks (`/gnn/`)

**Purpose**: Model service dependencies and predict failure propagation

**Components**:
- `graph_builder.py`: Build dependency graphs
- `gnn_model.py`: GNN models (GCN, GAT, GIN)
- `gnn_predictor.py`: High-level prediction interface

**Key Features**:
- Service dependency modeling
- Failure propagation prediction
- Impact analysis
- Critical service identification
- Healing priority recommendation

### 3. Transformers (`/transformers/`)

**Purpose**: Anomaly detection and workload forecasting

**Components**:
- `model.py`: Transformer models
- `dataset.py`: Time series data handling
- `forecasting.py`: High-level forecasting interface

**Key Features**:
- Anomaly detection in metrics
- Workload forecasting
- Multi-task learning
- Scaling recommendations

### 4. LLM Reasoning (`/llm-reasoning/`)

**Purpose**: High-level decision-making and explanations

**Components**:
- `planner.py`: LLM-based planning
- `chain_of_thought.py`: Step-by-step reasoning
- `reasoning_engine.py`: Main reasoning interface
- `safety_layer.py`: Safety validation

**Key Features**:
- Healing strategy planning
- Scaling strategy planning
- Chain-of-thought reasoning
- Explanation generation
- Safety checks and validation

### 5. Meta-Agent (`/meta-agent/`)

**Purpose**: Orchestrate all AI components

**Components**:
- `orchestrator.py`: Main orchestrator
- `decision_router.py`: Route problems to components
- `confidence_estimator.py`: Estimate decision confidence
- `memory.py`: Store decisions and learn patterns

**Key Features**:
- Multi-component decision fusion
- Problem classification and routing
- Confidence estimation
- Decision memory and learning
- Comprehensive explanations

## Quick Start

### Installation

```bash
pip install torch torch-geometric numpy
# For LLM: pip install openai anthropic (or your LLM client)
```

### Basic Usage

```python
from ai_engine.meta_agent import MetaAgentOrchestrator
from ai_engine.rl import RLAgent
from ai_engine.gnn import GNNPredictor
from ai_engine.transformers import ForecastingPipeline
from ai_engine.llm_reasoning import ReasoningEngine

# Initialize components
rl_agent = RLAgent(state_dim=19, action_dim=6)
gnn_predictor = GNNPredictor()
forecasting = ForecastingPipeline()
reasoning = ReasoningEngine()

# Create orchestrator
orchestrator = MetaAgentOrchestrator(
    rl_agent=rl_agent,
    gnn_predictor=gnn_predictor,
    forecasting_pipeline=forecasting,
    reasoning_engine=reasoning
)

# Make decision
decision = orchestrator.make_decision(
    system_state={
        "pod_count": 10,
        "healthy_pods": 8,
        "failed_pods": 2,
        "cpu_usage": 85.0,
        "memory_usage": 80.0,
        "error_rate": 5.0
    },
    failure_info={
        "type": "pod_crash",
        "service_id": "compute-service",
        "severity": "high"
    }
)

print(f"Action: {decision['action']}")
print(f"Confidence: {decision['confidence']:.2f}")
print(f"Explanation: {decision['explanation']}")
```

## Decision Output Format

All decisions include:

```python
{
    "action": "restart_pod",           # Recommended action
    "confidence": 0.85,                 # Confidence [0, 1]
    "reasoning": "...",                 # Step-by-step reasoning
    "explanation": "...",              # Human-readable explanation
    "sources": ["rl_agent", "llm"],   # Contributing components
    "warnings": [],                    # Safety warnings
    "expected_outcome": "...",         # Expected result
    "safety_checked": True,            # Safety validation status
    "is_safe": True                    # Safety status
}
```

## Training

### RL Agent Training

```python
from ai_engine.rl import RLTrainer, RLEnvironment, RLAgent

agent = RLAgent(state_dim=19, action_dim=6)
env = RLEnvironment()
trainer = RLTrainer(agent, env)

stats = trainer.train(num_episodes=1000)
```

### GNN Training

```python
# Training code would use PyTorch training loop
# with dependency graphs and failure propagation data
```

### Transformer Training

```python
# Training code would use PyTorch training loop
# with time series datasets
```

## Dependencies

- **PyTorch**: Deep learning framework
- **PyTorch Geometric**: Graph neural networks
- **NumPy**: Numerical computing
- **NetworkX**: Graph operations (for GNN)
- **LLM Client**: OpenAI, Anthropic, or local models

## Integration with Cloud Agents

The AI engine integrates with cloud agents:

```python
# Self-Healing Agent
from agents.self_healing.cloud_adapter import CloudAdapter
from ai_engine.meta_agent import MetaAgentOrchestrator

# Scaling Agent
from agents.scaling.k8s_scaling import K8sScaling
from ai_engine.transformers import ForecastingPipeline

# Performance Monitoring Agent
from agents.performance_monitoring.metrics_adapter import MetricsAdapter
from ai_engine.transformers import AnomalyDetectionEngine
```

## Performance Considerations

- **RL Agent**: Requires training on historical data
- **GNN**: Needs dependency graph construction
- **Transformers**: Requires time series data
- **LLM**: May have API latency (use caching)
- **Meta-Agent**: Combines all components (may be slower)

## Future Enhancements

- [ ] Online learning for RL agent
- [ ] Real-time GNN updates
- [ ] Federated learning support
- [ ] Multi-cloud deployment
- [ ] Advanced explanation generation
- [ ] Human-in-the-loop feedback

## License

Part of the AI-Driven Self-Healing Cloud project.

