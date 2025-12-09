"""
Self-Optimization System
Integrates all optimization components for continuous self-improvement
"""

import time
import logging
from typing import Dict, List, Optional
from pathlib import Path
import threading

from .optimization_feedback import OptimizationFeedbackSystem, ResourceMetrics
from .autoscaling_optimizer import AutoScalingOptimizer
from .cloud_optimizer import CloudOptimizer

logger = logging.getLogger(__name__)


class SelfOptimizationSystem:
    """Main self-optimization system that coordinates all optimization components"""
    
    def __init__(self):
        # Initialize components
        self.feedback_system = OptimizationFeedbackSystem()
        self.autoscaling_optimizer = AutoScalingOptimizer()
        self.cloud_optimizer = CloudOptimizer()
        
        # Optimization intervals
        self.metrics_collection_interval = 60  # 1 minute
        self.optimization_interval = 300  # 5 minutes
        self.cost_analysis_interval = 3600  # 1 hour
        
        # Running state
        self.running = False
        self.optimization_thread: Optional[threading.Thread] = None
        
        # Integration with continuous learning
        self.learning_pipeline = None  # Will be set by integration
    
    def start(self):
        """Start the self-optimization system"""
        if self.running:
            logger.warning("Self-optimization system is already running")
            return
        
        self.running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("Self-optimization system started")
    
    def stop(self):
        """Stop the self-optimization system"""
        self.running = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=10)
        logger.info("Self-optimization system stopped")
    
    def _optimization_loop(self):
        """Main optimization loop"""
        last_metrics_collection = time.time()
        last_optimization = time.time()
        last_cost_analysis = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Collect metrics periodically
                if current_time - last_metrics_collection >= self.metrics_collection_interval:
                    self._collect_and_analyze_metrics()
                    last_metrics_collection = current_time
                
                # Run optimization periodically
                if current_time - last_optimization >= self.optimization_interval:
                    self._run_optimization()
                    last_optimization = current_time
                
                # Analyze costs periodically
                if current_time - last_cost_analysis >= self.cost_analysis_interval:
                    self._analyze_costs()
                    last_cost_analysis = current_time
                
                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}", exc_info=True)
                time.sleep(60)
    
    def _collect_and_analyze_metrics(self):
        """Collect current resource metrics"""
        # In production, this would fetch from monitoring system
        # For now, this is a placeholder that would be called with actual metrics
        logger.debug("Collecting resource metrics...")
    
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
        self.feedback_system.record_metrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            cost_per_hour=cost_per_hour
        )
    
    def record_scaling_metrics(
        self,
        cpu_usage: float,
        memory_usage: float,
        request_rate: float,
        current_replicas: int
    ):
        """Record scaling metrics for auto-scaling optimization"""
        self.autoscaling_optimizer.record_load(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            request_rate=request_rate,
            current_replicas=current_replicas
        )
    
    def get_scaling_decision(
        self,
        current_cpu: float,
        current_memory: float,
        current_requests: float,
        current_replicas: int
    ):
        """Get optimized scaling decision"""
        return self.autoscaling_optimizer.optimize_scaling_decision(
            current_cpu=current_cpu,
            current_memory=current_memory,
            current_requests=current_requests,
            current_replicas=current_replicas
        )
    
    def register_cloud_resource(
        self,
        resource_id: str,
        resource_type: str,
        region: str,
        instance_type: Optional[str] = None,
        cost_per_hour: float = 0.0
    ):
        """Register cloud resource for optimization"""
        self.cloud_optimizer.register_resource(
            resource_id=resource_id,
            resource_type=resource_type,
            region=region,
            instance_type=instance_type,
            cost_per_hour=cost_per_hour
        )
    
    def update_cloud_resource_usage(
        self,
        resource_id: str,
        cpu_usage: float,
        memory_usage: float,
        status: str = "running"
    ):
        """Update cloud resource usage"""
        self.cloud_optimizer.update_resource_usage(
            resource_id=resource_id,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            status=status
        )
    
    def _run_optimization(self):
        """Run optimization processes"""
        logger.info("Running optimization processes...")
        
        # Optimize cost function
        self.feedback_system.optimize_cost_function()
        
        # Update scaling thresholds
        # (Would use actual feedback data in production)
        # self.autoscaling_optimizer.update_thresholds_from_feedback(feedback_data)
        
        logger.info("Optimization processes completed")
    
    def _analyze_costs(self):
        """Analyze costs and generate recommendations"""
        logger.info("Analyzing cloud costs...")
        
        # Generate cost-saving recommendations
        recommendations = self.cloud_optimizer.generate_cost_saving_recommendations()
        
        # Save recommendations
        self.cloud_optimizer.save_recommendations()
        
        # Log top recommendations
        if recommendations:
            logger.info(f"Top cost-saving recommendations:")
            for rec in recommendations[:5]:
                logger.info(
                    f"  - {rec.resource_id}: {rec.recommendation_type} "
                    f"(Savings: ${rec.potential_savings:.2f}/month, Risk: {rec.risk_level})"
                )
    
    def evaluate_optimization_action(
        self,
        action_taken: str,
        resource_before: ResourceMetrics,
        resource_after: ResourceMetrics
    ):
        """Evaluate an optimization action and get feedback"""
        return self.feedback_system.evaluate_optimization(
            action_taken=action_taken,
            resource_before=resource_before,
            resource_after=resource_after
        )
    
    def get_optimization_summary(self) -> Dict:
        """Get comprehensive optimization summary"""
        feedback_summary = self.feedback_system.get_optimization_summary()
        scaling_summary = self.autoscaling_optimizer.get_scaling_summary()
        cost_summary = self.cloud_optimizer.get_cost_summary()
        
        return {
            "feedback": feedback_summary,
            "scaling": scaling_summary,
            "costs": cost_summary,
            "timestamp": time.time()
        }
    
    def get_cost_recommendations(self) -> List[Dict]:
        """Get cost-saving recommendations"""
        recommendations = self.cloud_optimizer.generate_cost_saving_recommendations()
        return [r.__dict__ for r in recommendations]
    
    def set_learning_pipeline(self, learning_pipeline):
        """Set the continuous learning pipeline for integration"""
        self.learning_pipeline = learning_pipeline
        logger.info("Learning pipeline integrated with self-optimization system")

