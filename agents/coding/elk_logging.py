"""
ELK Stack logging integration for Coding Agent
"""

import json
import socket
import time
import logging
from typing import Dict, Any, Optional


class ELKLogger:
    """Logger for sending logs to ELK Stack via Logstash"""
    
    def __init__(self, logstash_host: str = "localhost", logstash_port: int = 5000):
        self.logstash_host = logstash_host
        self.logstash_port = logstash_port
        self.agent_id = "coding-agent"
        self.agent_name = "Coding/Code-Fixer Agent"
        self.logger = logging.getLogger(self.agent_id)
    
    def _send_to_logstash(self, log_entry: Dict[str, Any]) -> bool:
        """Send log entry to Logstash via TCP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.logstash_host, self.logstash_port))
            sock.sendall(json.dumps(log_entry).encode() + b'\n')
            sock.close()
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send log to Logstash: {e}")
            return False
    
    def log_action_trigger(self, action: str, input_data: Any, output_data: Any) -> None:
        """Log when an action is triggered"""
        log_entry = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "action": action,
            "action_taken": action,
            "log_type": "action",
            "level": "info",
            "message": f"{self.agent_name} triggered action: {action}",
            "input": str(input_data) if not isinstance(input_data, (dict, list)) else input_data,
            "output": str(output_data) if not isinstance(output_data, (dict, list)) else output_data,
        }
        
        self._send_to_logstash(log_entry)
        self.logger.info(f"Action triggered: {action}")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error"""
        log_entry = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "log_type": "error",
            "level": "error",
            "message": f"{self.agent_name} encountered error: {str(error)}",
        }
        
        if context:
            log_entry.update(context)
        
        self._send_to_logstash(log_entry)
        self.logger.error(f"Error occurred: {error}", exc_info=True)
    
    def log_explanation(self, explanation: Dict[str, Any]) -> None:
        """Log an explanation"""
        log_entry = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "explanation": explanation.get("explanation", ""),
            "reasoning": explanation.get("reason", ""),
            "confidence": explanation.get("confidence", 0.0),
            "confidence_level": explanation.get("confidence", 0.0),
            "log_type": "explanation",
            "level": "info",
            "message": f"{self.agent_name} generated explanation",
            "has_explanation": True,
        }
        
        self._send_to_logstash(log_entry)
        self.logger.info("Explanation logged")
    
    def log_confidence(self, confidence: float, mode: str, reasoning: str) -> None:
        """Log confidence level"""
        log_entry = {
            "@timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "confidence": confidence,
            "confidence_level": confidence,
            "mode": mode,
            "decision_mode": mode,
            "reasoning": reasoning,
            "log_type": "confidence",
            "level": "info",
            "message": f"{self.agent_name} decision confidence: {confidence*100:.0f}% ({mode} mode)",
        }
        
        self._send_to_logstash(log_entry)
        self.logger.info(f"Confidence logged: {confidence*100:.0f}%")


# Global ELK logger instance
_elk_logger: Optional[ELKLogger] = None


def get_elk_logger() -> ELKLogger:
    """Get or create global ELK logger"""
    global _elk_logger
    if _elk_logger is None:
        import os
        host = os.getenv("LOGSTASH_HOST", "localhost")
        port = int(os.getenv("LOGSTASH_PORT", "5000"))
        _elk_logger = ELKLogger(host, port)
    return _elk_logger

