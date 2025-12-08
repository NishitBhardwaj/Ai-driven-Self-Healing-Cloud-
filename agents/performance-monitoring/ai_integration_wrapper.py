#!/usr/bin/env python3
"""
Python wrapper for Performance Monitoring Agent AI Integration
Can be called from Go via subprocess
"""

import sys
import json
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_integration import MonitoringAIIntegration


def main():
    """Main entry point for Go agent integration"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Initialize integration
    integration = MonitoringAIIntegration()
    
    if command == "feed_metrics_to_models":
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Convert metrics to proper format
        metrics = input_data.get("metrics", {})
        for key, value in metrics.items():
            if isinstance(value, list):
                metrics[key] = np.array(value) if not isinstance(value, np.ndarray) else value
            else:
                metrics[key] = np.array([value])
        
        result = integration.feed_metrics_to_models(
            metrics=metrics,
            dependency_graph_data=input_data.get("dependency_graph_data")
        )
        
        # Convert numpy arrays to lists for JSON
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        result = convert_numpy(result)
        
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()

