"""
Explainability module for Security Agent
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
        "reason": f"Security Agent analyzed security logs and threat patterns (inputs={inputs}). Generated security response (outputs={outputs}). The action was determined based on threat detection algorithms, policy validation, and security best practices.",
        "inputs": str(inputs) if not isinstance(inputs, (dict, list)) else inputs,
        "outputs": str(outputs) if not isinstance(outputs, (dict, list)) else outputs,
        "explanation_type": "security_analysis"
    }

