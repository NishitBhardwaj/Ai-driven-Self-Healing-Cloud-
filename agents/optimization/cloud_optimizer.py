"""
Cloud Service Optimization
Tracks cloud resource usage and suggests cost-saving measures
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class CloudResource:
    """Cloud resource instance"""
    resource_id: str
    resource_type: str  # "ec2", "rds", "s3", "lambda", etc.
    region: str
    instance_type: Optional[str] = None
    status: str = "running"  # "running", "stopped", "idle"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    cost_per_hour: float = 0.0
    uptime_hours: float = 0.0
    idle_hours: float = 0.0
    last_activity: float = 0.0


@dataclass
class CostSavingRecommendation:
    """Cost-saving recommendation"""
    recommendation_id: str
    resource_id: str
    resource_type: str
    recommendation_type: str  # "terminate", "resize", "reserve", "spot"
    current_cost: float
    potential_savings: float
    savings_percentage: float
    reasoning: str
    risk_level: str  # "low", "medium", "high"
    implementation_steps: List[str]


class CloudOptimizer:
    """Optimizes cloud resource usage and suggests cost-saving measures"""
    
    def __init__(self):
        # Resource tracking
        self.resources: Dict[str, CloudResource] = {}
        
        # Usage patterns
        self.usage_patterns: Dict[str, List[Dict]] = defaultdict(list)
        
        # Cost-saving recommendations
        self.recommendations: List[CostSavingRecommendation] = []
        
        # Optimization thresholds
        self.thresholds = {
            "idle_threshold_hours": 24,  # Consider idle after 24 hours
            "low_utilization_threshold": 0.2,  # 20% utilization
            "high_utilization_threshold": 0.8,  # 80% utilization
            "min_savings_threshold": 10.0  # Minimum $10/month savings
        }
        
        # Storage
        self.storage_path = Path("data/optimization/cloud")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def register_resource(
        self,
        resource_id: str,
        resource_type: str,
        region: str,
        instance_type: Optional[str] = None,
        cost_per_hour: float = 0.0
    ):
        """Register a cloud resource for tracking"""
        resource = CloudResource(
            resource_id=resource_id,
            resource_type=resource_type,
            region=region,
            instance_type=instance_type,
            cost_per_hour=cost_per_hour,
            last_activity=time.time()
        )
        
        self.resources[resource_id] = resource
        logger.info(f"Registered resource: {resource_id} ({resource_type})")
    
    def update_resource_usage(
        self,
        resource_id: str,
        cpu_usage: float,
        memory_usage: float,
        status: str = "running"
    ):
        """Update resource usage metrics"""
        if resource_id not in self.resources:
            logger.warning(f"Resource {resource_id} not registered")
            return
        
        resource = self.resources[resource_id]
        resource.cpu_usage = cpu_usage
        resource.memory_usage = memory_usage
        resource.status = status
        
        if cpu_usage > 0 or memory_usage > 0:
            resource.last_activity = time.time()
        
        # Track usage pattern
        self.usage_patterns[resource_id].append({
            "timestamp": time.time(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "status": status
        })
        
        # Keep only recent patterns (last 1000 entries)
        if len(self.usage_patterns[resource_id]) > 1000:
            self.usage_patterns[resource_id] = self.usage_patterns[resource_id][-1000:]
    
    def analyze_idle_resources(self) -> List[CostSavingRecommendation]:
        """Identify and recommend actions for idle resources"""
        recommendations = []
        current_time = time.time()
        
        for resource_id, resource in self.resources.items():
            if resource.status != "running":
                continue
            
            # Calculate idle time
            idle_hours = (current_time - resource.last_activity) / 3600
            
            if idle_hours > self.thresholds["idle_threshold_hours"]:
                # Resource is idle
                monthly_cost = resource.cost_per_hour * 24 * 30
                potential_savings = monthly_cost  # 100% savings if terminated
                
                if potential_savings >= self.thresholds["min_savings_threshold"]:
                    recommendation = CostSavingRecommendation(
                        recommendation_id=f"idle_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        resource_type=resource.resource_type,
                        recommendation_type="terminate",
                        current_cost=monthly_cost,
                        potential_savings=potential_savings,
                        savings_percentage=100.0,
                        reasoning=f"Resource has been idle for {idle_hours:.1f} hours (threshold: {self.thresholds['idle_threshold_hours']} hours)",
                        risk_level="low",
                        implementation_steps=[
                            f"Verify resource {resource_id} is not needed",
                            f"Stop/terminate {resource_id}",
                            f"Monitor for 7 days to ensure no impact",
                            f"Expected savings: ${potential_savings:.2f}/month"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_underutilized_resources(self) -> List[CostSavingRecommendation]:
        """Identify underutilized resources that can be downsized"""
        recommendations = []
        
        for resource_id, resource in self.resources.items():
            if resource.status != "running":
                continue
            
            avg_utilization = (resource.cpu_usage + resource.memory_usage) / 2
            
            if avg_utilization < self.thresholds["low_utilization_threshold"]:
                # Resource is underutilized
                monthly_cost = resource.cost_per_hour * 24 * 30
                
                # Estimate savings from downsizing (simplified - 50% cost reduction)
                potential_savings = monthly_cost * 0.5
                
                if potential_savings >= self.thresholds["min_savings_threshold"]:
                    recommendation = CostSavingRecommendation(
                        recommendation_id=f"downsize_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        resource_type=resource.resource_type,
                        recommendation_type="resize",
                        current_cost=monthly_cost,
                        potential_savings=potential_savings,
                        savings_percentage=50.0,
                        reasoning=f"Resource utilization is {avg_utilization:.2%} (threshold: {self.thresholds['low_utilization_threshold']:.2%})",
                        risk_level="medium",
                        implementation_steps=[
                            f"Analyze usage patterns for {resource_id}",
                            f"Identify smaller instance type",
                            f"Test resize in staging environment",
                            f"Resize {resource_id} during maintenance window",
                            f"Expected savings: ${potential_savings:.2f}/month"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_reserved_instance_opportunities(self) -> List[CostSavingRecommendation]:
        """Identify resources that could benefit from reserved instances"""
        recommendations = []
        
        for resource_id, resource in self.resources.items():
            if resource.status != "running":
                continue
            
            # Check if resource runs consistently (simplified check)
            usage_pattern = self.usage_patterns.get(resource_id, [])
            if len(usage_pattern) < 100:
                continue
            
            # Calculate uptime percentage
            running_count = sum(1 for u in usage_pattern if u["status"] == "running")
            uptime_percentage = running_count / len(usage_pattern)
            
            # If uptime > 80%, consider reserved instance
            if uptime_percentage > 0.8:
                monthly_cost = resource.cost_per_hour * 24 * 30
                # Reserved instances typically save 30-50%
                potential_savings = monthly_cost * 0.4  # 40% savings estimate
                
                if potential_savings >= self.thresholds["min_savings_threshold"]:
                    recommendation = CostSavingRecommendation(
                        recommendation_id=f"reserve_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        resource_type=resource.resource_type,
                        recommendation_type="reserve",
                        current_cost=monthly_cost,
                        potential_savings=potential_savings,
                        savings_percentage=40.0,
                        reasoning=f"Resource has {uptime_percentage:.2%} uptime, suitable for reserved instance",
                        risk_level="low",
                        implementation_steps=[
                            f"Analyze 1-year usage forecast for {resource_id}",
                            f"Purchase 1-year reserved instance",
                            f"Replace on-demand instance with reserved instance",
                            f"Expected savings: ${potential_savings:.2f}/month"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def analyze_spot_instance_opportunities(self) -> List[CostSavingRecommendation]:
        """Identify workloads suitable for spot instances"""
        recommendations = []
        
        for resource_id, resource in self.resources.items():
            if resource.resource_type != "ec2":
                continue
            
            # Check if workload is fault-tolerant (simplified)
            # In practice, analyze workload characteristics
            avg_utilization = (resource.cpu_usage + resource.memory_usage) / 2
            
            # Spot instances suitable for fault-tolerant, flexible workloads
            if 0.3 <= avg_utilization <= 0.7:  # Moderate utilization
                monthly_cost = resource.cost_per_hour * 24 * 30
                # Spot instances typically save 50-90%
                potential_savings = monthly_cost * 0.7  # 70% savings estimate
                
                if potential_savings >= self.thresholds["min_savings_threshold"]:
                    recommendation = CostSavingRecommendation(
                        recommendation_id=f"spot_{resource_id}_{int(time.time())}",
                        resource_id=resource_id,
                        resource_type=resource.resource_type,
                        recommendation_type="spot",
                        current_cost=monthly_cost,
                        potential_savings=potential_savings,
                        savings_percentage=70.0,
                        reasoning=f"Workload has moderate utilization ({avg_utilization:.2%}), suitable for spot instances",
                        risk_level="medium",
                        implementation_steps=[
                            f"Verify workload can handle interruptions",
                            f"Set up spot instance fleet",
                            f"Implement checkpointing/state management",
                            f"Migrate workload to spot instances",
                            f"Expected savings: ${potential_savings:.2f}/month"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def generate_cost_saving_recommendations(self) -> List[CostSavingRecommendation]:
        """Generate all cost-saving recommendations"""
        logger.info("Generating cost-saving recommendations...")
        
        recommendations = []
        
        # Analyze idle resources
        recommendations.extend(self.analyze_idle_resources())
        
        # Analyze underutilized resources
        recommendations.extend(self.analyze_underutilized_resources())
        
        # Analyze reserved instance opportunities
        recommendations.extend(self.analyze_reserved_instance_opportunities())
        
        # Analyze spot instance opportunities
        recommendations.extend(self.analyze_spot_instance_opportunities())
        
        # Sort by potential savings
        recommendations.sort(key=lambda x: x.potential_savings, reverse=True)
        
        self.recommendations = recommendations
        
        total_potential_savings = sum(r.potential_savings for r in recommendations)
        logger.info(f"Generated {len(recommendations)} recommendations, total potential savings: ${total_potential_savings:.2f}/month")
        
        return recommendations
    
    def get_cost_summary(self) -> Dict:
        """Get summary of cloud costs and optimization opportunities"""
        total_monthly_cost = sum(
            r.cost_per_hour * 24 * 30
            for r in self.resources.values()
            if r.status == "running"
        )
        
        total_potential_savings = sum(r.potential_savings for r in self.recommendations)
        savings_percentage = (total_potential_savings / total_monthly_cost * 100) if total_monthly_cost > 0 else 0
        
        return {
            "total_resources": len(self.resources),
            "running_resources": sum(1 for r in self.resources.values() if r.status == "running"),
            "total_monthly_cost": total_monthly_cost,
            "total_potential_savings": total_potential_savings,
            "savings_percentage": savings_percentage,
            "recommendations_count": len(self.recommendations),
            "recommendations_by_type": {
                "terminate": sum(1 for r in self.recommendations if r.recommendation_type == "terminate"),
                "resize": sum(1 for r in self.recommendations if r.recommendation_type == "resize"),
                "reserve": sum(1 for r in self.recommendations if r.recommendation_type == "reserve"),
                "spot": sum(1 for r in self.recommendations if r.recommendation_type == "spot")
            }
        }
    
    def save_recommendations(self):
        """Save recommendations to disk"""
        if not self.recommendations:
            return
        
        timestamp = int(time.time())
        file_path = self.storage_path / f"cost_recommendations_{timestamp}.json"
        
        recommendations_data = {
            "timestamp": timestamp,
            "recommendations": [asdict(r) for r in self.recommendations],
            "summary": self.get_cost_summary()
        }
        
        with open(file_path, 'w') as f:
            json.dump(recommendations_data, f, indent=2)
        
        logger.info(f"Saved {len(self.recommendations)} recommendations to {file_path}")

