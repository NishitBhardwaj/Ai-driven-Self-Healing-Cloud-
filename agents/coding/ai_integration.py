"""
AI Engine Integration for Coding Agent
Uses LLM reasoning + memory
"""

import sys
import os
from typing import Dict, List, Optional, Any
import logging

# Add AI engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine
from ai_engine.meta_agent.memory import MetaAgentMemory

logger = logging.getLogger(__name__)


class CodingAIIntegration:
    """
    AI Engine Integration for Coding Agent
    
    Uses:
    - LLM reasoning for code analysis and fixes
    - Memory for learning from past fixes
    """
    
    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize AI integration
        
        Args:
            openrouter_api_key: OpenRouter API key
            gemini_api_key: Gemini API key
        """
        # Initialize LLM Reasoning Engine
        self.reasoning_engine = ReasoningEngine(
            openrouter_api_key=openrouter_api_key,
            gemini_api_key=gemini_api_key,
            use_openrouter=True,
            use_gemini=True,
            use_cot=True
        )
        
        # Initialize Memory
        self.memory = MetaAgentMemory()
        
        logger.info("Coding AI Integration initialized")
    
    def analyze_and_fix_code(
        self,
        error_info: Dict[str, Any],
        code_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze code error and generate fix using LLM reasoning + memory
        
        Args:
            error_info: Error information (stacktrace, error message, etc.)
            code_context: Code context (file_path, file_content, etc.)
        
        Returns:
            Fix recommendation with explanation
        """
        # Step 1: Classify error using LLM
        error_classification = self.reasoning_engine.classify_error(
            error_info=error_info,
            system_state=code_context
        )
        
        # Step 2: Retrieve similar past fixes from memory
        similar_fixes = self.memory.retrieve_similar_decisions(
            query_decision={"action": "fix_code", "error_type": error_classification.get("error_type")},
            query_context=code_context,
            top_k=3
        )
        
        # Step 3: Generate healing plan using LLM
        healing_plan = self.reasoning_engine.generate_healing_plan(
            error_classification=error_classification,
            system_state=code_context,
            available_actions=["fix_code", "refactor", "add_error_handling", "update_dependencies"]
        )
        
        # Step 4: Compare solutions (including past fixes)
        solutions = []
        
        # Add LLM solution
        solutions.append({
            "id": "llm_solution",
            "action": healing_plan.get("action", "fix_code"),
            "description": healing_plan.get("reasoning", ""),
            "confidence": healing_plan.get("confidence", 0.5)
        })
        
        # Add past solutions from memory
        for past_fix in similar_fixes:
            if past_fix.get("success"):
                solutions.append({
                    "id": f"past_fix_{past_fix.get('decision_id', 'unknown')}",
                    "action": past_fix.get("decision", {}).get("action", "fix_code"),
                    "description": f"Previously successful fix (similarity: {past_fix.get('similarity', 0):.2f})",
                    "confidence": past_fix.get("similarity", 0.5),
                    "past_fix": True
                })
        
        # Compare solutions
        comparison = self.reasoning_engine.compare_solutions(
            solutions=solutions,
            context={**error_info, **code_context}
        )
        
        # Step 5: Select best solution
        best_solution_id = comparison.get("best_solution", "llm_solution")
        best_solution = next((s for s in solutions if s["id"] == best_solution_id), solutions[0])
        
        # Step 6: Generate detailed fix using LLM
        fix_result = {
            "action": best_solution.get("action", "fix_code"),
            "confidence": best_solution.get("confidence", 0.5),
            "error_classification": error_classification,
            "healing_plan": healing_plan,
            "solution_comparison": comparison,
            "similar_past_fixes": similar_fixes,
            "recommended_solution": best_solution,
            "explanation": comparison.get("recommendation", "")
        }
        
        # Store in memory for future learning
        decision_id = self.memory.store_decision(
            decision=fix_result,
            context={**error_info, **code_context}
        )
        fix_result["decision_id"] = decision_id
        
        logger.info(f"Code fix recommendation: {best_solution.get('action')} (confidence: {best_solution.get('confidence', 0):.2f})")
        
        return fix_result
    
    def update_fix_outcome(
        self,
        decision_id: str,
        success: bool,
        outcome: Dict[str, Any]
    ):
        """
        Update fix outcome in memory
        
        Args:
            decision_id: Decision ID
            success: Whether fix was successful
            outcome: Outcome information
        """
        self.memory.update_decision_outcome(decision_id, outcome, success)
        logger.info(f"Fix outcome updated: decision_id={decision_id}, success={success}")

