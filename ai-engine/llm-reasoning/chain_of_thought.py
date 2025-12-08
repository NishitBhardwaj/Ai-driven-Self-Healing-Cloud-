"""
Chain of Thought Reasoning
Perform internal CoT reasoning (strictly non-exposed)
Summarized explanation returned
"""

from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class ChainOfThoughtReasoner:
    """
    Implements internal chain-of-thought reasoning
    
    Features:
    - Strictly non-exposed (internal only)
    - Detailed step-by-step reasoning
    - Summarized explanation returned to user
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.internal_reasoning = []  # Store internal reasoning (not exposed)
        logger.info("Chain of Thought Reasoner initialized (internal mode)")
    
    def reason_internal(
        self,
        problem: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform internal chain-of-thought reasoning
        
        Internal reasoning is NOT exposed to users.
        Only summarized explanation is returned.
        
        Args:
            problem: Problem description
            context: Additional context
        
        Returns:
            Reasoning result with summarized explanation
        """
        # Clear internal reasoning
        self.internal_reasoning = []
        
        # Step 1: Problem identification (internal)
        step1 = self._identify_problem_internal(problem, context)
        self.internal_reasoning.append(step1)
        
        # Step 2: Deep analysis (internal)
        step2 = self._deep_analysis_internal(problem, context, step1)
        self.internal_reasoning.append(step2)
        
        # Step 3: Generate solutions (internal)
        step3 = self._generate_solutions_internal(problem, context, step2)
        self.internal_reasoning.append(step3)
        
        # Step 4: Evaluate solutions (internal)
        step4 = self._evaluate_solutions_internal(problem, context, step3)
        self.internal_reasoning.append(step4)
        
        # Step 5: Make decision (internal)
        step5 = self._make_decision_internal(problem, context, step4)
        self.internal_reasoning.append(step5)
        
        # Generate summarized explanation (user-facing)
        summarized_explanation = self._summarize_reasoning(step5)
        
        result = {
            "decision": step5.get("decision", "no_action"),
            "confidence": step5.get("confidence", 0.5),
            "explanation": summarized_explanation,  # User-facing summary
            "justification": step5.get("justification", ""),  # Brief justification
            # Internal reasoning is NOT included in result
        }
        
        logger.info(f"Internal CoT reasoning completed: {len(self.internal_reasoning)} steps")
        logger.debug(f"Internal reasoning stored (not exposed): {len(self.internal_reasoning)} steps")
        
        return result
    
    def _identify_problem_internal(
        self,
        problem: Dict,
        context: Dict
    ) -> Dict:
        """Step 1: Internal problem identification"""
        prompt = f"""INTERNAL REASONING - DO NOT EXPOSE TO USER

Identify the core problem:

Problem: {json.dumps(problem, indent=2)}
Context: {json.dumps(context, indent=2)}

Provide detailed internal analysis in JSON:
{{
    "main_problem": "detailed problem description",
    "symptoms": ["symptom1", "symptom2"],
    "root_cause_analysis": "detailed root cause analysis",
    "severity": "low|medium|high|critical",
    "internal_notes": "internal reasoning notes"
}}
"""
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            result = self._parse_json_response(response)
        else:
            result = {
                "main_problem": problem.get("type", "unknown"),
                "symptoms": problem.get("symptoms", []),
                "root_cause_analysis": "Internal analysis",
                "severity": problem.get("severity", "medium"),
                "internal_notes": "Rule-based analysis"
            }
        
        result["step"] = "problem_identification"
        return result
    
    def _deep_analysis_internal(
        self,
        problem: Dict,
        context: Dict,
        previous_step: Dict
    ) -> Dict:
        """Step 2: Internal deep analysis"""
        prompt = f"""INTERNAL REASONING - DO NOT EXPOSE TO USER

Perform deep analysis:

Problem: {previous_step.get('main_problem', 'unknown')}
Severity: {previous_step.get('severity', 'medium')}
Context: {json.dumps(context, indent=2)}

Provide detailed internal analysis in JSON:
{{
    "system_state_analysis": "detailed system state analysis",
    "resource_availability": "resource analysis",
    "constraints": ["constraint1", "constraint2"],
    "dependencies": "dependency analysis",
    "impact_analysis": "detailed impact analysis",
    "internal_notes": "internal reasoning"
}}
"""
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            result = self._parse_json_response(response)
        else:
            result = {
                "system_state_analysis": "System operational with issues",
                "resource_availability": "Resources available",
                "constraints": [],
                "dependencies": context.get("dependencies", []),
                "impact_analysis": "Moderate impact",
                "internal_notes": "Rule-based analysis"
            }
        
        result["step"] = "deep_analysis"
        return result
    
    def _generate_solutions_internal(
        self,
        problem: Dict,
        context: Dict,
        previous_step: Dict
    ) -> Dict:
        """Step 3: Internal solution generation"""
        available_actions = context.get("available_actions", [])
        
        prompt = f"""INTERNAL REASONING - DO NOT EXPOSE TO USER

Generate solutions:

Problem: {problem.get('type', 'unknown')}
Available Actions: {', '.join(available_actions)}
Constraints: {', '.join(previous_step.get('constraints', []))}

Provide detailed internal solution analysis in JSON:
{{
    "solutions": [
        {{
            "solution_id": "solution1",
            "action": "action_name",
            "detailed_analysis": "detailed analysis of this solution",
            "pros": ["pro1", "pro2"],
            "cons": ["con1", "con2"],
            "feasibility": "high|medium|low",
            "internal_notes": "internal reasoning"
        }}
    ],
    "internal_comparison": "internal comparison of solutions"
}}
"""
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            result = self._parse_json_response(response)
        else:
            solutions = []
            for i, action in enumerate(available_actions[:5]):
                solutions.append({
                    "solution_id": f"solution{i+1}",
                    "action": action,
                    "detailed_analysis": f"Internal analysis of {action}",
                    "pros": ["Addresses problem"],
                    "cons": ["May have side effects"],
                    "feasibility": "high",
                    "internal_notes": "Rule-based"
                })
            result = {"solutions": solutions, "internal_comparison": "Rule-based comparison"}
        
        result["step"] = "solution_generation"
        return result
    
    def _evaluate_solutions_internal(
        self,
        problem: Dict,
        context: Dict,
        previous_step: Dict
    ) -> Dict:
        """Step 4: Internal solution evaluation"""
        solutions = previous_step.get("solutions", [])
        
        prompt = f"""INTERNAL REASONING - DO NOT EXPOSE TO USER

Evaluate solutions:

Problem: {problem.get('type', 'unknown')}
Solutions: {json.dumps(solutions, indent=2)}

Provide detailed internal evaluation in JSON:
{{
    "evaluations": [
        {{
            "solution_id": "solution1",
            "effectiveness": 0.0-1.0,
            "risk_level": "low|medium|high",
            "cost_benefit": "detailed cost-benefit analysis",
            "time_to_implement": "fast|medium|slow",
            "overall_score": 0.0-1.0,
            "internal_notes": "internal evaluation notes"
        }}
    ],
    "internal_ranking": "internal ranking of solutions"
}}
"""
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            result = self._parse_json_response(response)
        else:
            evaluations = []
            for sol in solutions:
                evaluations.append({
                    "solution_id": sol["solution_id"],
                    "effectiveness": 0.7,
                    "risk_level": "medium",
                    "cost_benefit": "Moderate cost, good benefit",
                    "time_to_implement": "fast",
                    "overall_score": 0.7,
                    "internal_notes": "Rule-based evaluation"
                })
            result = {"evaluations": evaluations, "internal_ranking": "Rule-based ranking"}
        
        result["step"] = "solution_evaluation"
        return result
    
    def _make_decision_internal(
        self,
        problem: Dict,
        context: Dict,
        previous_step: Dict
    ) -> Dict:
        """Step 5: Internal decision making"""
        evaluations = previous_step.get("evaluations", [])
        
        if not evaluations:
            return {
                "step": "decision",
                "decision": "no_action",
                "justification": "No viable solutions",
                "confidence": 0.0,
                "internal_notes": "No solutions available"
            }
        
        # Select best solution
        best_solution = max(evaluations, key=lambda x: x.get("overall_score", 0))
        
        prompt = f"""INTERNAL REASONING - DO NOT EXPOSE TO USER

Make final decision:

Problem: {problem.get('type', 'unknown')}
Best Solution: {json.dumps(best_solution, indent=2)}
All Evaluations: {json.dumps(evaluations, indent=2)}

Provide detailed internal decision in JSON:
{{
    "decision": "action_name",
    "justification": "brief justification (will be summarized)",
    "confidence": 0.0-1.0,
    "expected_outcome": "expected outcome",
    "contingency_plan": "contingency plan",
    "internal_reasoning": "detailed internal reasoning (not exposed)",
    "internal_notes": "internal notes"
}}
"""
        
        if self.llm_client:
            response = self.llm_client.generate(prompt)
            result = self._parse_json_response(response)
        else:
            result = {
                "decision": best_solution.get("solution_id", "unknown"),
                "justification": f"Selected based on highest score ({best_solution.get('overall_score', 0):.2f})",
                "confidence": best_solution.get("overall_score", 0.7),
                "expected_outcome": "Problem will be resolved",
                "contingency_plan": "Try alternative if this fails",
                "internal_reasoning": "Internal rule-based reasoning",
                "internal_notes": "Rule-based decision"
            }
        
        result["step"] = "decision"
        return result
    
    def _summarize_reasoning(self, decision: Dict) -> str:
        """
        Generate summarized explanation for user
        
        Internal reasoning is NOT included.
        Only high-level summary is returned.
        """
        action = decision.get("decision", "unknown")
        justification = decision.get("justification", "")
        confidence = decision.get("confidence", 0.5)
        
        summary = f"Selected action: {action}. {justification} (Confidence: {confidence:.0%})"
        
        return summary
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {}
    
    def get_internal_reasoning_count(self) -> int:
        """Get count of internal reasoning steps (for debugging, not exposed)"""
        return len(self.internal_reasoning)
