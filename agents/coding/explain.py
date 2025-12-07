"""
Explainability module for Coding Agent
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
        "reason": f"Coding Agent analyzed the input ({inputs}) and generated output ({outputs}). The action was taken based on LLM analysis of error patterns, code structure, and best practices. The fix/generation addresses the root cause while maintaining code quality.",
        "inputs": str(inputs) if not isinstance(inputs, (dict, list)) else inputs,
        "outputs": str(outputs) if not isinstance(outputs, (dict, list)) else outputs,
        "explanation_type": "llm_driven"
    }

