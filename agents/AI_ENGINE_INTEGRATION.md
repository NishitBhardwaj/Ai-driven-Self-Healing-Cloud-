# AI Engine Integration for Agents

This document describes how agents are connected to the AI Engine (Phase 5).

## Overview

All agents have been updated to use the hybrid AI engine components:
- **Reinforcement Learning (RL)**: For action selection and policy learning
- **Graph Neural Networks (GNN)**: For dependency modeling and failure propagation
- **Transformers**: For workload forecasting and anomaly detection
- **LLM Reasoning**: For high-level decision-making and explanations
- **Meta-Agent Memory**: For learning from past decisions

## Agent Integrations

### 1. Self-Healing Agent

**Location**: `agents/self-healing/`

**AI Components Used**:
- RL Agent: Chooses optimal healing actions based on system state
- GNN Predictor: Analyzes dependency graphs to predict failure propagation
- LLM Reasoning: Provides deep reasoning and explanations for healing decisions

**Integration Files**:
- `ai_integration.py`: Python integration module
- `ai_integration_wrapper.py`: Python wrapper for Go agent calls
- `heal.go`: Updated to call AI integration

**Usage**:
```python
from ai_integration import SelfHealingAIIntegration

integration = SelfHealingAIIntegration()
decision = integration.decide_healing_action(
    failure_info={"service_id": "api-service", "type": "crash"},
    system_state={"cpu_usage": 0.9, "error_rate": 0.1},
    dependency_graph_data={"kubernetes": {...}, "localstack": {...}}
)
```

### 2. Scaling Agent

**Location**: `agents/scaling/`

**AI Components Used**:
- Transformer Forecasting: Predicts CPU, latency, memory risk, and error bursts 5 minutes ahead

**Integration Files**:
- `ai_integration.py`: Python integration module
- `ai_integration_wrapper.py`: Python wrapper for Go agent calls
- `autoscale.go`: Updated to use Transformer predictions

**Usage**:
```python
from ai_integration import ScalingAIIntegration

integration = ScalingAIIntegration()
recommendation = integration.get_scaling_recommendation(
    historical_metrics={
        "cpu": np.array([...]),
        "memory": np.array([...]),
        "latency": np.array([...])
    },
    current_replicas=2
)
```

### 3. Coding Agent

**Location**: `agents/coding/`

**AI Components Used**:
- LLM Reasoning: Analyzes code errors and generates fixes
- Meta-Agent Memory: Learns from past successful fixes

**Integration Files**:
- `ai_integration.py`: Python integration module
- `agent.py`: Updated to use AI integration

**Usage**:
```python
from ai_integration import CodingAIIntegration

integration = CodingAIIntegration()
fix_result = integration.analyze_and_fix_code(
    error_info={"stacktrace": "...", "error_logs": "..."},
    code_context={"file_path": "app.py", "file_content": "..."}
)
```

### 4. Security Agent

**Location**: `agents/security/`

**AI Components Used**:
- GNN Dependencies: Analyzes dependency graphs to identify critical services
- LLM Threat Model: Classifies threats and generates response plans

**Integration Files**:
- `ai_integration.py`: Python integration module
- `agent.py`: Updated to use AI integration

**Usage**:
```python
from ai_integration import SecurityAIIntegration

integration = SecurityAIIntegration()
threat_result = integration.detect_threat(
    security_logs=[...],
    dependency_graph_data={"kubernetes": {...}},
    network_traffic={...}
)
```

### 5. Performance Monitoring Agent

**Location**: `agents/performance-monitoring/`

**AI Components Used**:
- All Models: Feeds metrics data to RL, GNN, Transformers, and LLM

**Integration Files**:
- `ai_integration.py`: Python integration module
- `ai_integration_wrapper.py`: Python wrapper for Go agent calls
- `metrics.go`: Updated to feed data to all models

**Usage**:
```python
from ai_integration import MonitoringAIIntegration

integration = MonitoringAIIntegration()
results = integration.feed_metrics_to_models(
    metrics={"cpu": [...], "memory": [...], "latency": [...]},
    dependency_graph_data={...}
)
```

## Go-Python Integration

Go agents call Python AI integration via subprocess:

```go
cmd := exec.Command("python3", scriptPath, "command")
cmd.Stdin = bytes.NewReader(inputJSON)
output, err := cmd.Output()
```

## Configuration

Set environment variables for API keys:

```bash
export OPENROUTER_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

## Model Checkpoints

Place trained model checkpoints in:
- RL: `ai-engine/rl/checkpoints/`
- GNN: `ai-engine/gnn/checkpoints/`
- Transformers: `ai-engine/transformers/checkpoints/`

## Next Steps

1. Train models using Phase 4 metrics
2. Deploy agents with AI integration enabled
3. Monitor AI decision quality and confidence scores
4. Fine-tune models based on real-world performance

