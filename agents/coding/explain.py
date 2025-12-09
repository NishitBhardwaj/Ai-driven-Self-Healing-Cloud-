"""
Explainability module for Coding Agent
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
    problem = "a code error was detected"
    action = "generated a fix"
    reason = "to resolve the error and restore functionality"
    
    # Parse inputs to extract error details
    if isinstance(inputs, dict):
        if "stacktrace" in inputs:
            error_type = inputs.get("stacktrace", "").split(":")[0] if inputs.get("stacktrace") else "error"
            problem = f"a {error_type} was detected"
        if "file_path" in inputs:
            file_path = inputs.get("file_path", "")
            if file_path:
                problem = f"a code error was detected in {file_path}"
    
    # Parse outputs to extract action details
    if isinstance(outputs, dict):
        if "action" in outputs:
            action = outputs.get("action", "generated a fix")
        if "patch" in outputs:
            action = "applied a code patch"
        if "fix_suggestions" in outputs:
            action = "generated fix suggestions"
    
    # Build human-readable explanation
    explanation = f"The agent detected that {problem} and {action} {reason}."
    
    return {
        "agent": agent_name,
        "message": "Action automatically executed.",
        "explanation": explanation,
        "reason": explanation,
        "inputs": str(inputs) if not isinstance(inputs, (dict, list)) else inputs,
        "outputs": str(outputs) if not isinstance(outputs, (dict, list)) else outputs,
        "explanation_type": "llm_driven"
    }

