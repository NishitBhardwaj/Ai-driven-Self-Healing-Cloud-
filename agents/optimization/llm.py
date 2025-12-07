"""
LLM module for Optimization Agent (shared with other Python agents)
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
        """Call LLM API (OpenRouter or Gemini)"""
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
            "messages": [{"role": "user", "content": prompt}],
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
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
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


_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

