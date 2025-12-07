# Optimization Agent

## Purpose

The Optimization Agent is responsible for:
- Reducing infrastructure costs
- Suggesting infrastructure improvements
- Analyzing resource utilization
- Providing cost optimization recommendations

## Responsibilities

1. **Cost Analysis**: Analyzes current infrastructure costs
2. **Optimization Recommendations**: Suggests cost reduction strategies
3. **Architecture Recommendations**: Recommends infrastructure improvements
4. **Resource Optimization**: Identifies underutilized resources

## Functions

- `optimize_cost()` - Optimize infrastructure costs
- `recommend_architecture()` - Recommend architecture improvements
- `llm_call()` - Make LLM API calls for analysis

## Input

- Infrastructure configuration
- Current cost data
- System requirements
- Constraints (budget, technical)

## Output

- Cost optimization recommendations
- Potential savings estimates
- Architecture improvement suggestions

## LLM Integration

Uses shared `llm.py` module supporting:
- OpenRouter (default)
- Google Gemini

## Usage

```python
from agent import OptimizationAgent

agent = OptimizationAgent()
agent.start()

# Optimize costs
result = agent.optimize_cost(
    infrastructure_data={"instances": 10},
    current_costs={"monthly": 1000.0}
)

# Get architecture recommendations
recommendations = agent.recommend_architecture(
    requirements={"expected_traffic": 5000}
)
```

