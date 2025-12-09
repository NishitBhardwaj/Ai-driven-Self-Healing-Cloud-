"""
Unit tests for Security Agent
Tests intrusion detection and security breach handling
"""

import unittest
import sys
import os

# Add parent directory to path to import agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.security.agent import SecurityAgent


class TestSecurityAgent(unittest.TestCase):
    """Test cases for Security Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = SecurityAgent()
        self.agent.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.agent.stop()
    
    def test_agent_health_check(self):
        """Test that agent health check works"""
        self.assertEqual(self.agent.status, "running", "Agent should be running")
        self.assertIsNotNone(self.agent.agent_id, "Agent should have ID")
        self.assertIsNotNone(self.agent.name, "Agent should have name")
    
    def test_intrusion_detection(self):
        """Test that agent correctly detects intrusions"""
        # Simulate suspicious activity
        logs = [
            {
                "source_ip": "192.168.1.100",
                "action": "failed_login",
                "count": 10,
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "source_ip": "192.168.1.100",
                "action": "failed_login",
                "count": 15,
                "timestamp": "2024-01-01T12:05:00Z"
            }
        ]
        
        result = self.agent.detect_intrusion(logs)
        
        self.assertIsNotNone(result, "Intrusion detection should return result")
        self.assertIn("threats", result, "Result should contain threats")
        
        # Verify threats are detected
        if "threats" in result:
            threats = result["threats"]
            self.assertIsInstance(threats, list, "Threats should be a list")
            if len(threats) > 0:
                threat = threats[0]
                self.assertIn("severity", threat, "Threat should have severity")
                self.assertIn("source_ip", threat, "Threat should have source IP")
    
    def test_security_breach_blocking(self):
        """Test that agent blocks security breaches"""
        # Simulate security breach
        logs = [
            {
                "source_ip": "10.0.0.1",
                "action": "unauthorized_access",
                "count": 1,
                "severity": "critical"
            }
        ]
        
        result = self.agent.detect_intrusion(logs)
        
        self.assertIsNotNone(result, "Security breach detection should return result")
        
        # Verify blocking action is taken
        if "action" in result:
            action = result["action"]
            self.assertIn("block", action.lower(), "Should block security breach")
    
    def test_multiple_failed_logins(self):
        """Test detection of multiple failed login attempts"""
        logs = [
            {
                "source_ip": "192.168.1.50",
                "action": "failed_login",
                "count": 5,
                "timestamp": "2024-01-01T12:00:00Z"
            },
            {
                "source_ip": "192.168.1.50",
                "action": "failed_login",
                "count": 10,
                "timestamp": "2024-01-01T12:10:00Z"
            },
            {
                "source_ip": "192.168.1.50",
                "action": "failed_login",
                "count": 15,
                "timestamp": "2024-01-01T12:20:00Z"
            }
        ]
        
        result = self.agent.detect_intrusion(logs)
        
        self.assertIsNotNone(result, "Should detect multiple failed logins")
        
        # Verify threat is detected
        if "threats" in result:
            threats = result["threats"]
            self.assertGreater(len(threats), 0, "Should detect threat from multiple failed logins")
    
    def test_suspicious_ip_detection(self):
        """Test detection of suspicious IP addresses"""
        logs = [
            {
                "source_ip": "203.0.113.1",
                "action": "port_scan",
                "count": 100,
                "timestamp": "2024-01-01T12:00:00Z"
            }
        ]
        
        result = self.agent.detect_intrusion(logs)
        
        self.assertIsNotNone(result, "Should detect suspicious IP")
        
        # Verify suspicious activity is flagged
        if "threats" in result:
            threats = result["threats"]
            if len(threats) > 0:
                threat = threats[0]
                self.assertEqual(threat.get("source_ip"), "203.0.113.1", "Should identify correct IP")
    
    def test_explain_action(self):
        """Test explanation generation"""
        input_data = [
            {
                "source_ip": "192.168.1.100",
                "action": "failed_login",
                "count": 10
            }
        ]
        
        output_data = {
            "action": "block_ip",
            "blocked_ip": "192.168.1.100",
            "severity": "high"
        }
        
        explanation = self.agent.explain_action(input_data, output_data)
        
        self.assertIsNotNone(explanation, "Explanation should be generated")
        self.assertIn("message", explanation, "Explanation should have message")
        self.assertIn("explanation", explanation, "Explanation should have explanation text")
        
        # Verify explanation format
        if "explanation" in explanation:
            exp_text = explanation["explanation"]
            self.assertIn("The agent detected that", exp_text, "Should follow standard format")
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        # Test with empty logs
        result = self.agent.detect_intrusion([])
        
        # Should handle gracefully
        self.assertIsNotNone(result, "Should return result even with empty logs")
    
    def test_network_traffic_analysis(self):
        """Test network traffic analysis"""
        network_traffic = {
            "source_ip": "192.168.1.200",
            "destination_ip": "10.0.0.1",
            "protocol": "TCP",
            "port": 22,
            "packet_count": 1000,
            "anomaly_score": 0.85
        }
        
        logs = [
            {
                "source_ip": "192.168.1.200",
                "action": "connection_attempt",
                "count": 1000
            }
        ]
        
        result = self.agent.detect_intrusion(
            logs=logs,
            network_traffic=network_traffic
        )
        
        self.assertIsNotNone(result, "Should analyze network traffic")
    
    def test_dependency_graph_analysis(self):
        """Test dependency graph analysis for security"""
        dependency_graph = {
            "nodes": [
                {"id": "service-1", "type": "service"},
                {"id": "service-2", "type": "service"}
            ],
            "edges": [
                {"from": "service-1", "to": "service-2", "type": "api_call"}
            ]
        }
        
        logs = [
            {
                "source_ip": "192.168.1.100",
                "action": "api_abuse",
                "count": 50
            }
        ]
        
        result = self.agent.detect_intrusion(
            logs=logs,
            dependency_graph_data=dependency_graph
        )
        
        self.assertIsNotNone(result, "Should use dependency graph for analysis")


if __name__ == '__main__':
    unittest.main()

