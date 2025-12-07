"""
LLM module for Python agents
Provides generic LLM call functions supporting OpenRouter and Gemini
"""

import os
import json
import requests
import time
from typing import Dict, Any, Optional


class LLMClient:
    """Generic LLM client supporting OpenRouter and Gemini"""
    
    def __init__(self):
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.default_provider = os.getenv("LLM_PROVIDER", "openrouter")
    
    def call_llm(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Call LLM API (OpenRouter or Gemini)
        
        Args:
            prompt: The prompt to send
            provider: 'openrouter' or 'gemini' (defaults to env var)
            model: Model name (defaults based on provider)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Dict with 'response', 'provider', 'model', 'usage'
        """
        provider = provider or self.default_provider
        
        if provider == "openrouter":
            return self._call_openrouter(prompt, model, max_tokens, temperature)
        elif provider == "gemini":
            return self._call_gemini(prompt, model, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _call_openrouter(
        self,
        prompt: str,
        model: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call OpenRouter API"""
        if not self.openrouter_key:
            raise ValueError("OPENROUTER_API_KEY not set")
        
        model = model or "openai/gpt-3.5-turbo"
        url = "https://openrouter.ai/api/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openrouter_key}",
            "HTTP-Referer": "https://github.com/ai-driven-self-healing-cloud",
            "X-Title": "AI-Driven Self-Healing Cloud"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "response": data["choices"][0]["message"]["content"],
            "provider": "openrouter",
            "model": model,
            "usage": data.get("usage", {}),
            "timestamp": time.time()
        }
    
    def _call_gemini(
        self,
        prompt: str,
        model: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Call Gemini API"""
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        model = model or "gemini-pro"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "response": data["candidates"][0]["content"]["parts"][0]["text"],
            "provider": "gemini",
            "model": model,
            "usage": {},
            "timestamp": time.time()
        }


# Global LLM client instance
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


# Enhanced functions for coding agent

def call_openrouter(prompt: str, model: Optional[str] = None, max_tokens: int = 2000) -> Dict[str, Any]:
    """Call OpenRouter API directly"""
    client = get_llm_client()
    return client.call_llm(prompt, provider="openrouter", model=model, max_tokens=max_tokens)


def call_gemini(prompt: str, model: Optional[str] = None, max_tokens: int = 2000) -> Dict[str, Any]:
    """Call Gemini API directly"""
    client = get_llm_client()
    return client.call_llm(prompt, provider="gemini", model=model, max_tokens=max_tokens)


def choose_best_model(error_type: str) -> tuple[str, str]:
    """
    Choose the best model based on error type
    
    Args:
        error_type: Type of error (syntax, runtime, logic, etc.)
    
    Returns:
        Tuple of (provider, model_name)
    """
    # Model selection logic
    if error_type in ["syntax", "type", "import"]:
        # Simple errors - use faster/cheaper model
        return ("openrouter", "openai/gpt-3.5-turbo")
    elif error_type in ["runtime", "logic", "performance"]:
        # Complex errors - use more capable model
        return ("openrouter", "openai/gpt-4")
    elif error_type in ["security", "vulnerability"]:
        # Security issues - use Gemini for better analysis
        return ("gemini", "gemini-pro")
    else:
        # Default to GPT-4 for unknown types
        return ("openrouter", "openai/gpt-4")


def generate_code(specs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate code based on specifications
    
    Args:
        specs: Dict with 'description', 'language', 'requirements', etc.
    
    Returns:
        Dict with generated code, explanation, and metadata
    """
    client = get_llm_client()
    
    description = specs.get("description", "")
    language = specs.get("language", "python")
    requirements = specs.get("requirements", "")
    context = specs.get("context", "")
    
    prompt = f"""Generate {language} code based on these specifications:

Description:
{description}

Requirements:
{requirements}
"""
    
    if context:
        prompt += f"\n\nContext:\n{context}"
    
    prompt += "\n\nProvide:\n1. Complete, production-ready code\n2. Brief explanation of the implementation\n3. Usage example\n4. Any important notes"
    
    # Use GPT-4 for code generation
    response = client.call_llm(
        prompt,
        provider="openrouter",
        model="openai/gpt-4",
        max_tokens=3000,
        temperature=0.3  # Lower temperature for more deterministic code
    )
    
    return {
        "code": response["response"],
        "provider": response["provider"],
        "model": response["model"],
        "language": language,
        "timestamp": response["timestamp"]
    }


def fix_code(error_log: str, file_content: str, stacktrace: Optional[str] = None) -> Dict[str, Any]:
    """
    Fix code based on error log and file content
    
    Args:
        error_log: Error message or log
        file_content: Current file content
        stacktrace: Optional stacktrace
    
    Returns:
        Dict with fixed code, patch, and explanation
    """
    client = get_llm_client()
    
    # Determine error type for model selection
    error_type = "runtime"  # Default
    if "SyntaxError" in error_log or "syntax" in error_log.lower():
        error_type = "syntax"
    elif "TypeError" in error_log or "type" in error_log.lower():
        error_type = "type"
    elif "ImportError" in error_log or "import" in error_log.lower():
        error_type = "import"
    
    provider, model = choose_best_model(error_type)
    
    prompt = f"""Fix this code error:

Error:
{error_log}
"""
    
    if stacktrace:
        prompt += f"\n\nStacktrace:\n{stacktrace}"
    
    prompt += f"\n\nCurrent Code:\n```\n{file_content}\n```\n\n"
    prompt += "Provide:\n1. Fixed code (complete, working version)\n2. Explanation of what was wrong and why the fix works\n3. Code diff/patch showing changes\n4. Any additional recommendations"
    
    response = client.call_llm(
        prompt,
        provider=provider,
        model=model,
        max_tokens=3000,
        temperature=0.2  # Very low temperature for accurate fixes
    )
    
    # Extract code and explanation from response
    # In Phase 5, this will parse structured JSON response
    fixed_code = response["response"]
    explanation = response["response"]  # Will be parsed in Phase 5
    
    return {
        "fixed_code": fixed_code,
        "patch": "",  # Will be generated in return_patch
        "explanation": explanation,
        "provider": response["provider"],
        "model": response["model"],
        "error_type": error_type,
        "timestamp": response["timestamp"]
    }


def return_patch(original_code: str, fixed_code: str) -> str:
    """
    Generate a code patch/diff between original and fixed code
    
    Args:
        original_code: Original code
        fixed_code: Fixed code
    
    Returns:
        Patch string in unified diff format
    """
    # Simple patch generation - in Phase 5, use proper diff library
    # For now, return a placeholder format
    
    lines_original = original_code.split('\n')
    lines_fixed = fixed_code.split('\n')
    
    patch = "--- original\n+++ fixed\n"
    
    # Simple line-by-line comparison
    max_len = max(len(lines_original), len(lines_fixed))
    for i in range(max_len):
        if i < len(lines_original) and i < len(lines_fixed):
            if lines_original[i] != lines_fixed[i]:
                patch += f"-{lines_original[i]}\n"
                patch += f"+{lines_fixed[i]}\n"
        elif i < len(lines_original):
            patch += f"-{lines_original[i]}\n"
        elif i < len(lines_fixed):
            patch += f"+{lines_fixed[i]}\n"
    
    return patch

