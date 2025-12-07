"""Basic tests for Optimization Agent"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import OptimizationAgent


def test_agent_import():
    """Test that agent can be imported"""
    agent = OptimizationAgent()
    assert agent.agent_id == "optimization-agent"
    assert agent.name == "Optimization Agent"
    print("✓ Agent import test passed")


def test_agent_start_stop():
    """Test agent start/stop"""
    agent = OptimizationAgent()
    assert agent.start() == True
    assert agent.status == "running"
    assert agent.stop() == True
    assert agent.status == "stopped"
    print("✓ Agent start/stop test passed")


def test_agent_methods():
    """Test agent methods exist"""
    agent = OptimizationAgent()
    assert hasattr(agent, 'optimize_cost')
    assert hasattr(agent, 'recommend_architecture')
    assert hasattr(agent, 'llm_call')
    assert hasattr(agent, 'explain_action')
    print("✓ Agent methods test passed")


if __name__ == "__main__":
    test_agent_import()
    test_agent_start_stop()
    test_agent_methods()
    print("\nAll tests passed!")

