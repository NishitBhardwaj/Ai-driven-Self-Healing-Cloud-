#!/usr/bin/env python3
"""
Python wrapper for Self-Healing Agent AI Integration
Can be called from Go via subprocess
"""

import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_integration import SelfHealingAIIntegration


def main():
    """Main entry point for Go agent integration"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Initialize integration
    integration = SelfHealingAIIntegration()
    
    if command == "decide_healing_action":
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        result = integration.decide_healing_action(
            failure_info=input_data.get("failure_info", {}),
            system_state=input_data.get("system_state", {}),
            dependency_graph_data=input_data.get("dependency_graph_data")
        )
        
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()

