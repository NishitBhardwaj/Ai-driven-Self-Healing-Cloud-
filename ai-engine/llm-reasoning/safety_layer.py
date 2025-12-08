"""
Safety Layer for LLM Reasoning
Ensures: no unsafe instructions, no deletion of important resources, no infinite scaling
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
import re

logger = logging.getLogger(__name__)


class SafetyLayer:
    """
    Safety layer for LLM reasoning
    
    Ensures:
    - No unsafe instructions
    - No deletion of important resources
    - No infinite scaling
    - Security-aware correction
    """
    
    def __init__(
        self,
        allowed_actions: Optional[List[str]] = None,
        max_replicas: int = 20,
        min_replicas: int = 1,
        protected_resources: Optional[List[str]] = None
    ):
        """
        Initialize safety layer
        
        Args:
            allowed_actions: List of allowed actions
            max_replicas: Maximum allowed replicas (prevents infinite scaling)
            min_replicas: Minimum allowed replicas
            protected_resources: List of protected resource names (cannot be deleted)
        """
        self.allowed_actions = allowed_actions or [
            "restart_pod", "rollback_deployment", "replace_pod",
            "rebuild_deployment", "trigger_heal", "trigger_code_fix",
            "scale_up", "scale_down", "do_nothing"
        ]
        self.max_replicas = max_replicas
        self.min_replicas = min_replicas
        self.protected_resources = protected_resources or [
            "database", "storage", "backup", "critical-service"
        ]
        
        # Unsafe action patterns
        self.unsafe_patterns = [
            r"delete\s+(service|deployment|pod|namespace)",
            r"rm\s+-rf",
            r"format\s+disk",
            r"shutdown\s+all",
            r"kill\s+all",
            r"drop\s+database",
            r"truncate\s+table"
        ]
        
        # Dangerous actions
        self.dangerous_actions = [
            "delete_service",
            "delete_deployment",
            "delete_namespace",
            "delete_pod",
            "drop_database",
            "format_disk",
            "shutdown_all"
        ]
        
        logger.info("SafetyLayer initialized")
    
    def validate_action(
        self,
        action: str,
        action_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate action for safety
        
        Args:
            action: Action to validate
            action_params: Action parameters
        
        Returns:
            Tuple of (is_safe, error_message, corrected_action)
        """
        action_params = action_params or {}
        corrected_action = {"action": action, **action_params}
        
        # Check 1: Action is in allowed list
        if action not in self.allowed_actions:
            return False, f"Action '{action}' is not in allowed actions list", corrected_action
        
        # Check 2: No deletion of important resources
        if self._is_deletion_action(action, action_params):
            resource_name = action_params.get("resource_name", "").lower()
            if any(protected in resource_name for protected in self.protected_resources):
                return False, f"Cannot delete protected resource: {resource_name}", corrected_action
        
        # Check 3: No infinite scaling
        if "scale" in action:
            target_replicas = action_params.get("target_replicas", action_params.get("replicas", 0))
            if target_replicas > self.max_replicas:
                corrected_action["target_replicas"] = self.max_replicas
                return False, f"Target replicas {target_replicas} exceeds maximum {self.max_replicas}", corrected_action
            if target_replicas < self.min_replicas:
                corrected_action["target_replicas"] = self.min_replicas
                return False, f"Target replicas {target_replicas} below minimum {self.min_replicas}", corrected_action
        
        # Check 4: No unsafe instructions in parameters
        params_str = str(action_params)
        if self._contains_unsafe_patterns(params_str):
            return False, "Action parameters contain unsafe instructions", corrected_action
        
        # Check 5: Dangerous actions require extra validation
        if action in self.dangerous_actions:
            return False, f"Dangerous action '{action}' is not allowed", corrected_action
        
        return True, None, corrected_action
    
    def _is_deletion_action(self, action: str, params: Dict[str, Any]) -> bool:
        """Check if action is a deletion action"""
        deletion_keywords = ["delete", "remove", "drop", "destroy", "kill"]
        return any(keyword in action.lower() for keyword in deletion_keywords)
    
    def _contains_unsafe_patterns(self, text: str) -> bool:
        """Check for unsafe patterns in text"""
        text_lower = text.lower()
        for pattern in self.unsafe_patterns:
            if re.search(pattern, text_lower):
                return True
        return False
    
    def sanitize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize LLM output
        
        Args:
            output: Raw LLM output
        
        Returns:
            Sanitized output
        """
        sanitized = output.copy()
        
        # Extract action
        action = sanitized.get("action", "")
        
        # Validate action
        action_params = sanitized.get("action_params", {})
        is_safe, error_msg, corrected = self.validate_action(action, action_params)
        
        if not is_safe:
            logger.warning(f"Unsafe action detected: {error_msg}")
            # Correct the action
            sanitized["action"] = corrected.get("action", "do_nothing")
            sanitized["action_params"] = corrected
            sanitized["safety_corrected"] = True
            sanitized["safety_warning"] = error_msg
        else:
            sanitized["safety_corrected"] = False
        
        # Clamp confidence
        confidence = sanitized.get("confidence", 0.5)
        sanitized["confidence"] = max(0.0, min(1.0, float(confidence)))
        
        # Sanitize reasoning text
        if "reasoning" in sanitized:
            sanitized["reasoning"] = self._sanitize_text(sanitized["reasoning"])
        
        if "explanation" in sanitized:
            sanitized["explanation"] = self._sanitize_text(sanitized["explanation"])
        
        return sanitized
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text output"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove unsafe commands
        for pattern in self.unsafe_patterns:
            text = re.sub(pattern, "[REMOVED]", text, flags=re.IGNORECASE)
        
        # Limit length
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    def apply_safety_checks(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply all safety checks and correct if needed
        
        Args:
            decision: Decision to check
            context: Context information
        
        Returns:
            Safe decision (possibly corrected)
        """
        # Sanitize output
        safe_decision = self.sanitize_output(decision)
        
        # Additional checks
        action = safe_decision.get("action", "")
        action_params = safe_decision.get("action_params", {})
        
        # Check scaling limits
        if "scale" in action:
            current_replicas = context.get("current_replicas", 1)
            target_replicas = action_params.get("target_replicas", current_replicas)
            
            if target_replicas > self.max_replicas:
                safe_decision["action_params"]["target_replicas"] = self.max_replicas
                safe_decision["safety_corrected"] = True
                safe_decision["safety_warning"] = f"Scaling limited to maximum {self.max_replicas} replicas"
                logger.warning(f"Scaling corrected: {target_replicas} -> {self.max_replicas}")
            
            if target_replicas < self.min_replicas:
                safe_decision["action_params"]["target_replicas"] = self.min_replicas
                safe_decision["safety_corrected"] = True
                safe_decision["safety_warning"] = f"Scaling limited to minimum {self.min_replicas} replicas"
                logger.warning(f"Scaling corrected: {target_replicas} -> {self.min_replicas}")
        
        # Check for protected resources
        resource_name = action_params.get("resource_name", "")
        if resource_name:
            if any(protected in resource_name.lower() for protected in self.protected_resources):
                if self._is_deletion_action(action, action_params):
                    safe_decision["action"] = "do_nothing"
                    safe_decision["safety_corrected"] = True
                    safe_decision["safety_warning"] = f"Cannot delete protected resource: {resource_name}"
                    logger.warning(f"Protected resource deletion blocked: {resource_name}")
        
        # Add safety metadata
        safe_decision["safety_checked"] = True
        safe_decision["is_safe"] = not safe_decision.get("safety_corrected", False)
        
        return safe_decision
    
    def get_safety_report(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate safety report
        
        Args:
            decision: Decision to report on
            context: Context
        
        Returns:
            Safety report
        """
        action = decision.get("action", "")
        action_params = decision.get("action_params", {})
        
        is_safe, error_msg, corrected = self.validate_action(action, action_params)
        
        report = {
            "is_safe": is_safe,
            "error_message": error_msg,
            "action": action,
            "corrected_action": corrected if not is_safe else None,
            "safety_checks": {
                "allowed_action": action in self.allowed_actions,
                "no_deletion_of_protected": not (self._is_deletion_action(action, action_params) and 
                                                 any(p in str(action_params).lower() for p in self.protected_resources)),
                "scaling_within_limits": self._check_scaling_limits(action, action_params),
                "no_unsafe_patterns": not self._contains_unsafe_patterns(str(decision))
            }
        }
        
        return report
    
    def _check_scaling_limits(self, action: str, params: Dict[str, Any]) -> bool:
        """Check if scaling is within limits"""
        if "scale" not in action:
            return True
        
        target_replicas = params.get("target_replicas", params.get("replicas", 0))
        return self.min_replicas <= target_replicas <= self.max_replicas
