"""
Explainability module for Security Agent
"""

from typing import Any, Dict


def explain_action(agent_name: str, inputs: Any, outputs: Any = None) -> Dict[str, Any]:
    """
    Provide human-readable explanation for agent actions
    
    Args:
        agent_name: Name of the agent
        inputs: Input data that led to the action
        outputs: Output/result of the action
    
    Returns:
        Dict with explanation details in human-readable format
    """
    # Extract problem, action, and reason from inputs/outputs
    problem = "a security threat was detected"
    action = "blocked the threat"
    reason = "to prevent potential security breach"
    
    # Parse inputs to extract threat details
    if isinstance(inputs, (list, dict)):
        if isinstance(inputs, list) and len(inputs) > 0:
            # Security logs
            threat_count = len(inputs)
            if threat_count > 0:
                first_threat = inputs[0] if isinstance(inputs[0], dict) else {}
                if "source_ip" in first_threat:
                    ip = first_threat.get("source_ip", "unknown")
                    problem = f"suspicious activity was detected from IP {ip}"
                if "action" in first_threat:
                    threat_action = first_threat.get("action", "")
                    if "failed_login" in threat_action:
                        problem = f"multiple failed login attempts were detected"
        elif isinstance(inputs, dict):
            if "threats" in inputs:
                threats = inputs.get("threats", [])
                if len(threats) > 0:
                    problem = f"{len(threats)} security threat(s) were detected"
    
    # Parse outputs to extract action details
    if isinstance(outputs, dict):
        if "action" in outputs:
            action = outputs.get("action", "blocked the threat")
        if "blocked_ip" in outputs:
            ip = outputs.get("blocked_ip", "")
            action = f"blocked IP address {ip}"
        if "severity" in outputs:
            severity = outputs.get("severity", "medium")
            if severity == "high":
                reason = "to prevent a critical security breach"
    
    # Build human-readable explanation
    explanation = f"The agent detected that {problem} and {action} {reason}."
    
    return {
        "agent": agent_name,
        "message": "Action automatically executed.",
        "explanation": explanation,
        "reason": explanation,
        "inputs": str(inputs) if not isinstance(inputs, (dict, list)) else inputs,
        "outputs": str(outputs) if not isinstance(outputs, (dict, list)) else outputs,
        "explanation_type": "security_analysis"
    }

