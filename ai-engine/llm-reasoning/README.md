# LLM Reasoning Module

This module implements LLM-based reasoning for high-level decision-making in the self-healing cloud system.

## Overview

The LLM Reasoning module:
- Generates high-level plans for healing and scaling
- Provides step-by-step chain-of-thought reasoning
- Generates human-readable explanations
- Ensures safety through validation layers

## Components

### `planner.py` - LLM Planner
- **LLMPlanner**: High-level planning using LLM
- Features:
  - Healing strategy planning
  - Scaling strategy planning
  - Explanation generation
  - Rule-based fallback

### `chain_of_thought.py` - Chain of Thought Reasoning
- **ChainOfThoughtReasoner**: Step-by-step reasoning
- Steps:
  1. Problem identification
  2. Situation analysis
  3. Option generation
  4. Option evaluation
  5. Decision making

### `reasoning_engine.py` - Main Interface
- **ReasoningEngine**: Main reasoning interface
- Features:
  - Failure reasoning
  - Scaling reasoning
  - Explanation generation
  - Decision validation
  - Decision refinement

### `safety_layer.py` - Safety Checks
- **SafetyLayer**: Safety validation
- Features:
  - Input validation
  - Output sanitization
  - Safety checks
  - Dangerous action detection
  - Fallback mechanisms

## Usage

### Basic Planning

```python
from ai_engine.llm_reasoning.planner import LLMPlanner

planner = LLMPlanner(llm_client=llm_client)

# Plan healing strategy
plan = planner.plan_healing_strategy(
    failure_info={"type": "pod_crash", "severity": "high"},
    system_state={"cpu": 80, "memory": 75},
    available_actions=["restart_pod", "rollback_deployment"]
)
```

### Chain of Thought Reasoning

```python
from ai_engine.llm_reasoning.chain_of_thought import ChainOfThoughtReasoner

reasoner = ChainOfThoughtReasoner(llm_client=llm_client)

# Perform reasoning
result = reasoner.reason(
    problem={"type": "resource_exhaustion"},
    context={"metrics": {...}}
)
```

### Complete Reasoning Engine

```python
from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine

engine = ReasoningEngine(llm_client=llm_client, use_cot=True)

# Reason about failure
decision = engine.reason_about_failure(
    failure_info={...},
    system_state={...},
    available_actions=[...]
)

# Generate explanation
explanation = engine.explain_action(
    action="restart_pod",
    context={...}
)
```

### Safety Layer

```python
from ai_engine.llm_reasoning.safety_layer import SafetyLayer

safety = SafetyLayer(allowed_actions=[...])

# Apply safety checks
safe_decision = safety.apply_safety_checks(decision, context)

# Get safety report
report = safety.get_safety_report(decision, context)
```

## LLM Integration

The module is designed to work with various LLM providers:

- OpenAI GPT models
- Anthropic Claude
- Local LLM models
- Rule-based fallback (when LLM unavailable)

## Safety Features

1. **Input Validation**: Checks for malicious patterns
2. **Output Sanitization**: Ensures safe actions
3. **Dangerous Action Detection**: Flags risky operations
4. **Confidence Thresholds**: Requires review for high-confidence decisions
5. **Fallback Mechanisms**: Safe defaults when LLM fails

## Dependencies

- Python 3.8+
- LLM client library (OpenAI, Anthropic, etc.)
- JSON handling

## Related Modules

- RL module for learning optimal actions
- GNN module for dependency modeling
- Transformers module for forecasting
- Meta-Agent for orchestration

