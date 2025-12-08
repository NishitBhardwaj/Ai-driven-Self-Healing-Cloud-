# Graph Neural Network Module

This module implements Graph Neural Networks (GNNs) for modeling service dependencies and predicting failure propagation in the cloud infrastructure.

## Overview

The GNN module:
- Models service dependencies as graphs
- Predicts failure propagation
- Identifies critical services
- Analyzes impact of failures
- Recommends healing priorities

## Components

### `graph_builder.py` - Graph Construction
- **DependencyGraph**: Represents service dependency graph
- **GraphBuilder**: Builds graphs from Kubernetes resources or config
- Features:
  - Node and edge management
  - PyTorch Geometric conversion
  - Subgraph extraction
  - Failure impact analysis

### `gnn_model.py` - GNN Models
- **GNNModel**: Base GNN model (GCN, GAT, or GIN)
- **FailurePropagationPredictor**: Predicts failure propagation
- **DependencyAnalyzer**: Analyzes service criticality
- **ImpactPredictor**: Predicts impact of failures

### `gnn_predictor.py` - High-Level Interface
- **GNNPredictor**: Main interface for GNN-based predictions
- Features:
  - Failure propagation prediction
  - Dependency analysis
  - Impact prediction
  - Healing priority recommendation

## Usage

### Building a Dependency Graph

```python
from ai_engine.gnn.graph_builder import GraphBuilder

# From Kubernetes resources
graph = GraphBuilder.build_from_kubernetes(
    deployments=deployment_list,
    services=service_list,
    pods=pod_list
)

# From configuration
graph = GraphBuilder.build_from_config(config_dict)
```

### Predicting Failure Propagation

```python
from ai_engine.gnn.gnn_predictor import GNNPredictor

predictor = GNNPredictor()

# Predict which services will fail
failure_probs = predictor.predict_failure_propagation(
    graph=graph,
    failed_service="compute-service"
)
```

### Analyzing Dependencies

```python
# Get critical services
critical_services = predictor.get_critical_services(
    graph=graph,
    threshold=0.7,
    top_k=10
)

# Analyze impact
impact = predictor.predict_impact(
    graph=graph,
    failed_service="storage-service"
)
```

### Recommending Healing Priority

```python
# Get healing priority recommendation
priorities = predictor.recommend_healing_priority(
    graph=graph,
    failed_services=["service1", "service2"]
)
```

## Graph Structure

### Nodes (Services)
- Service ID
- Service type
- Features: CPU, memory, health, request rate, error rate

### Edges (Dependencies)
- Source service
- Target service
- Dependency type (depends_on, communicates_with)
- Weight
- Features: latency, request count

## Model Architecture

### GNN Types
- **GCN**: Graph Convolutional Network (default)
- **GAT**: Graph Attention Network
- **GIN**: Graph Isomorphism Network

### Model Components
1. **GNN Encoder**: Learns node embeddings
2. **Failure Predictor**: Classifies failure probability
3. **Dependency Analyzer**: Scores service criticality
4. **Impact Predictor**: Predicts failure impact

## Training

Models can be trained on historical failure data:

```python
# Training code would go here
# Uses supervised learning on failure propagation data
```

## Dependencies

- PyTorch
- PyTorch Geometric
- NetworkX
- NumPy

## Related Modules

- RL module for learning optimal actions
- Transformers module for forecasting
- LLM reasoning for high-level decisions
- Meta-Agent for orchestration

