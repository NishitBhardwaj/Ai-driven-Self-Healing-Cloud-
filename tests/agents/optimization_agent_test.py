"""
Unit tests for Optimization Agent
Tests cost optimization recommendations
"""

import unittest
import sys
import os

# Add parent directory to path to import agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.optimization.agent import OptimizationAgent


class TestOptimizationAgent(unittest.TestCase):
    """Test cases for Optimization Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = OptimizationAgent()
        self.agent.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.agent.stop()
    
    def test_agent_health_check(self):
        """Test that agent health check works"""
        self.assertEqual(self.agent.status, "running", "Agent should be running")
        self.assertIsNotNone(self.agent.agent_id, "Agent should have ID")
        self.assertIsNotNone(self.agent.name, "Agent should have name")
    
    def test_cost_optimization_recommendations(self):
        """Test that agent generates cost optimization recommendations"""
        infrastructure_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.large",
                    "cpu_usage": 0.25,
                    "memory_usage": 0.30
                },
                {
                    "id": "instance-2",
                    "type": "t3.xlarge",
                    "cpu_usage": 0.15,
                    "memory_usage": 0.20
                }
            ]
        }
        
        current_costs = {
            "instance-1": 0.10,
            "instance-2": 0.20,
            "total": 0.30
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should generate recommendations")
        self.assertIn("recommendations", recommendations, "Result should contain recommendations")
        
        # Verify recommendations structure
        if "recommendations" in recommendations:
            recs = recommendations["recommendations"]
            self.assertIsInstance(recs, list, "Recommendations should be a list")
            if len(recs) > 0:
                rec = recs[0]
                self.assertIn("action", rec, "Recommendation should have action")
                self.assertIn("savings", rec, "Recommendation should have savings estimate")
    
    def test_underutilized_resources(self):
        """Test detection of underutilized resources"""
        resource_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.xlarge",
                    "cost_per_hour": 0.20,
                    "cpu_usage": 0.10,  # Very low usage
                    "memory_usage": 0.15
                }
            ],
            "total_cost": 0.20
        }
        
        infrastructure_data = {
            "instances": resource_data.get("instances", [])
        }
        current_costs = {
            "total": resource_data.get("total_cost", 0.20)
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should detect underutilized resources")
        
        # Verify downscaling recommendation
        if "recommendations" in recommendations:
            recs = recommendations["recommendations"]
            for rec in recs:
                if "downscale" in rec.get("action", "").lower() or "resize" in rec.get("action", "").lower():
                    self.assertIn("savings", rec, "Should estimate savings")
                    break
    
    def test_rightsizing_recommendations(self):
        """Test rightsizing recommendations"""
        resource_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.large",
                    "cost_per_hour": 0.10,
                    "cpu_usage": 0.95,  # High usage - needs larger instance
                    "memory_usage": 0.90
                }
            ],
            "total_cost": 0.10
        }
        
        infrastructure_data = {
            "instances": resource_data.get("instances", [])
        }
        current_costs = {
            "total": resource_data.get("total_cost", 0.20)
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should provide rightsizing recommendations")
    
    def test_idle_resource_detection(self):
        """Test detection of idle resources"""
        resource_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.medium",
                    "cost_per_hour": 0.05,
                    "cpu_usage": 0.01,  # Almost idle
                    "memory_usage": 0.02,
                    "network_io": 0.001
                }
            ],
            "total_cost": 0.05
        }
        
        infrastructure_data = {
            "instances": resource_data.get("instances", [])
        }
        current_costs = {
            "total": resource_data.get("total_cost", 0.20)
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should detect idle resources")
        
        # Verify termination or stop recommendation
        if "recommendations" in recommendations:
            recs = recommendations["recommendations"]
            for rec in recs:
                action = rec.get("action", "").lower()
                if "terminate" in action or "stop" in action:
                    self.assertIn("savings", rec, "Should estimate savings from termination")
                    break
    
    def test_cost_savings_calculation(self):
        """Test cost savings calculation"""
        resource_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.large",
                    "cost_per_hour": 0.10,
                    "cpu_usage": 0.20,
                    "memory_usage": 0.25
                }
            ],
            "total_cost": 0.10
        }
        
        infrastructure_data = {
            "instances": resource_data.get("instances", [])
        }
        current_costs = {
            "total": resource_data.get("total_cost", 0.20)
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should calculate cost savings")
        
        # Verify savings are calculated
        if "recommendations" in recommendations:
            recs = recommendations["recommendations"]
            for rec in recs:
                if "savings" in rec:
                    savings = rec["savings"]
                    self.assertIsInstance(savings, (int, float), "Savings should be a number")
                    self.assertGreaterEqual(savings, 0, "Savings should be non-negative")
    
    def test_explain_action(self):
        """Test explanation generation"""
        input_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.large",
                    "cost_per_hour": 0.10,
                    "cpu_usage": 0.20
                }
            ]
        }
        
        output_data = {
            "recommendations": [
                {
                    "action": "downscale",
                    "savings": 0.05
                }
            ]
        }
        
        explanation = self.agent.explain_action(input_data, output_data)
        
        self.assertIsNotNone(explanation, "Explanation should be generated")
        self.assertIn("message", explanation, "Explanation should have message")
        self.assertIn("explanation", explanation, "Explanation should have explanation text")
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        # Test with empty data
        result = self.agent.optimize_cost(
            infrastructure_data={},
            current_costs={}
        )
        
        # Should handle gracefully
        self.assertIsNotNone(result, "Should return result even with empty input")
    
    def test_multiple_optimization_strategies(self):
        """Test multiple optimization strategies"""
        infrastructure_data = {
            "instances": [
                {
                    "id": "instance-1",
                    "type": "t3.large",
                    "cpu_usage": 0.25
                },
                {
                    "id": "instance-2",
                    "type": "t3.xlarge",
                    "cpu_usage": 0.15
                }
            ]
        }
        
        current_costs = {
            "instance-1": 0.10,
            "instance-2": 0.20,
            "total": 0.30
        }
        
        recommendations = self.agent.optimize_cost(
            infrastructure_data=infrastructure_data,
            current_costs=current_costs
        )
        
        self.assertIsNotNone(recommendations, "Should provide multiple strategies")
        
        # Verify multiple recommendations
        if "recommendations" in recommendations:
            recs = recommendations["recommendations"]
            self.assertGreater(len(recs), 0, "Should provide at least one recommendation")


if __name__ == '__main__':
    unittest.main()

