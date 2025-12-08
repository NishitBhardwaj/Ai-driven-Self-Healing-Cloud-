"""
Security Agent
Detects threats, IAM misconfiguration checks, and API abuse detection
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List
from detect import SecurityDetector
from ai_integration import SecurityAIIntegration


class SecurityAgent:
    """Agent for security threat detection and policy validation"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        self.agent_id = "security-agent"
        self.name = "Security Agent"
        self.description = "Detects threats using GNN dependencies + LLM threat model"
        self.status = "stopped"
        self.logger = self._setup_logger()
        self.detector = SecurityDetector()
        
        # Initialize AI Engine Integration
        self.ai_integration = SecurityAIIntegration(
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
        from llm import get_llm_client
        llm_client = get_llm_client()
        try:
            return llm_client.call_llm(prompt, provider=provider)
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
    
    def detect_intrusion(
        self,
        logs: List[Dict[str, Any]],
        network_traffic: Optional[Dict[str, Any]] = None,
        dependency_graph_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect intrusion attempts using GNN dependencies + LLM threat model
        
        Args:
            logs: Security logs to analyze
            network_traffic: Network traffic data
            dependency_graph_data: Dependency graph data (Kubernetes + LocalStack)
        
        Returns:
            Dict with detected threats and severity
        """
        self.logger.info("Detecting intrusions using AI Engine")
        
        try:
            # Use AI Engine Integration
            threat_result = self.ai_integration.detect_threat(
                security_logs=logs,
                dependency_graph_data=dependency_graph_data,
                network_traffic=network_traffic
            )
            
            # Also use basic detector as fallback
            basic_result = self.detector.detect_intrusion(logs, network_traffic)
            
            # Combine results
            return {
                **threat_result,
                "basic_detection": basic_result,
                "ai_enhanced": True
            }
        except Exception as e:
            self.logger.error(f"AI-powered threat detection failed: {e}, using basic detector")
            return {
                **self.detector.detect_intrusion(logs, network_traffic),
                "ai_enhanced": False,
                "error": str(e)
            }
    
    def validate_policy(
        self,
        policy: Dict[str, Any],
        policy_type: str = "iam",
        dependency_graph_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate security policy using GNN + LLM
        
        Args:
            policy: Policy configuration to validate
            policy_type: Type of policy (iam, network, etc.)
            dependency_graph_data: Dependency graph data
        
        Returns:
            Dict with validation results and issues
        """
        self.logger.info(f"Validating {policy_type} policy using AI Engine")
        
        try:
            # Use AI Engine Integration
            ai_result = self.ai_integration.validate_security_policy(
                policy=policy,
                dependency_graph_data=dependency_graph_data
            )
            
            # Also use basic detector
            basic_result = self.detector.validate_policy(policy, policy_type)
            
            return {
                **ai_result,
                "basic_validation": basic_result,
                "ai_enhanced": True
            }
        except Exception as e:
            self.logger.error(f"AI-powered policy validation failed: {e}, using basic detector")
            return {
                **self.detector.validate_policy(policy, policy_type),
                "ai_enhanced": False,
                "error": str(e)
            }
    
    def explain_action(self, input_data: Any, output_data: Any = None) -> Dict[str, Any]:
        """Provide explanation for actions (Explainability Layer)"""
        from explain import explain_action
        return explain_action(self.name, input_data, output_data)


def main():
    """Main entry point for testing"""
    agent = SecurityAgent()
    agent.start()
    
    # Test intrusion detection
    result = agent.detect_intrusion([
        {"source_ip": "192.168.1.100", "action": "failed_login", "count": 10}
    ])
    print(json.dumps(result, indent=2))
    
    agent.stop()


if __name__ == "__main__":
    main()

