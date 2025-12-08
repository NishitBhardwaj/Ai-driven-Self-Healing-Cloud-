"""
Meta-Agent Orchestrator
High-level "brain" controlling all agents
Listens to all events, combines RL + GNN + Transformers + LLM, chooses best agent, coordinates recovery plan
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import logging
from collections import deque
from datetime import datetime

from ..rl.agent import RLAgent
from ..rl.environment import RLEnvironment
from ..gnn.gnn_predictor import GNNPredictor
from ..gnn.graph_builder import DependencyGraph
from ..transformers.forecasting import ScalingForecastEngine
from ..llm_reasoning.reasoning_engine import ReasoningEngine
from ..llm_reasoning.safety_layer import SafetyLayer
from .decision_router import DecisionRouter, AgentType
from .confidence_estimator import ConfidenceEstimator
from .memory import MetaAgentMemory

logger = logging.getLogger(__name__)


class EventListener:
    """Listens to all events from cloud infrastructure"""
    
    def __init__(self):
        self.event_queue = deque(maxlen=1000)
        self.event_handlers = {}
        logger.info("EventListener initialized")
    
    def register_handler(self, event_type: str, handler):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")
    
    def on_event(self, event: Dict[str, Any]):
        """Handle incoming event"""
        event_type = event.get("type", "unknown")
        event["timestamp"] = datetime.now().isoformat()
        
        self.event_queue.append(event)
        
        # Call registered handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        logger.debug(f"Event received: {event_type}")
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent events"""
        events = list(self.event_queue)
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        return events[-limit:]


class MetaAgentOrchestrator:
    """
    Meta-Agent Orchestrator - High-level "brain" controlling all agents
    
    Responsibilities:
    - Listening to all events
    - Combining RL + GNN + Transformers + LLM
    - Choosing best agent to call
    - Coordinating recovery plan
    """
    
    def __init__(
        self,
        rl_agent: Optional[RLAgent] = None,
        gnn_predictor: Optional[GNNPredictor] = None,
        forecast_engine: Optional[ScalingForecastEngine] = None,
        reasoning_engine: Optional[ReasoningEngine] = None,
        safety_layer: Optional[SafetyLayer] = None,
        decision_router: Optional[DecisionRouter] = None,
        confidence_estimator: Optional[ConfidenceEstimator] = None,
        memory: Optional[MetaAgentMemory] = None
    ):
        """
        Initialize meta-agent orchestrator
        
        Args:
            rl_agent: RL agent instance
            gnn_predictor: GNN predictor instance
            forecast_engine: Forecasting engine instance
            reasoning_engine: Reasoning engine instance
            safety_layer: Safety layer instance
            decision_router: Decision router instance
            confidence_estimator: Confidence estimator instance
            memory: Memory system instance
        """
        self.rl_agent = rl_agent
        self.gnn_predictor = gnn_predictor
        self.forecast_engine = forecast_engine
        self.reasoning_engine = reasoning_engine
        self.safety_layer = safety_layer or SafetyLayer()
        self.decision_router = decision_router or DecisionRouter()
        self.confidence_estimator = confidence_estimator or ConfidenceEstimator()
        self.memory = memory or MetaAgentMemory()
        
        # Event listener
        self.event_listener = EventListener()
        self.event_listener.register_handler("failure", self._handle_failure_event)
        self.event_listener.register_handler("anomaly", self._handle_anomaly_event)
        self.event_listener.register_handler("overload", self._handle_overload_event)
        self.event_listener.register_handler("error", self._handle_error_event)
        self.event_listener.register_handler("attack", self._handle_attack_event)
        
        # Agent interfaces (would be connected to actual agents)
        self.agents = {
            "code_agent": None,
            "self_healing_agent": None,
            "scaling_agent": None,
            "monitoring_agent": None,
            "security_agent": None
        }
        
        logger.info("MetaAgentOrchestrator initialized")
    
    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming event and coordinate response
        
        Args:
            event: Event from cloud infrastructure
        
        Returns:
            Orchestrated response
        """
        logger.info(f"Processing event: {event.get('type', 'unknown')}")
        
        # Store event in memory
        self.memory.store_event(event)
        
        # Route to appropriate agent
        routing = self.decision_router.route_event(event)
        target_agent = routing.get("target_agent")
        
        # Gather intelligence from all AI components
        intelligence = self._gather_intelligence(event)
        
        # Choose best agent and action
        decision = self._choose_best_action(event, intelligence, routing)
        
        # Coordinate recovery plan
        recovery_plan = self._coordinate_recovery_plan(decision, intelligence)
        
        # Estimate confidence
        confidence, confidence_details = self.confidence_estimator.estimate_confidence(
            recommendations=decision.get("recommendations", []),
            situation_complexity=self._assess_complexity(event, intelligence),
            risk_score=decision.get("risk_score", 0.5)
        )
        
        # Apply safety checks
        safe_decision = self.safety_layer.apply_safety_checks(decision, event)
        safe_decision["confidence"] = confidence
        safe_decision["confidence_details"] = confidence_details
        
        # Store decision in memory
        decision_id = self.memory.store_decision(safe_decision, event)
        
        # Execute action through target agent
        execution_result = self._execute_through_agent(target_agent, safe_decision)
        
        result = {
            "event": event,
            "routing": routing,
            "decision": safe_decision,
            "recovery_plan": recovery_plan,
            "execution_result": execution_result,
            "decision_id": decision_id
        }
        
        logger.info(f"Event processed: action={safe_decision.get('action', 'unknown')}, agent={target_agent}")
        
        return result
    
    def _gather_intelligence(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather intelligence from all AI components
        
        Args:
            event: Event information
        
        Returns:
            Combined intelligence from RL, GNN, Transformers, LLM
        """
        intelligence = {}
        
        # Get system state from event
        system_state = event.get("system_state", {})
        failure_info = event.get("failure_info")
        dependency_graph = event.get("dependency_graph")
        historical_metrics = event.get("historical_metrics")
        
        # RL Agent intelligence
        if self.rl_agent:
            try:
                state_array = self._state_to_array(system_state)
                action, confidence = self.rl_agent.choose_action(state_array, training=False)
                intelligence["rl"] = {
                    "action": action,
                    "confidence": confidence,
                    "source": "rl_agent"
                }
            except Exception as e:
                logger.error(f"RL agent error: {e}")
        
        # GNN intelligence
        if self.gnn_predictor and dependency_graph:
            try:
                failure_probs = self.gnn_predictor.predict_failure_propagation(
                    dependency_graph,
                    failure_info.get("service_id") if failure_info else None
                )
                intelligence["gnn"] = {
                    "failure_propagation": failure_probs,
                    "source": "gnn"
                }
            except Exception as e:
                logger.error(f"GNN predictor error: {e}")
        
        # Transformers intelligence
        if self.forecast_engine and historical_metrics is not None:
            try:
                forecast = self.forecast_engine.forecast_5min(historical_metrics)
                intelligence["transformers"] = {
                    "forecast": forecast,
                    "source": "transformers"
                }
            except Exception as e:
                logger.error(f"Forecast engine error: {e}")
        
        # LLM intelligence
        if self.reasoning_engine:
            try:
                llm_result = self.reasoning_engine.reason_about_failure(
                    failure_info or {},
                    system_state,
                    available_actions=["restart_pod", "rebuild_deployment", "scale_up", "scale_down"],
                    rl_suggestion=intelligence.get("rl"),
                    gnn_suggestion=intelligence.get("gnn")
                )
                intelligence["llm"] = {
                    **llm_result,
                    "source": "llm_reasoning"
                }
            except Exception as e:
                logger.error(f"Reasoning engine error: {e}")
        
        return intelligence
    
    def _choose_best_action(
        self,
        event: Dict[str, Any],
        intelligence: Dict[str, Any],
        routing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Choose best action by combining all intelligence
        
        Args:
            event: Event information
            intelligence: Combined intelligence
            routing: Routing information
        
        Returns:
            Best action decision
        """
        recommendations = []
        
        # Collect recommendations from all sources
        if "rl" in intelligence:
            recommendations.append(intelligence["rl"])
        
        if "llm" in intelligence:
            recommendations.append({
                "action": intelligence["llm"].get("action", "no_action"),
                "confidence": intelligence["llm"].get("confidence", 0.5),
                "source": "llm_reasoning",
                "reasoning": intelligence["llm"].get("reasoning", "")
            })
        
        if "gnn" in intelligence:
            # Convert GNN failure probabilities to recommendation
            failure_probs = intelligence["gnn"].get("failure_propagation", {})
            if failure_probs:
                max_risk_node = max(failure_probs.items(), key=lambda x: x[1])
                recommendations.append({
                    "action": "trigger_heal",
                    "confidence": max_risk_node[1],
                    "source": "gnn",
                    "reasoning": f"High failure risk detected: {max_risk_node[0]}"
                })
        
        if "transformers" in intelligence:
            forecast = intelligence["transformers"].get("forecast", {})
            if forecast.get("cpu_forecast"):
                avg_cpu = np.mean(forecast["cpu_forecast"])
                if avg_cpu > 80:
                    recommendations.append({
                        "action": "scale_up",
                        "confidence": min(1.0, avg_cpu / 100.0),
                        "source": "transformers",
                        "reasoning": f"CPU forecasted to be high: {avg_cpu:.1f}%"
                    })
        
        # Combine recommendations
        if not recommendations:
            return {
                "action": "do_nothing",
                "confidence": 0.0,
                "recommendations": [],
                "risk_score": 0.5
            }
        
        # Select best recommendation
        best_rec = max(recommendations, key=lambda r: r.get("confidence", 0.0))
        
        return {
            "action": best_rec.get("action", "no_action"),
            "confidence": best_rec.get("confidence", 0.5),
            "recommendations": recommendations,
            "risk_score": self._calculate_risk_score(event, intelligence),
            "target_agent": routing.get("target_agent")
        }
    
    def _coordinate_recovery_plan(
        self,
        decision: Dict[str, Any],
        intelligence: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate multi-step recovery plan
        
        Args:
            decision: Decision made
            intelligence: Intelligence gathered
        
        Returns:
            Recovery plan
        """
        plan = {
            "steps": [],
            "estimated_duration": 0,
            "rollback_plan": None
        }
        
        action = decision.get("action", "no_action")
        
        # Generate recovery steps based on action
        if action == "restart_pod":
            plan["steps"] = [
                {"step": 1, "action": "identify_failed_pod", "duration": 5},
                {"step": 2, "action": "restart_pod", "duration": 30},
                {"step": 3, "action": "verify_health", "duration": 60}
            ]
            plan["estimated_duration"] = 95  # seconds
        
        elif action == "scale_up":
            plan["steps"] = [
                {"step": 1, "action": "calculate_target_replicas", "duration": 5},
                {"step": 2, "action": "scale_deployment", "duration": 60},
                {"step": 3, "action": "verify_scaling", "duration": 120}
            ]
            plan["estimated_duration"] = 185  # seconds
        
        elif action == "rebuild_deployment":
            plan["steps"] = [
                {"step": 1, "action": "backup_current_state", "duration": 30},
                {"step": 2, "action": "rebuild_deployment", "duration": 180},
                {"step": 3, "action": "verify_deployment", "duration": 120},
                {"step": 4, "action": "rollback_if_needed", "duration": 60}
            ]
            plan["estimated_duration"] = 390  # seconds
            plan["rollback_plan"] = {"action": "restore_backup", "duration": 120}
        
        else:
            plan["steps"] = [
                {"step": 1, "action": "monitor_situation", "duration": 60}
            ]
            plan["estimated_duration"] = 60
        
        return plan
    
    def _assess_complexity(self, event: Dict[str, Any], intelligence: Dict[str, Any]) -> float:
        """Assess situation complexity [0, 1]"""
        complexity = 0.0
        
        # More components involved = higher complexity
        if len(intelligence) > 2:
            complexity += 0.3
        
        # Multiple failures = higher complexity
        if event.get("failure_count", 0) > 1:
            complexity += 0.3
        
        # High risk = higher complexity
        if intelligence.get("gnn", {}).get("failure_propagation", {}):
            max_risk = max(intelligence["gnn"]["failure_propagation"].values(), default=0)
            complexity += max_risk * 0.4
        
        return min(1.0, complexity)
    
    def _calculate_risk_score(self, event: Dict[str, Any], intelligence: Dict[str, Any]) -> float:
        """Calculate overall risk score [0, 1]"""
        risk = 0.0
        
        # Event severity
        severity = event.get("severity", "medium")
        severity_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
        risk += severity_map.get(severity, 0.5) * 0.4
        
        # Failure propagation risk
        if "gnn" in intelligence:
            failure_probs = intelligence["gnn"].get("failure_propagation", {})
            if failure_probs:
                avg_risk = np.mean(list(failure_probs.values()))
                risk += avg_risk * 0.3
        
        # Forecast risk
        if "transformers" in intelligence:
            forecast = intelligence["transformers"].get("forecast", {})
            if forecast.get("error_burst"):
                if np.any(forecast["error_burst"] > 0.5):
                    risk += 0.3
        
        return min(1.0, risk)
    
    def _execute_through_agent(self, agent_type: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute decision through target agent
        
        Args:
            agent_type: Type of agent to use
            decision: Decision to execute
        
        Returns:
            Execution result
        """
        # In practice, this would call the actual agent
        # For now, simulate execution
        logger.info(f"Executing through {agent_type}: {decision.get('action', 'unknown')}")
        
        return {
            "agent": agent_type,
            "action": decision.get("action"),
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }
    
    def _state_to_array(self, state: Dict) -> np.ndarray:
        """Convert state dictionary to array"""
        return np.array([
            state.get("cpu_usage", 0.0),
            state.get("memory_usage", 0.0),
            state.get("error_rate", 0.0),
            state.get("network_latency", 0.0),
            float(state.get("replicas", 0)),
            state.get("dependency_health", 1.0)
        ], dtype=np.float32)
    
    def _handle_failure_event(self, event: Dict):
        """Handle failure event"""
        logger.debug(f"Handling failure event: {event.get('type', 'unknown')}")
    
    def _handle_anomaly_event(self, event: Dict):
        """Handle anomaly event"""
        logger.debug(f"Handling anomaly event: {event.get('type', 'unknown')}")
    
    def _handle_overload_event(self, event: Dict):
        """Handle overload event"""
        logger.debug(f"Handling overload event: {event.get('type', 'unknown')}")
    
    def _handle_error_event(self, event: Dict):
        """Handle error event"""
        logger.debug(f"Handling error event: {event.get('type', 'unknown')}")
    
    def _handle_attack_event(self, event: Dict):
        """Handle attack event"""
        logger.debug(f"Handling attack event: {event.get('type', 'unknown')}")
