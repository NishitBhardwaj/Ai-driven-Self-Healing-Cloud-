"""Basic tests for Coding Agent"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import CodingAgent


def test_agent_import():
    """Test that agent can be imported"""
    agent = CodingAgent()
    assert agent.agent_id == "coding-agent"
    assert agent.name == "Coding/Code-Fixer Agent"
    print("✓ Agent import test passed")


def test_agent_start_stop():
    """Test agent start/stop"""
    agent = CodingAgent()
    assert agent.start() == True
    assert agent.status == "running"
    assert agent.stop() == True
    assert agent.status == "stopped"
    print("✓ Agent start/stop test passed")


def test_agent_methods():
    """Test agent methods exist"""
    agent = CodingAgent()
    assert hasattr(agent, 'debug_code')
    assert hasattr(agent, 'generate_code')
    assert hasattr(agent, 'llm_call')
    assert hasattr(agent, 'explain_action')
    print("✓ Agent methods test passed")


if __name__ == "__main__":
    test_agent_import()
    test_agent_start_stop()
    test_agent_methods()
    print("\nAll tests passed!")

