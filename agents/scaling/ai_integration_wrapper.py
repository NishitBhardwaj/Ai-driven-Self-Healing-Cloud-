#!/usr/bin/env python3
"""
Python wrapper for Scaling Agent AI Integration
Can be called from Go via subprocess
"""

import sys
import json
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_integration import ScalingAIIntegration


def main():
    """Main entry point for Go agent integration"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing command"}))
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Initialize integration
    integration = ScalingAIIntegration()
    
    if command == "get_scaling_recommendation":
        # Read input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Convert metrics to numpy arrays
        historical_metrics = {}
        for key, value in input_data.get("historical_metrics", {}).items():
            if isinstance(value, list):
                historical_metrics[key] = np.array(value)
            else:
                historical_metrics[key] = np.array([value])
        
        result = integration.get_scaling_recommendation(
            historical_metrics=historical_metrics,
            current_replicas=input_data.get("current_replicas", 2),
            cpu_threshold=input_data.get("cpu_threshold", 80.0),
            memory_threshold=input_data.get("memory_threshold", 80.0),
            latency_threshold=input_data.get("latency_threshold", 500.0)
        )
        
        # Convert numpy arrays to lists for JSON
        if "forecast" in result:
            for key, value in result["forecast"].items():
                if isinstance(value, np.ndarray):
                    result["forecast"][key] = value.tolist()
        
        print(json.dumps(result))
    
    elif command == "forecast_workload":
        input_data = json.loads(sys.stdin.read())
        
        historical_metrics = {}
        for key, value in input_data.get("historical_metrics", {}).items():
            if isinstance(value, list):
                historical_metrics[key] = np.array(value)
            else:
                historical_metrics[key] = np.array([value])
        
        result = integration.forecast_workload(
            historical_metrics=historical_metrics,
            forecast_horizon=input_data.get("forecast_horizon", 5)
        )
        
        # Convert numpy arrays to lists
        for key, value in result.items():
            if isinstance(value, np.ndarray):
                result[key] = value.tolist()
        
        print(json.dumps(result))
    
    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()

