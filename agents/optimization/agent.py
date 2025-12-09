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
from elk_logging import get_elk_logger
from self_optimization import SelfOptimizationSystem


class OptimizationAgent:
    """Agent for cost optimization and infrastructure improvements"""
    
    def __init__(self):
        self.agent_id = "optimization-agent"
        self.name = "Optimization Agent"
        self.description = "Reduces cost and suggests infrastructure improvements"
        self.status = "stopped"
        self.logger = self._setup_logger()
        self.optimizer = CostOptimizer()
        self.self_optimization = SelfOptimizationSystem()
    
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
        # Start self-optimization system
        self.self_optimization.start()
        return True
    
    def stop(self) -> bool:
        """Stop the agent"""
        self.logger.info(f"Stopping {self.name}")
        # Stop self-optimization system
        self.self_optimization.stop()
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
        
        # Log action trigger to ELK
        elk_logger = get_elk_logger()
        elk_logger.log_action_trigger("optimize_cost", {
            "instances_count": len(infrastructure_data.get("instances", [])),
            "total_cost": current_costs.get("total", 0.0)
        }, None)
        
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
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary"""
        return self.self_optimization.get_optimization_summary()
    
    def get_cost_recommendations(self) -> Dict[str, Any]:
        """Get cost-saving recommendations"""
        recommendations = self.self_optimization.get_cost_recommendations()
        return {
            "recommendations": recommendations,
            "count": len(recommendations),
            "total_potential_savings": sum(r.get("potential_savings", 0) for r in recommendations)
        }
    
    def record_resource_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_io: float,
        response_time: float,
        throughput: float,
        error_rate: float,
        cost_per_hour: float
    ):
        """Record resource metrics for optimization"""
        self.self_optimization.record_resource_metrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            cost_per_hour=cost_per_hour
        )
    
    def get_scaling_decision(
        self,
        current_cpu: float,
        current_memory: float,
        current_requests: float,
        current_replicas: int
    ) -> Dict[str, Any]:
        """Get optimized scaling decision based on load predictions"""
        decision = self.self_optimization.get_scaling_decision(
            current_cpu=current_cpu,
            current_memory=current_memory,
            current_requests=current_requests,
            current_replicas=current_replicas
        )
        return {
            "action": decision.action,
            "target_replicas": decision.target_replicas,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "predicted_cpu": decision.predicted_cpu,
            "predicted_memory": decision.predicted_memory
        }


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

