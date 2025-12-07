"""
Optimization Agent
Reduces cost and suggests infrastructure improvements
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
from optimizer import CostOptimizer


class OptimizationAgent:
    """Agent for cost optimization and infrastructure improvements"""
    
    def __init__(self):
        self.agent_id = "optimization-agent"
        self.name = "Optimization Agent"
        self.description = "Reduces cost and suggests infrastructure improvements"
        self.status = "stopped"
        self.logger = self._setup_logger()
        self.optimizer = CostOptimizer()
    
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
    
    def optimize_cost(
        self,
        infrastructure_data: Dict[str, Any],
        current_costs: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Optimize infrastructure costs
        
        Args:
            infrastructure_data: Current infrastructure configuration
            current_costs: Current cost breakdown
        
        Returns:
            Dict with optimization recommendations and potential savings
        """
        self.logger.info("Optimizing costs")
        return self.optimizer.optimize_cost(infrastructure_data, current_costs)
    
    def recommend_architecture(
        self,
        requirements: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend infrastructure architecture improvements
        
        Args:
            requirements: System requirements
            constraints: Budget or technical constraints
        
        Returns:
            Dict with architecture recommendations
        """
        self.logger.info("Generating architecture recommendations")
        return self.optimizer.recommend_architecture(requirements, constraints)
    
    def explain_action(self, input_data: Any, output_data: Any = None) -> Dict[str, Any]:
        """Provide explanation for actions (Explainability Layer)"""
        from explain import explain_action
        return explain_action(self.name, input_data, output_data)


def main():
    """Main entry point for testing"""
    agent = OptimizationAgent()
    agent.start()
    
    # Test cost optimization
    result = agent.optimize_cost(
        infrastructure_data={"instances": 10, "type": "m5.large"},
        current_costs={"monthly": 1000.0}
    )
    print(json.dumps(result, indent=2))
    
    agent.stop()


if __name__ == "__main__":
    main()

