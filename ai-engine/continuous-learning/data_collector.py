"""
Data Collector for Continuous Learning
Collects real-world operational data for model training and optimization
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentAction:
    """Represents an agent action with metadata"""
    agent_name: str
    action_type: str
    timestamp: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    success: bool
    execution_time: float
    confidence: float
    explanation: str
    context: Dict[str, Any]


@dataclass
class PerformanceMetric:
    """Represents system performance metrics"""
    timestamp: float
    agent_name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    throughput: float
    error_rate: float
    success_rate: float


@dataclass
class TaskResult:
    """Represents task execution result"""
    task_id: str
    agent_name: str
    task_type: str
    timestamp: float
    status: str  # success, failure, timeout
    execution_time: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str] = None


class DataCollector:
    """Collects operational data for continuous learning"""
    
    def __init__(self, storage_path: str = "data/continuous-learning"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Data buffers
        self.actions_buffer: List[AgentAction] = []
        self.metrics_buffer: List[PerformanceMetric] = []
        self.tasks_buffer: List[TaskResult] = []
        
        # Buffer size before flushing to disk
        self.buffer_size = 100
        
    def collect_action(
        self,
        agent_name: str,
        action_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        success: bool,
        execution_time: float,
        confidence: float,
        explanation: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Collect agent action data"""
        action = AgentAction(
            agent_name=agent_name,
            action_type=action_type,
            timestamp=time.time(),
            input_data=input_data,
            output_data=output_data,
            success=success,
            execution_time=execution_time,
            confidence=confidence,
            explanation=explanation,
            context=context or {}
        )
        
        self.actions_buffer.append(action)
        logger.debug(f"Collected action: {agent_name} - {action_type}")
        
        # Flush if buffer is full
        if len(self.actions_buffer) >= self.buffer_size:
            self._flush_actions()
    
    def collect_metric(
        self,
        agent_name: str,
        cpu_usage: float,
        memory_usage: float,
        response_time: float,
        throughput: float,
        error_rate: float,
        success_rate: float
    ):
        """Collect performance metrics"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            agent_name=agent_name,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            throughput=throughput,
            error_rate=error_rate,
            success_rate=success_rate
        )
        
        self.metrics_buffer.append(metric)
        logger.debug(f"Collected metric: {agent_name}")
        
        # Flush if buffer is full
        if len(self.metrics_buffer) >= self.buffer_size:
            self._flush_metrics()
    
    def collect_task_result(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        status: str,
        execution_time: float,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        error_message: Optional[str] = None
    ):
        """Collect task execution result"""
        task_result = TaskResult(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            timestamp=time.time(),
            status=status,
            execution_time=execution_time,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message
        )
        
        self.tasks_buffer.append(task_result)
        logger.debug(f"Collected task result: {task_id} - {status}")
        
        # Flush if buffer is full
        if len(self.tasks_buffer) >= self.buffer_size:
            self._flush_tasks()
    
    def _flush_actions(self):
        """Flush actions buffer to disk"""
        if not self.actions_buffer:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.storage_path / f"actions_{timestamp}.jsonl"
        
        with open(file_path, 'a') as f:
            for action in self.actions_buffer:
                f.write(json.dumps(asdict(action)) + '\n')
        
        logger.info(f"Flushed {len(self.actions_buffer)} actions to {file_path}")
        self.actions_buffer.clear()
    
    def _flush_metrics(self):
        """Flush metrics buffer to disk"""
        if not self.metrics_buffer:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.storage_path / f"metrics_{timestamp}.jsonl"
        
        with open(file_path, 'a') as f:
            for metric in self.metrics_buffer:
                f.write(json.dumps(asdict(metric)) + '\n')
        
        logger.info(f"Flushed {len(self.metrics_buffer)} metrics to {file_path}")
        self.metrics_buffer.clear()
    
    def _flush_tasks(self):
        """Flush tasks buffer to disk"""
        if not self.tasks_buffer:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.storage_path / f"tasks_{timestamp}.jsonl"
        
        with open(file_path, 'a') as f:
            for task in self.tasks_buffer:
                f.write(json.dumps(asdict(task)) + '\n')
        
        logger.info(f"Flushed {len(self.tasks_buffer)} tasks to {file_path}")
        self.tasks_buffer.clear()
    
    def flush_all(self):
        """Flush all buffers to disk"""
        self._flush_actions()
        self._flush_metrics()
        self._flush_tasks()
    
    def get_recent_actions(self, agent_name: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get recent actions from storage"""
        actions = []
        action_files = sorted(self.storage_path.glob("actions_*.jsonl"), reverse=True)
        
        for file_path in action_files:
            with open(file_path, 'r') as f:
                for line in f:
                    action = json.loads(line)
                    if agent_name is None or action['agent_name'] == agent_name:
                        actions.append(action)
                    if len(actions) >= limit:
                        return actions
        
        return actions
    
    def get_recent_metrics(self, agent_name: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get recent metrics from storage"""
        metrics = []
        metric_files = sorted(self.storage_path.glob("metrics_*.jsonl"), reverse=True)
        
        for file_path in metric_files:
            with open(file_path, 'r') as f:
                for line in f:
                    metric = json.loads(line)
                    if agent_name is None or metric['agent_name'] == agent_name:
                        metrics.append(metric)
                    if len(metrics) >= limit:
                        return metrics
        
        return metrics
    
    def get_recent_tasks(self, agent_name: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get recent task results from storage"""
        tasks = []
        task_files = sorted(self.storage_path.glob("tasks_*.jsonl"), reverse=True)
        
        for file_path in task_files:
            with open(file_path, 'r') as f:
                for line in f:
                    task = json.loads(line)
                    if agent_name is None or task['agent_name'] == agent_name:
                        tasks.append(task)
                    if len(tasks) >= limit:
                        return tasks
        
        return tasks

