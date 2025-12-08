"""
Self-Healing Test Lambda Function

This Lambda function is designed to simulate failures and trigger
the Self-Healing Agent for testing purposes.

It randomly throws exceptions to simulate various failure scenarios
that the Self-Healing Agent should detect and remediate.
"""

import json
import random
import time
import os
from datetime import datetime

# Failure simulation parameters
FAILURE_PROBABILITY = float(os.environ.get('FAILURE_PROBABILITY', '0.3'))  # 30% chance of failure
FAILURE_TYPES = [
    'timeout',
    'memory_error',
    'connection_error',
    'validation_error',
    'resource_not_found',
    'permission_denied'
]


def lambda_handler(event, context):
    """
    Lambda handler that simulates various failure scenarios.
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        dict: Response with status and metadata
    """
    
    # Log the invocation
    print(f"[{datetime.now().isoformat()}] Lambda invoked with event: {json.dumps(event)}")
    
    # Simulate processing time
    processing_time = random.uniform(0.1, 2.0)
    time.sleep(processing_time)
    
    # Random failure simulation
    if random.random() < FAILURE_PROBABILITY:
        failure_type = random.choice(FAILURE_TYPES)
        error_message = f"Simulated {failure_type} failure for testing self-healing agent"
        
        print(f"[{datetime.now().isoformat()}] SIMULATED FAILURE: {failure_type}")
        print(f"[{datetime.now().isoformat()}] Error: {error_message}")
        
        # Raise different exception types based on failure type
        if failure_type == 'timeout':
            # Simulate timeout by sleeping longer than timeout
            time.sleep(35)  # Assuming 30s timeout
            raise TimeoutError(error_message)
            
        elif failure_type == 'memory_error':
            # Simulate memory error
            raise MemoryError(error_message)
            
        elif failure_type == 'connection_error':
            # Simulate connection error
            raise ConnectionError(error_message)
            
        elif failure_type == 'validation_error':
            # Simulate validation error
            raise ValueError(error_message)
            
        elif failure_type == 'resource_not_found':
            # Simulate resource not found
            raise FileNotFoundError(error_message)
            
        elif failure_type == 'permission_denied':
            # Simulate permission error
            raise PermissionError(error_message)
    
    # Successful execution
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Lambda executed successfully',
            'timestamp': datetime.now().isoformat(),
            'processing_time': f"{processing_time:.2f}s",
            'event': event,
            'context': {
                'function_name': context.function_name if context else 'N/A',
                'request_id': context.aws_request_id if context else 'N/A',
                'memory_limit': context.memory_limit_in_mb if context else 'N/A'
            }
        })
    }
    
    print(f"[{datetime.now().isoformat()}] Lambda executed successfully")
    return response


def simulate_health_check():
    """
    Simulate a health check endpoint.
    Can be used to test agent monitoring capabilities.
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': '100%'
    }


def simulate_metrics_collection():
    """
    Simulate metrics collection for CloudWatch.
    """
    return {
        'cpu_usage': random.uniform(10, 90),
        'memory_usage': random.uniform(20, 80),
        'request_count': random.randint(100, 1000),
        'error_rate': random.uniform(0, 5),
        'latency': random.uniform(50, 500)
    }

