# Meta-Agent Module

This module implements the Meta-Agent that orchestrates all AI components for intelligent decision-making.

## Overview

The Meta-Agent:
- Orchestrates RL, GNN, Transformers, and LLM components
- Combines recommendations from multiple sources
- Estimates confidence in decisions
- Routes problems to appropriate components
- Maintains memory of past decisions
- Generates comprehensive explanations

## Components

### `orchestrator.py` - Main Orchestrator
- **MetaAgentOrchestrator**: Main orchestrator class
- Features:
  - Combines all AI components
  - Makes final decisions
  - Generates explanations
  - Applies safety checks

### `decision_router.py` - Decision Routing
- **DecisionRouter**: Routes problems to appropriate components
- **AdaptiveRouter**: Learns optimal routing
- Features:
  - Problem classification
  - Component selection
  - Adaptive weight adjustment

### `confidence_estimator.py` - Confidence Estimation
- **ConfidenceEstimator**: Estimates decision confidence
- Features:
  - Combines component confidences
  - Calculates agreement
  - Historical performance adjustment
  - Uncertainty estimation

### `memory.py` - Memory System
- **DecisionMemory**: Stores decisions and outcomes
- **EpisodicMemory**: Stores complete episodes
- Features:
  - Decision history
  - Outcome tracking
  - Pattern learning
  - Similar decision retrieval

## Usage

### Basic Orchestration

```python
from ai_engine.meta_agent.orchestrator import MetaAgentOrchestrator
from ai_engine.rl.agent import RLAgent
from ai_engine.gnn.gnn_predictor import GNNPredictor
from ai_engine.transformers.forecasting import ForecastingPipeline
from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine

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
    system_state={...},
    failure_info={...},
    dependency_graph=graph,
    historical_metrics=metrics
)
```

### Decision Routing

```python
from ai_engine.meta_agent.decision_router import AdaptiveRouter

router = AdaptiveRouter()

# Route problem
routing_plan = router.route(
    problem_info={"type": "failure", "severity": "high"},
    available_components=["rl_agent", "llm_reasoning", "gnn"]
)
```

### Confidence Estimation

```python
from ai_engine.meta_agent.confidence_estimator import ConfidenceEstimator

estimator = ConfidenceEstimator()

# Estimate confidence
confidence, details = estimator.estimate_confidence(
    recommendations=[...],
    component_weights={"rl_agent": 0.4, "llm_reasoning": 0.6}
)
```

### Memory System

```python
from ai_engine.meta_agent.memory import DecisionMemory

memory = DecisionMemory()

# Store decision
decision_id = memory.store_decision(decision, context)

# Store outcome
memory.store_outcome(decision_id, outcome, success=True)

# Retrieve similar decisions
similar = memory.retrieve_similar_decisions(current_context, top_k=5)
```

## Decision Flow

1. **Problem Classification**: Router classifies problem type
2. **Component Selection**: Router selects appropriate components
3. **Parallel Analysis**: Components analyze problem simultaneously
4. **Recommendation Collection**: Gather recommendations from all components
5. **Confidence Estimation**: Estimate overall confidence
6. **Decision Combination**: Combine recommendations with weights
7. **Safety Checks**: Apply safety layer validation
8. **Explanation Generation**: Generate human-readable explanation
9. **Memory Storage**: Store decision for future learning

## Output Format

All decisions include:
- **action**: Recommended action
- **confidence**: Confidence score [0, 1]
- **reasoning**: Step-by-step reasoning
- **explanation**: Human-readable explanation
- **sources**: Components that contributed
- **warnings**: Safety warnings (if any)
- **expected_outcome**: What will happen

## Dependencies

- All other AI engine modules (RL, GNN, Transformers, LLM)
- NumPy
- Python 3.8+

## Related Modules

- RL module for learning optimal actions
- GNN module for dependency modeling
- Transformers module for forecasting
- LLM reasoning for high-level decisions

