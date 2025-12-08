"""
Coding/Code-Fixer Agent
Uses LLM to generate/fix code, auto-detect error patterns, and suggest solutions
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from llm import get_llm_client, fix_code, generate_code, return_patch
from ai_integration import CodingAIIntegration


class CodingAgent:
    """Agent for code generation and debugging"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.agent_id = "coding-agent"
        self.name = "Coding/Code-Fixer Agent"
        self.description = "Uses LLM reasoning + memory to generate/fix code, auto-detect error patterns, and suggest solutions"
        self.status = "stopped"
        self.logger = self._setup_logger()
        self.llm_client = get_llm_client()
        
        # Initialize AI Engine Integration
        self.ai_integration = CodingAIIntegration(
            openrouter_api_key=openrouter_api_key,
            gemini_api_key=gemini_api_key
        )
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent"""
        logger = logging.getLogger(self.agent_id)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def start(self) -> bool:
        """Start the agent"""
        self.logger.info(f"Starting {self.name}")
        self.status = "running"
        return True
    
    def stop(self) -> bool:
        """Stop the agent"""
        self.logger.info(f"Stopping {self.name}")
        self.status = "stopped"
        return True
    
    def handle_message(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages"""
        self.logger.debug(f"Received message: {event}")
        return {"status": "received"}
    
    def llm_call(self, prompt: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """Make LLM call"""
        try:
            return self.llm_client.call_llm(prompt, provider=provider)
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def debug_code(
        self,
        stacktrace: str,
        file_path: Optional[str] = None,
        error_logs: Optional[str] = None,
        file_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Debug code using LLM reasoning + memory
        
        Args:
            stacktrace: Stack trace or error message
            file_path: Path to the file with error
            error_logs: Additional error logs
            file_content: Current file content
        
        Returns:
            Dict with fix suggestions, patch, and explanation
        """
        self.logger.info("Debugging code issue using AI Engine")
        
        # Use AI Engine Integration
        try:
            error_info = {
                "type": "code_error",
                "stacktrace": stacktrace,
                "error_logs": error_logs,
                "file_path": file_path
            }
            
            code_context = {
                "file_path": file_path,
                "file_content": file_content,
                "language": self._detect_language(file_path) if file_path else "python"
            }
            
            # Get AI-powered fix recommendation
            ai_result = self.ai_integration.analyze_and_fix_code(
                error_info=error_info,
                code_context=code_context
            )
            
            # Generate actual fix using LLM
            if file_content:
                result = fix_code(error_logs or stacktrace, file_content, stacktrace)
                
                if result.get("fixed_code"):
                    patch = return_patch(file_content, result["fixed_code"])
                    result["patch"] = patch
            else:
                result = {"fixed_code": None, "patch": None}
            
            return {
                "status": "success",
                "ai_recommendation": ai_result,
                "fixed_code": result.get("fixed_code"),
                "patch": result.get("patch"),
                "explanation": ai_result.get("explanation", ""),
                "similar_past_fixes": ai_result.get("similar_past_fixes", [])
            }
        except Exception as e:
            self.logger.error(f"AI-powered debug failed: {e}, falling back to basic LLM")
            # Fallback to basic LLM
            return self._basic_debug_code(stacktrace, file_path, error_logs)
    
    def _basic_debug_code(
        self,
        stacktrace: str,
        file_path: Optional[str],
        error_logs: Optional[str]
    ) -> Dict[str, Any]:
        """Basic debug code fallback"""
        prompt = f"""Analyze this error and provide a fix:

Stacktrace:
{stacktrace}
"""
        if file_path:
            prompt += f"\nFile: {file_path}"
        if error_logs:
            prompt += f"\nError Logs:\n{error_logs}"
        prompt += "\n\nProvide:\n1. Root cause analysis\n2. Suggested fix\n3. Explanation"
        
        try:
            llm_response = self.llm_call(prompt)
            return {
                "status": "success",
                "analysis": llm_response["response"],
                "provider": llm_response["provider"]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path"""
        ext = os.path.splitext(file_path)[1].lower()
        lang_map = {
            ".py": "python",
            ".go": "go",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c"
        }
        return lang_map.get(ext, "python")
    
    def generate_code(
        self,
        description: str,
        language: str = "python",
        context: Optional[str] = None,
        requirements: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code using LLM (enhanced with generate_code function)
        
        Args:
            description: Description of what code to generate
            language: Programming language
            context: Additional context or requirements
            requirements: Specific requirements
        
        Returns:
            Dict with generated code and explanation
        """
        self.logger.info(f"Generating {language} code")
        
        specs = {
            "description": description,
            "language": language,
            "context": context or "",
            "requirements": requirements or ""
        }
        
        try:
            result = generate_code(specs)
            return {
                "status": "success",
                **result,
                "explanation": "Code generated using LLM with best practices and error handling"
            }
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def fix_code_endpoint(
        self,
        error_log: str,
        file_content: str,
        file_path: Optional[str] = None,
        stacktrace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fix code endpoint - uses AI Engine (LLM reasoning + memory)
        
        Args:
            error_log: Error message
            file_content: Current file content
            file_path: File path
            stacktrace: Stack trace
        
        Returns:
            Dict with fixed_code, patch, explanation
        """
        self.logger.info(f"Fixing code for {file_path or 'unknown file'} using AI Engine")
        
        try:
            # Use AI Engine Integration
            error_info = {
                "type": "code_error",
                "error_log": error_log,
                "stacktrace": stacktrace
            }
            
            code_context = {
                "file_path": file_path,
                "file_content": file_content
            }
            
            ai_result = self.ai_integration.analyze_and_fix_code(
                error_info=error_info,
                code_context=code_context
            )
            
            # Generate actual fix
            result = fix_code(error_log, file_content, stacktrace)
            patch = return_patch(file_content, result["fixed_code"])
            
            return {
                "status": "success",
                "fixed_code": result["fixed_code"],
                "patch": patch,
                "file_path": file_path,
                "explanation": ai_result.get("explanation", result.get("explanation", "")),
                "ai_recommendation": ai_result,
                "decision_id": ai_result.get("decision_id")
            }
        except Exception as e:
            self.logger.error(f"AI-powered fix failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "explanation": f"Failed to fix code: {str(e)}"
            }
    
    def update_fix_outcome(
        self,
        decision_id: str,
        success: bool,
        outcome: Dict[str, Any]
    ):
        """Update fix outcome in memory"""
        self.ai_integration.update_fix_outcome(decision_id, success, outcome)
    
    def explain_action(self, input_data: Any, output_data: Any = None) -> Dict[str, Any]:
        """Provide explanation for actions (Explainability Layer)"""
        from explain import explain_action
        return explain_action(self.name, input_data, output_data)


def main():
    """Main entry point for testing"""
    agent = CodingAgent()
    agent.start()
    
    # Test debug
    result = agent.debug_code(
        stacktrace="IndexError: list index out of range",
        file_path="app.py",
        error_logs="Error occurred at line 42"
    )
    print(json.dumps(result, indent=2))
    
    agent.stop()


if __name__ == "__main__":
    main()

