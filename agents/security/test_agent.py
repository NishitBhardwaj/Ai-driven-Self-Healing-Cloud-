"""Basic tests for Security Agent"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import SecurityAgent


def test_agent_import():
    """Test that agent can be imported"""
    agent = SecurityAgent()
    assert agent.agent_id == "security-agent"
    assert agent.name == "Security Agent"
    print("✓ Agent import test passed")


def test_agent_start_stop():
    """Test agent start/stop"""
    agent = SecurityAgent()
    assert agent.start() == True
    assert agent.status == "running"
    assert agent.stop() == True
    assert agent.status == "stopped"
    print("✓ Agent start/stop test passed")


def test_agent_methods():
    """Test agent methods exist"""
    agent = SecurityAgent()
    assert hasattr(agent, 'detect_intrusion')
    assert hasattr(agent, 'validate_policy')
    assert hasattr(agent, 'llm_call')
    assert hasattr(agent, 'explain_action')
    print("✓ Agent methods test passed")


if __name__ == "__main__":
    test_agent_import()
    test_agent_start_stop()
    test_agent_methods()
    print("\nAll tests passed!")

