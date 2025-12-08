"""
Reasoning Engine
Integrates OpenRouter and Gemini APIs
Classify error, generate healing plan, evaluate risk, compare solutions
"""

from typing import Dict, List, Optional, Any
import logging
import json

from .planner import LLMPlanner
from .chain_of_thought import ChainOfThoughtReasoner

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4"):
        self.api_key = api_key
        self.model = model
        logger.info(f"OpenRouter client initialized: model={model}")
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate response using OpenRouter"""
        if not self.api_key:
            logger.warning("OpenRouter API key not set, returning placeholder")
            return '{"action": "no_action", "reasoning": "API key not configured"}'
        
        try:
            import requests
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return '{"action": "no_action", "reasoning": "API error"}'
    
    def generate_stream(self, prompt: str, max_tokens: int = 2000):
        """Generate streaming response (not implemented)"""
        return self.generate(prompt, max_tokens)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        logger.info(f"Gemini client initialized: model={model}")
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate response using Gemini"""
        if not self.api_key:
            logger.warning("Gemini API key not set, returning placeholder")
            return '{"action": "no_action", "reasoning": "API key not configured"}'
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except ImportError:
            logger.warning("google-generativeai not installed, using requests fallback")
            try:
                import requests
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}]}
                )
                response.raise_for_status()
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                return '{"action": "no_action", "reasoning": "API error"}'
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return '{"action": "no_action", "reasoning": "API error"}'


class ReasoningEngine:
    """
    Main reasoning engine integrating OpenRouter and Gemini
    
    Capabilities:
    - Classify error
    - Generate healing plan
    - Evaluate risk
    - Compare solutions
    """
    
    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        use_openrouter: bool = True,
        use_gemini: bool = True,
        use_cot: bool = True
    ):
        """
        Initialize reasoning engine
        
        Args:
            openrouter_api_key: OpenRouter API key
            gemini_api_key: Gemini API key
            use_openrouter: Whether to use OpenRouter
            use_gemini: Whether to use Gemini
            use_cot: Whether to use chain-of-thought reasoning
        """
        # Initialize clients
        self.openrouter_client = OpenRouterClient(openrouter_api_key) if use_openrouter else None
        self.gemini_client = GeminiClient(gemini_api_key) if use_gemini else None
        
        # Use primary client (OpenRouter preferred)
        primary_client = self.openrouter_client or self.gemini_client
        
        self.planner = LLMPlanner(llm_client=primary_client)
        self.cot_reasoner = ChainOfThoughtReasoner(llm_client=primary_client) if use_cot else None
        self.use_cot = use_cot
        
        logger.info(f"ReasoningEngine initialized: openrouter={use_openrouter}, gemini={use_gemini}, cot={use_cot}")
    
    def classify_error(
        self,
        error_info: Dict[str, Any],
        system_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify error type and severity
        
        Args:
            error_info: Error information
            system_state: Current system state
        
        Returns:
            Error classification
        """
        prompt = f"""Classify this error in cloud infrastructure:

Error Information:
{json.dumps(error_info, indent=2)}

System State:
{json.dumps(system_state, indent=2) if system_state else "Not available"}

Classify the error:
1. Error type (pod_crash, deployment_error, resource_exhaustion, network_issue, etc.)
2. Severity (low, medium, high, critical)
3. Root cause category
4. Affected components

Respond in JSON:
{{
    "error_type": "type",
    "severity": "low|medium|high|critical",
    "root_cause_category": "category",
    "affected_components": ["component1", "component2"],
    "classification_confidence": 0.0-1.0
}}
"""
        
        # Try OpenRouter first, then Gemini
        response = None
        if self.openrouter_client:
            response = self.openrouter_client.generate(prompt)
        elif self.gemini_client:
            response = self.gemini_client.generate(prompt)
        
        if response:
            try:
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                classification = json.loads(response)
                logger.info(f"Error classified: {classification.get('error_type', 'unknown')}")
                return classification
            except json.JSONDecodeError:
                logger.warning("Failed to parse classification response")
        
        # Fallback
        return {
            "error_type": error_info.get("type", "unknown"),
            "severity": error_info.get("severity", "medium"),
            "root_cause_category": "unknown",
            "affected_components": [],
            "classification_confidence": 0.5
        }
    
    def generate_healing_plan(
        self,
        error_classification: Dict[str, Any],
        system_state: Dict[str, Any],
        available_actions: List[str],
        rl_suggestion: Optional[Dict[str, Any]] = None,
        gnn_suggestion: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate healing plan
        
        Args:
            error_classification: Classified error
            system_state: Current system state
            available_actions: Available actions
            rl_suggestion: RL agent suggestion
            gnn_suggestion: GNN suggestion
        
        Returns:
            Healing plan
        """
        return self.planner.plan_multi_step_healing(
            failure_info=error_classification,
            system_state=system_state,
            rl_suggestion=rl_suggestion,
            gnn_suggestion=gnn_suggestion,
            dependency_graph=None
        )
    
    def evaluate_risk(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate risk of an action
        
        Args:
            action: Action to evaluate
            context: Context information
        
        Returns:
            Risk evaluation
        """
        prompt = f"""Evaluate the risk of this action in cloud infrastructure:

Action: {action}
Context: {json.dumps(context, indent=2)}

Evaluate:
1. Risk level (low, medium, high, critical)
2. Potential negative impacts
3. Safety concerns
4. Recommended safeguards

Respond in JSON:
{{
    "risk_level": "low|medium|high|critical",
    "risk_score": 0.0-1.0,
    "potential_impacts": ["impact1", "impact2"],
    "safety_concerns": ["concern1", "concern2"],
    "recommended_safeguards": ["safeguard1", "safeguard2"],
    "is_safe": true|false
}}
"""
        
        # Try OpenRouter first, then Gemini
        response = None
        if self.openrouter_client:
            response = self.openrouter_client.generate(prompt)
        elif self.gemini_client:
            response = self.gemini_client.generate(prompt)
        
        if response:
            try:
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                risk_eval = json.loads(response)
                logger.info(f"Risk evaluated: {risk_eval.get('risk_level', 'unknown')}")
                return risk_eval
            except json.JSONDecodeError:
                logger.warning("Failed to parse risk evaluation response")
        
        # Fallback
        return {
            "risk_level": "medium",
            "risk_score": 0.5,
            "potential_impacts": [],
            "safety_concerns": [],
            "recommended_safeguards": [],
            "is_safe": True
        }
    
    def compare_solutions(
        self,
        solutions: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multiple solutions
        
        Args:
            solutions: List of solutions to compare
            context: Context information
        
        Returns:
            Comparison result
        """
        prompt = f"""Compare these solutions for cloud infrastructure:

Solutions:
{json.dumps(solutions, indent=2)}

Context:
{json.dumps(context, indent=2)}

Compare:
1. Effectiveness
2. Risk levels
3. Cost-benefit
4. Time to implement
5. Best solution recommendation

Respond in JSON:
{{
    "comparison": [
        {{
            "solution_id": "solution1",
            "effectiveness": 0.0-1.0,
            "risk_level": "low|medium|high",
            "cost_benefit": "description",
            "time_to_implement": "fast|medium|slow",
            "overall_score": 0.0-1.0
        }}
    ],
    "best_solution": "solution_id",
    "recommendation": "detailed recommendation"
}}
"""
        
        # Try OpenRouter first, then Gemini
        response = None
        if self.openrouter_client:
            response = self.openrouter_client.generate(prompt)
        elif self.gemini_client:
            response = self.gemini_client.generate(prompt)
        
        if response:
            try:
                if "```json" in response:
                    json_start = response.find("```json") + 7
                    json_end = response.find("```", json_start)
                    response = response[json_start:json_end].strip()
                comparison = json.loads(response)
                logger.info(f"Solutions compared: best={comparison.get('best_solution', 'unknown')}")
                return comparison
            except json.JSONDecodeError:
                logger.warning("Failed to parse comparison response")
        
        # Fallback
        return {
            "comparison": [],
            "best_solution": solutions[0].get("id", "unknown") if solutions else "unknown",
            "recommendation": "Rule-based comparison"
        }
    
    def reason_about_failure(
        self,
        failure_info: Dict[str, Any],
        system_state: Dict[str, Any],
        available_actions: List[str],
        rl_suggestion: Optional[Dict[str, Any]] = None,
        gnn_suggestion: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete reasoning about failure
        
        Args:
            failure_info: Failure information
            system_state: Current system state
            available_actions: Available actions
            rl_suggestion: RL agent suggestion
            gnn_suggestion: GNN suggestion
        
        Returns:
            Complete reasoning result
        """
        # Step 1: Classify error
        error_classification = self.classify_error(failure_info, system_state)
        
        # Step 2: Generate healing plan
        healing_plan = self.generate_healing_plan(
            error_classification,
            system_state,
            available_actions,
            rl_suggestion,
            gnn_suggestion
        )
        
        # Step 3: Evaluate risk
        risk_evaluation = self.evaluate_risk(
            healing_plan.get("action", "no_action"),
            system_state
        )
        
        # Step 4: Use chain-of-thought if enabled
        if self.use_cot and self.cot_reasoner:
            cot_result = self.cot_reasoner.reason_internal(
                problem=error_classification,
                context={**system_state, "available_actions": available_actions}
            )
            healing_plan["cot_explanation"] = cot_result.get("explanation", "")
            healing_plan["cot_justification"] = cot_result.get("justification", "")
        
        # Combine results
        result = {
            **healing_plan,
            "error_classification": error_classification,
            "risk_evaluation": risk_evaluation,
            "is_safe": risk_evaluation.get("is_safe", True)
        }
        
        return result
