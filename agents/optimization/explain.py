"""
Explainability module for Optimization Agent
"""

from typing import Any, Dict


def explain_action(agent_name: str, inputs: Any, outputs: Any) -> Dict[str, Any]:
    """
    Provide explanation for agent actions
    
    Args:
        agent_name: Name of the agent
        inputs: Input data that led to the action
        outputs: Output/result of the action
    
    Returns:
        Dict with explanation details
    """
    return {
        "agent": agent_name,
        "reason": f"Optimization Agent analyzed infrastructure usage and costs (inputs={inputs}). Generated optimization recommendations (outputs={outputs}). The recommendations are based on cost analysis, resource utilization patterns, and performance metrics to balance efficiency with requirements.",
        "inputs": str(inputs) if not isinstance(inputs, (dict, list)) else inputs,
        "outputs": str(outputs) if not isinstance(outputs, (dict, list)) else outputs,
        "explanation_type": "cost_optimization"
    }

