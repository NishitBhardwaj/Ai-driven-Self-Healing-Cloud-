"""
Continuous Learning Pipeline
Orchestrates data collection, model training, and policy updates
"""

import time
import logging
from typing import Dict, List, Optional
from pathlib import Path
import threading
from datetime import datetime

from .data_collector import DataCollector
from .rl_feedback_loop import RLFeedbackLoop, SelfHealingRLFeedback, ScalingRLFeedback

logger = logging.getLogger(__name__)


class LearningPipeline:
    """Main pipeline for continuous learning"""
    
    def __init__(self, storage_path: str = "data/continuous-learning"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_collector = DataCollector(str(self.storage_path))
        
        # Initialize RL feedback loops for each agent
        self.feedback_loops: Dict[str, RLFeedbackLoop] = {
            "self-healing": SelfHealingRLFeedback(),
            "scaling": ScalingRLFeedback(),
            "task-solving": RLFeedbackLoop("task-solving"),
            "performance-monitoring": RLFeedbackLoop("performance-monitoring"),
            "coding": RLFeedbackLoop("coding"),
            "security": RLFeedbackLoop("security"),
            "optimization": RLFeedbackLoop("optimization"),
        }
        
        # Pipeline configuration
        self.retrain_interval = 3600  # 1 hour
        self.evaluation_interval = 300  # 5 minutes
        self.last_retrain_time = time.time()
        self.last_evaluation_time = time.time()
        
        # Running state
        self.running = False
        self.pipeline_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the continuous learning pipeline"""
        if self.running:
            logger.warning("Learning pipeline is already running")
            return
        
        self.running = True
        self.pipeline_thread = threading.Thread(target=self._run_pipeline, daemon=True)
        self.pipeline_thread.start()
        logger.info("Continuous learning pipeline started")
    
    def stop(self):
        """Stop the continuous learning pipeline"""
        self.running = False
        if self.pipeline_thread:
            self.pipeline_thread.join(timeout=10)
        logger.info("Continuous learning pipeline stopped")
    
    def _run_pipeline(self):
        """Main pipeline loop"""
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic evaluation
                if current_time - self.last_evaluation_time >= self.evaluation_interval:
                    self._evaluate_performance()
                    self.last_evaluation_time = current_time
                
                # Periodic retraining
                if current_time - self.last_retrain_time >= self.retrain_interval:
                    self._check_retraining()
                    self.last_retrain_time = current_time
                
                # Flush data buffers
                self.data_collector.flush_all()
                
                # Sleep for a short interval
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in learning pipeline: {e}", exc_info=True)
                time.sleep(60)
    
    def _evaluate_performance(self):
        """Evaluate agent performance and generate recommendations"""
        logger.info("Evaluating agent performance...")
        
        for agent_name, feedback_loop in self.feedback_loops.items():
            recommendations = feedback_loop.get_policy_recommendations()
            
            logger.info(
                f"Agent {agent_name} - "
                f"Success Rate: {recommendations['success_rate']:.2%}, "
                f"Avg Reward: {recommendations['average_reward']:.2f}"
            )
            
            if recommendations['recommendations']:
                logger.info(f"Recommendations for {agent_name}:")
                for rec in recommendations['recommendations']:
                    logger.info(f"  - {rec['suggestion']}")
    
    def _check_retraining(self):
        """Check if models need retraining"""
        logger.info("Checking if models need retraining...")
        
        for agent_name, feedback_loop in self.feedback_loops.items():
            if feedback_loop.should_retrain():
                logger.info(f"Retraining recommended for {agent_name}")
                # Trigger retraining (to be implemented)
                self._trigger_retraining(agent_name)
    
    def _trigger_retraining(self, agent_name: str):
        """Trigger model retraining for an agent"""
        logger.info(f"Triggering retraining for {agent_name}...")
        
        # Get recent data
        actions = self.data_collector.get_recent_actions(agent_name, limit=10000)
        metrics = self.data_collector.get_recent_metrics(agent_name, limit=10000)
        
        if len(actions) < 100:
            logger.warning(f"Insufficient data for retraining {agent_name}: {len(actions)} actions")
            return
        
        # Save retraining trigger
        retrain_info = {
            "agent_name": agent_name,
            "timestamp": time.time(),
            "action_count": len(actions),
            "metric_count": len(metrics),
            "status": "pending"
        }
        
        retrain_file = self.storage_path / f"retrain_{agent_name}_{int(time.time())}.json"
        import json
        with open(retrain_file, 'w') as f:
            json.dump(retrain_info, f, indent=2)
        
        logger.info(f"Retraining trigger saved: {retrain_file}")
    
    def record_action(
        self,
        agent_name: str,
        action_type: str,
        input_data: Dict,
        output_data: Dict,
        success: bool,
        execution_time: float,
        confidence: float,
        explanation: str,
        context: Optional[Dict] = None
    ):
        """Record an agent action for learning"""
        # Collect data
        self.data_collector.collect_action(
            agent_name=agent_name,
            action_type=action_type,
            input_data=input_data,
            output_data=output_data,
            success=success,
            execution_time=execution_time,
            confidence=confidence,
            explanation=explanation,
            context=context
        )
        
        # Update RL feedback if agent has feedback loop
        if agent_name in self.feedback_loops:
            feedback_loop = self.feedback_loops[agent_name]
            
            # Special handling for self-healing agent
            if agent_name == "self-healing" and isinstance(feedback_loop, SelfHealingRLFeedback):
                failure_type = context.get("failure_type") if context else None
                feedback_loop.update_healing_feedback(
                    success=success,
                    recovery_time=execution_time,
                    healing_action=action_type,
                    failure_type=failure_type,
                    context=context
                )
            # Special handling for scaling agent
            elif agent_name == "scaling" and isinstance(feedback_loop, ScalingRLFeedback):
                resource_utilization = context.get("resource_utilization", 0.5) if context else 0.5
                feedback_loop.update_scaling_feedback(
                    success=success,
                    recovery_time=execution_time,
                    scaling_action=action_type,
                    resource_utilization=resource_utilization,
                    context=context
                )
            else:
                # Generic feedback update
                feedback_loop.update_reward(
                    success=success,
                    recovery_time=execution_time,
                    action_type=action_type,
                    context=context
                )
    
    def record_metric(
        self,
        agent_name: str,
        cpu_usage: float,
        memory_usage: float,
        response_time: float,
        throughput: float,
        error_rate: float,
        success_rate: float
    ):
        """Record performance metrics"""
        self.data_collector.collect_metric(
            agent_name=agent_name,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            success_rate=success_rate
        )
    
    def record_task_result(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        status: str,
        execution_time: float,
        input_data: Dict,
        output_data: Dict,
        error_message: Optional[str] = None
    ):
        """Record task execution result"""
        self.data_collector.collect_task_result(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            status=status,
            execution_time=execution_time,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message
        )
    
    def get_feedback_loop(self, agent_name: str) -> Optional[RLFeedbackLoop]:
        """Get feedback loop for an agent"""
        return self.feedback_loops.get(agent_name)
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for all agents"""
        summary = {
            "timestamp": time.time(),
            "agents": {}
        }
        
        for agent_name, feedback_loop in self.feedback_loops.items():
            summary["agents"][agent_name] = {
                "success_rate": feedback_loop.get_success_rate(),
                "average_reward": feedback_loop.get_average_reward(),
                "total_actions": len(feedback_loop.action_history),
                "recommendations": feedback_loop.get_policy_recommendations()["recommendations"]
            }
        
        return summary

