"""
LLM Planner
Plan multi-step healing with deep reasoning and explanation
"""

import json
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class LLMPlanner:
    """
    Planner that uses LLM for multi-step healing planning
    
    Multi-step process:
    1) Analyze failure
    2) Check dependency graph
    3) Use RL suggestion
    4) Compare with GNN
    5) Choose best action
    6) Explain why
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize LLM planner
        
        Args:
            llm_client: LLM client (OpenRouter, Gemini, etc.)
        """
        self.llm_client = llm_client
        logger.info("LLM Planner initialized")
    
    def plan_multi_step_healing(
        self,
        failure_info: Dict[str, Any],
        dependency_graph: Optional[Dict[str, Any]] = None,
        rl_suggestion: Optional[Dict[str, Any]] = None,
        gnn_suggestion: Optional[Dict[str, Any]] = None,
        system_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Plan multi-step healing strategy
        
        Args:
            failure_info: Information about the failure
            dependency_graph: Dependency graph information
            rl_suggestion: RL agent suggestion
            gnn_suggestion: GNN suggestion
            system_state: Current system state
        
        Returns:
            Multi-step healing plan with explanation
        """
        prompt = self._build_multi_step_prompt(
            failure_info, dependency_graph, rl_suggestion, gnn_suggestion, system_state
        )
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            plan = self._parse_llm_response(response)
        else:
            # Fallback to rule-based planning
            plan = self._rule_based_multi_step_planning(
                failure_info, dependency_graph, rl_suggestion, gnn_suggestion, system_state
            )
        
        logger.info(f"Multi-step healing plan created: {plan.get('action', 'unknown')}")
        
        return plan
    
    def _build_multi_step_prompt(
        self,
        failure_info: Dict,
        dependency_graph: Optional[Dict],
        rl_suggestion: Optional[Dict],
        gnn_suggestion: Optional[Dict],
        system_state: Optional[Dict]
    ) -> str:
        """Build prompt for multi-step healing planning"""
        prompt = f"""You are an AI system managing cloud infrastructure. A failure has been detected. Plan a multi-step healing strategy.

STEP 1: ANALYZE FAILURE
Failure Information:
{json.dumps(failure_info, indent=2)}

STEP 2: CHECK DEPENDENCY GRAPH
Dependency Graph Information:
{json.dumps(dependency_graph, indent=2) if dependency_graph else "No dependency graph available"}

STEP 3: USE RL SUGGESTION
RL Agent Suggestion:
{json.dumps(rl_suggestion, indent=2) if rl_suggestion else "No RL suggestion available"}

STEP 4: COMPARE WITH GNN
GNN Suggestion:
{json.dumps(gnn_suggestion, indent=2) if gnn_suggestion else "No GNN suggestion available"}

STEP 5: CHOOSE BEST ACTION
Current System State:
{json.dumps(system_state, indent=2) if system_state else "No system state available"}

STEP 6: EXPLAIN WHY

Based on the above information, perform the following steps:

1. Analyze the failure: Identify the type, severity, and root cause
2. Check dependency graph: Determine which services/components are affected
3. Use RL suggestion: Consider the RL agent's recommendation
4. Compare with GNN: Evaluate the GNN's failure propagation prediction
5. Choose best action: Select the optimal healing action considering all inputs
6. Explain why: Provide detailed justification for the chosen action

Provide your response in JSON format:
{{
    "step1_analysis": {{
        "failure_type": "type of failure",
        "severity": "low|medium|high|critical",
        "root_cause": "identified root cause",
        "affected_components": ["component1", "component2"]
    }},
    "step2_dependency_check": {{
        "impacted_services": ["service1", "service2"],
        "critical_paths": ["path1", "path2"],
        "dependency_health": "description"
    }},
    "step3_rl_evaluation": {{
        "rl_action": "action from RL",
        "rl_confidence": 0.0-1.0,
        "rl_reasoning": "evaluation of RL suggestion"
    }},
    "step4_gnn_comparison": {{
        "gnn_action": "action from GNN",
        "gnn_confidence": 0.0-1.0,
        "failure_propagation_risk": 0.0-1.0,
        "gnn_reasoning": "evaluation of GNN suggestion"
    }},
    "step5_best_action": {{
        "chosen_action": "final recommended action",
        "confidence": 0.0-1.0,
        "alternative_actions": ["action1", "action2"],
        "expected_outcome": "what will happen"
    }},
    "step6_explanation": {{
        "justification": "detailed explanation of why this action was chosen",
        "risk_assessment": "evaluation of risks",
        "expected_benefits": "expected benefits",
        "contingency_plan": "what to do if this fails"
    }}
}}
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            plan = json.loads(response)
            
            # Extract final action and explanation
            step5 = plan.get("step5_best_action", {})
            step6 = plan.get("step6_explanation", {})
            
            return {
                "action": step5.get("chosen_action", "no_action"),
                "confidence": step5.get("confidence", 0.5),
                "reasoning": step6.get("justification", ""),
                "explanation": step6.get("justification", ""),
                "risk_assessment": step6.get("risk_assessment", ""),
                "expected_benefits": step6.get("expected_benefits", ""),
                "contingency_plan": step6.get("contingency_plan", ""),
                "multi_step_plan": plan,
                "step1_analysis": plan.get("step1_analysis", {}),
                "step2_dependency_check": plan.get("step2_dependency_check", {}),
                "step3_rl_evaluation": plan.get("step3_rl_evaluation", {}),
                "step4_gnn_comparison": plan.get("step4_gnn_comparison", {}),
                "step5_best_action": step5,
                "step6_explanation": step6
            }
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, using fallback")
            return self._extract_plan_from_text(response)
    
    def _extract_plan_from_text(self, text: str) -> Dict:
        """Extract plan information from text response"""
        plan = {
            "action": "restart_pod",
            "confidence": 0.7,
            "reasoning": text[:500],
            "explanation": text[:500],
            "multi_step_plan": {}
        }
        return plan
    
    def _rule_based_multi_step_planning(
        self,
        failure_info: Dict,
        dependency_graph: Optional[Dict],
        rl_suggestion: Optional[Dict],
        gnn_suggestion: Optional[Dict],
        system_state: Optional[Dict]
    ) -> Dict:
        """Rule-based multi-step planning fallback"""
        failure_type = failure_info.get('type', 'unknown')
        
        # Step 1: Analyze failure
        step1 = {
            "failure_type": failure_type,
            "severity": failure_info.get('severity', 'medium'),
            "root_cause": "unknown",
            "affected_components": [failure_info.get('service_id', 'unknown')]
        }
        
        # Step 2: Check dependency graph
        step2 = {
            "impacted_services": dependency_graph.get('impacted_services', []) if dependency_graph else [],
            "critical_paths": [],
            "dependency_health": "unknown"
        }
        
        # Step 3: RL evaluation
        step3 = {
            "rl_action": rl_suggestion.get('action', 'no_action') if rl_suggestion else 'no_action',
            "rl_confidence": rl_suggestion.get('confidence', 0.5) if rl_suggestion else 0.5,
            "rl_reasoning": "RL agent recommendation"
        }
        
        # Step 4: GNN comparison
        step4 = {
            "gnn_action": gnn_suggestion.get('action', 'no_action') if gnn_suggestion else 'no_action',
            "gnn_confidence": gnn_suggestion.get('confidence', 0.5) if gnn_suggestion else 0.5,
            "failure_propagation_risk": 0.5,
            "gnn_reasoning": "GNN recommendation"
        }
        
        # Step 5: Choose best action
        if rl_suggestion and gnn_suggestion:
            # Use higher confidence
            if rl_suggestion.get('confidence', 0) > gnn_suggestion.get('confidence', 0):
                action = rl_suggestion.get('action', 'no_action')
                confidence = rl_suggestion.get('confidence', 0.5)
            else:
                action = gnn_suggestion.get('action', 'no_action')
                confidence = gnn_suggestion.get('confidence', 0.5)
        elif rl_suggestion:
            action = rl_suggestion.get('action', 'no_action')
            confidence = rl_suggestion.get('confidence', 0.5)
        elif gnn_suggestion:
            action = gnn_suggestion.get('action', 'no_action')
            confidence = gnn_suggestion.get('confidence', 0.5)
        else:
            # Fallback based on failure type
            if failure_type == 'pod_crash':
                action = 'restart_pod'
            elif failure_type == 'deployment_error':
                action = 'rebuild_deployment'
            else:
                action = 'trigger_heal'
            confidence = 0.6
        
        step5 = {
            "chosen_action": action,
            "confidence": confidence,
            "alternative_actions": [],
            "expected_outcome": f"System will recover from {failure_type}"
        }
        
        # Step 6: Explain why
        step6 = {
            "justification": f"Selected {action} based on failure type {failure_type} and available suggestions",
            "risk_assessment": "Moderate risk",
            "expected_benefits": "System recovery",
            "contingency_plan": "Try alternative action if this fails"
        }
        
        return {
            "action": action,
            "confidence": confidence,
            "reasoning": step6["justification"],
            "explanation": step6["justification"],
            "multi_step_plan": {
                "step1_analysis": step1,
                "step2_dependency_check": step2,
                "step3_rl_evaluation": step3,
                "step4_gnn_comparison": step4,
                "step5_best_action": step5,
                "step6_explanation": step6
            },
            "step1_analysis": step1,
            "step2_dependency_check": step2,
            "step3_rl_evaluation": step3,
            "step4_gnn_comparison": step4,
            "step5_best_action": step5,
            "step6_explanation": step6
        }
