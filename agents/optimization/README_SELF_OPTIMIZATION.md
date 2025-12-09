# Self-Optimization System

This document describes the self-optimization capabilities added to the Optimization Agent in Phase 10, Part 3.

## Overview

The self-optimization system enables the Optimization Agent to:
- **Continuously evaluate** resource usage and performance
- **Optimize cost functions** over time using real performance metrics
- **Predict load** and optimize auto-scaling decisions
- **Track cloud resources** and suggest cost-saving measures

## Components

### 1. Optimization Feedback System (`optimization_feedback.py`)

Continuously evaluates resource usage and optimizes cost function:

**Features**:
- Records resource metrics (CPU, memory, disk, network, response time, cost)
- Evaluates optimization actions and generates feedback
- Calculates optimization scores
- Generates recommendations
- Optimizes cost function weights over time

**Usage**:
```python
from agents.optimization.optimization_feedback import OptimizationFeedbackSystem

feedback_system = OptimizationFeedbackSystem()

# Record metrics
feedback_system.record_metrics(
    cpu_usage=0.65,
    memory_usage=0.70,
    disk_usage=0.50,
    network_io=100.0,
    response_time=0.5,
    throughput=1000.0,
    error_rate=0.01,
    cost_per_hour=10.0
)

# Evaluate optimization action
feedback = feedback_system.evaluate_optimization(
    action_taken="scale_down",
    resource_before=before_metrics,
    resource_after=after_metrics
)

# Get summary
summary = feedback_system.get_optimization_summary()
```

### 2. Auto-Scaling Optimizer (`autoscaling_optimizer.py`)

Optimizes scaling decisions based on load predictions:

**Features**:
- Load prediction using historical data
- Trend-based forecasting
- Optimized scaling decisions
- Threshold learning from feedback

**Usage**:
```python
from agents.optimization.autoscaling_optimizer import AutoScalingOptimizer

optimizer = AutoScalingOptimizer()

# Record load
optimizer.record_load(
    cpu_usage=0.75,
    memory_usage=0.70,
    request_rate=1000.0,
    current_replicas=5
)

# Get scaling decision
decision = optimizer.optimize_scaling_decision(
    current_cpu=0.75,
    current_memory=0.70,
    current_requests=1000.0,
    current_replicas=5
)

print(f"Action: {decision.action}, Target replicas: {decision.target_replicas}")
print(f"Reasoning: {decision.reasoning}")
```

### 3. Cloud Optimizer (`cloud_optimizer.py`)

Tracks cloud resources and suggests cost-saving measures:

**Features**:
- Resource registration and tracking
- Idle resource detection
- Underutilized resource analysis
- Reserved instance recommendations
- Spot instance opportunities
- Cost-saving recommendations

**Usage**:
```python
from agents.optimization.cloud_optimizer import CloudOptimizer

cloud_optimizer = CloudOptimizer()

# Register resource
cloud_optimizer.register_resource(
    resource_id="i-1234567890abcdef0",
    resource_type="ec2",
    region="us-east-1",
    instance_type="m5.large",
    cost_per_hour=0.10
)

# Update usage
cloud_optimizer.update_resource_usage(
    resource_id="i-1234567890abcdef0",
    cpu_usage=0.15,
    memory_usage=0.20,
    status="running"
)

# Generate recommendations
recommendations = cloud_optimizer.generate_cost_saving_recommendations()

for rec in recommendations:
    print(f"{rec.resource_id}: {rec.recommendation_type} - ${rec.potential_savings:.2f}/month")
```

### 4. Self-Optimization System (`self_optimization.py`)

Main orchestrator that coordinates all optimization components:

**Features**:
- Continuous optimization loop
- Metrics collection
- Cost analysis
- Integration with learning pipeline

**Usage**:
```python
from agents.optimization.self_optimization import SelfOptimizationSystem

self_opt = SelfOptimizationSystem()
self_opt.start()

# Record metrics (automatically processed)
self_opt.record_resource_metrics(
    cpu_usage=0.65,
    memory_usage=0.70,
    disk_usage=0.50,
    network_io=100.0,
    response_time=0.5,
    throughput=1000.0,
    error_rate=0.01,
    cost_per_hour=10.0
)

# Get scaling decision
decision = self_opt.get_scaling_decision(
    current_cpu=0.75,
    current_memory=0.70,
    current_requests=1000.0,
    current_replicas=5
)

# Get summary
summary = self_opt.get_optimization_summary()
```

## Integration with Optimization Agent

The self-optimization system is integrated into the Optimization Agent:

```python
from agents.optimization.agent import OptimizationAgent

agent = OptimizationAgent()
agent.start()

# Record metrics
agent.record_resource_metrics(
    cpu_usage=0.65,
    memory_usage=0.70,
    disk_usage=0.50,
    network_io=100.0,
    response_time=0.5,
    throughput=1000.0,
    error_rate=0.01,
    cost_per_hour=10.0
)

# Get scaling decision
decision = agent.get_scaling_decision(
    current_cpu=0.75,
    current_memory=0.70,
    current_requests=1000.0,
    current_replicas=5
)

# Get cost recommendations
recommendations = agent.get_cost_recommendations()

# Get optimization summary
summary = agent.get_optimization_summary()
```

## Cost-Saving Recommendations

### Types of Recommendations

1. **Terminate Idle Resources**
   - Resources idle for >24 hours
   - 100% cost savings
   - Low risk

2. **Resize Underutilized Resources**
   - Resources with <20% utilization
   - ~50% cost savings
   - Medium risk

3. **Reserved Instances**
   - Resources with >80% uptime
   - ~40% cost savings
   - Low risk

4. **Spot Instances**
   - Fault-tolerant workloads
   - ~70% cost savings
   - Medium risk

## Load Prediction

The auto-scaling optimizer uses trend-based prediction:

- **Method**: Linear trend analysis on historical data
- **Horizon**: 5 minutes (configurable)
- **Confidence**: Based on data stability
- **Updates**: Continuously as new data arrives

## Optimization Feedback

The feedback system evaluates optimization actions:

- **Optimization Score**: Combines cost, performance, utilization, and error rate
- **Recommendations**: Actionable suggestions for improvement
- **Cost Function**: Continuously optimized based on feedback

## Best Practices

1. **Regular Metrics Collection**: Collect metrics every minute
2. **Review Recommendations**: Regularly review cost-saving recommendations
3. **Monitor Optimization Scores**: Track optimization performance
4. **Validate Predictions**: Verify load predictions are accurate
5. **Gradual Implementation**: Implement recommendations gradually

## Next Steps

1. **Integrate with Monitoring**: Connect to Prometheus/Grafana
2. **Implement ML Predictions**: Use LSTM/ARIMA for better load prediction
3. **Automated Actions**: Automatically implement low-risk recommendations
4. **Cost Tracking**: Track actual savings from recommendations
5. **Reporting**: Generate optimization reports

