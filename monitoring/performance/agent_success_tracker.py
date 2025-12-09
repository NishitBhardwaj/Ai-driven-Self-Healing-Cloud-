"""
Agent Success Tracking
Tracks agent performance over time: success rates, recovery times, resource consumption
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    agent_name: str
    task_type: str
    timestamp: float
    success: bool
    execution_time: float
    error_message: Optional[str] = None


@dataclass
class FailureRecovery:
    """Failure recovery record"""
    failure_id: str
    agent_name: str
    failure_type: str
    failure_timestamp: float
    recovery_timestamp: float
    recovery_time: float
    recovery_action: str
    success: bool


@dataclass
class AgentPerformance:
    """Agent performance summary"""
    agent_name: str
    timestamp: float
    task_success_rate: float
    average_recovery_time: float
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_failures: int
    recovered_failures: int
    average_cpu_usage: float
    average_memory_usage: float
    average_latency_p95: float


class AgentSuccessTracker:
    """Tracks agent success rates, recovery times, and resource consumption"""
    
    def __init__(self):
        # Task tracking
        self.tasks: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Failure recovery tracking
        self.failures: Dict[str, List[FailureRecovery]] = defaultdict(list)
        self.recoveries: Dict[str, List[FailureRecovery]] = defaultdict(list)
        
        # Resource consumption tracking
        self.resource_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Performance summaries
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Storage
        self.storage_path = Path("data/monitoring/agent-success")
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def record_task(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        success: bool,
        execution_time: float,
        error_message: Optional[str] = None
    ):
        """Record task execution result"""
        task = TaskResult(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            timestamp=time.time(),
            success=success,
            execution_time=execution_time,
            error_message=error_message
        )
        
        self.tasks[agent_name].append(task)
        logger.debug(f"Recorded task {task_id} for {agent_name}: Success={success}")
    
    def record_failure(
        self,
        failure_id: str,
        agent_name: str,
        failure_type: str
    ):
        """Record a failure occurrence"""
        failure = FailureRecovery(
            failure_id=failure_id,
            agent_name=agent_name,
            failure_type=failure_type,
            failure_timestamp=time.time(),
            recovery_timestamp=0.0,
            recovery_time=0.0,
            recovery_action="",
            success=False
        )
        
        self.failures[agent_name].append(failure)
        logger.info(f"Recorded failure {failure_id} for {agent_name}: {failure_type}")
    
    def record_recovery(
        self,
        failure_id: str,
        agent_name: str,
        recovery_action: str,
        success: bool
    ):
        """Record failure recovery"""
        # Find the failure
        failure = None
        for f in self.failures[agent_name]:
            if f.failure_id == failure_id:
                failure = f
                break
        
        if not failure:
            logger.warning(f"Failure {failure_id} not found for {agent_name}")
            return
        
        # Update recovery information
        recovery_timestamp = time.time()
        recovery_time = recovery_timestamp - failure.failure_timestamp
        
        recovery = FailureRecovery(
            failure_id=failure_id,
            agent_name=agent_name,
            failure_type=failure.failure_type,
            failure_timestamp=failure.failure_timestamp,
            recovery_timestamp=recovery_timestamp,
            recovery_time=recovery_time,
            recovery_action=recovery_action,
            success=success
        )
        
        self.recoveries[agent_name].append(recovery)
        
        # Remove from failures list
        self.failures[agent_name] = [f for f in self.failures[agent_name] if f.failure_id != failure_id]
        
        logger.info(
            f"Recorded recovery for {failure_id} ({agent_name}): "
            f"Time={recovery_time:.2f}s, Success={success}"
        )
    
    def record_resource_consumption(
        self,
        agent_name: str,
        cpu_usage: float,
        memory_usage: float,
        disk_usage: float,
        network_io: float
    ):
        """Record resource consumption"""
        resource_data = {
            "timestamp": time.time(),
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "network_io": network_io
        }
        
        self.resource_history[agent_name].append(resource_data)
    
    def calculate_performance(self, agent_name: str) -> AgentPerformance:
        """Calculate agent performance metrics"""
        # Task success rate
        tasks = list(self.tasks[agent_name])
        if not tasks:
            return AgentPerformance(
                agent_name=agent_name,
                timestamp=time.time(),
                task_success_rate=0.0,
                average_recovery_time=0.0,
                total_tasks=0,
                successful_tasks=0,
                failed_tasks=0,
                total_failures=0,
                recovered_failures=0,
                average_cpu_usage=0.0,
                average_memory_usage=0.0,
                average_latency_p95=0.0
            )
        
        successful_tasks = sum(1 for t in tasks if t.success)
        failed_tasks = len(tasks) - successful_tasks
        task_success_rate = successful_tasks / len(tasks) if tasks else 0.0
        
        # Failure recovery time
        recoveries = self.recoveries[agent_name]
        if recoveries:
            successful_recoveries = [r for r in recoveries if r.success]
            average_recovery_time = np.mean([r.recovery_time for r in successful_recoveries]) if successful_recoveries else 0.0
        else:
            average_recovery_time = 0.0
        
        # Resource consumption
        resources = list(self.resource_history[agent_name])
        if resources:
            average_cpu = np.mean([r["cpu_usage"] for r in resources])
            average_memory = np.mean([r["memory_usage"] for r in resources])
        else:
            average_cpu = 0.0
            average_memory = 0.0
        
        # Latency (from task execution times)
        execution_times = [t.execution_time for t in tasks if t.success]
        if execution_times:
            latency_p95 = np.percentile(execution_times, 95)
        else:
            latency_p95 = 0.0
        
        performance = AgentPerformance(
            agent_name=agent_name,
            timestamp=time.time(),
            task_success_rate=task_success_rate,
            average_recovery_time=average_recovery_time,
            total_tasks=len(tasks),
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            total_failures=len(self.failures[agent_name]) + len(self.recoveries[agent_name]),
            recovered_failures=len([r for r in self.recoveries[agent_name] if r.success]),
            average_cpu_usage=average_cpu,
            average_memory_usage=average_memory,
            average_latency_p95=latency_p95
        )
        
        self.performance_history[agent_name].append(performance)
        return performance
    
    def get_performance_summary(self, agent_name: Optional[str] = None) -> Dict:
        """Get performance summary for agent(s)"""
        if agent_name:
            performance = self.calculate_performance(agent_name)
            return asdict(performance)
        else:
            summary = {}
            for agent in self.tasks.keys():
                summary[agent] = asdict(self.calculate_performance(agent))
            return summary
    
    def get_success_rate_trend(self, agent_name: str, window_hours: int = 24) -> List[Tuple[float, float]]:
        """Get success rate trend over time"""
        tasks = list(self.tasks[agent_name])
        if not tasks:
            return []
        
        # Group tasks by time window
        current_time = time.time()
        window_seconds = window_hours * 3600
        
        # Calculate success rate for each hour
        trend = []
        for hour in range(window_hours):
            window_start = current_time - (window_hours - hour) * 3600
            window_end = window_start + 3600
            
            window_tasks = [t for t in tasks if window_start <= t.timestamp <= window_end]
            if window_tasks:
                success_rate = sum(1 for t in window_tasks if t.success) / len(window_tasks)
                trend.append((window_start, success_rate))
        
        return trend
    
    def get_recovery_time_trend(self, agent_name: str, window_hours: int = 24) -> List[Tuple[float, float]]:
        """Get recovery time trend over time"""
        recoveries = self.recoveries[agent_name]
        if not recoveries:
            return []
        
        # Group recoveries by time window
        current_time = time.time()
        
        trend = []
        for hour in range(window_hours):
            window_start = current_time - (window_hours - hour) * 3600
            window_end = window_start + 3600
            
            window_recoveries = [
                r for r in recoveries
                if window_start <= r.recovery_timestamp <= window_end and r.success
            ]
            if window_recoveries:
                avg_recovery_time = np.mean([r.recovery_time for r in window_recoveries])
                trend.append((window_start, avg_recovery_time))
        
        return trend
    
    def save_performance_data(self):
        """Save performance data to disk"""
        timestamp = int(time.time())
        
        # Save performance summaries
        for agent_name in self.performance_history.keys():
            performance_file = self.storage_path / f"{agent_name}_performance_{timestamp}.json"
            performance_data = [asdict(p) for p in list(self.performance_history[agent_name])[-1000:]]
            
            with open(performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2)
            
            logger.info(f"Saved {len(performance_data)} performance records for {agent_name}")

