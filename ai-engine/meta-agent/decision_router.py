"""
Decision Router
Maps events to appropriate agents:
- error → Code Agent
- crash → Self-Healing Agent
- overload → Scaling Agent
- anomaly → Monitoring Agent
- attack → Security Agent
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events"""
    ERROR = "error"
    CRASH = "crash"
    OVERLOAD = "overload"
    ANOMALY = "anomaly"
    ATTACK = "attack"
    UNKNOWN = "unknown"


class AgentType(Enum):
    """Types of agents"""
    CODE_AGENT = "code_agent"
    SELF_HEALING_AGENT = "self_healing_agent"
    SCALING_AGENT = "scaling_agent"
    MONITORING_AGENT = "monitoring_agent"
    SECURITY_AGENT = "security_agent"
    UNKNOWN = "unknown"


class DecisionRouter:
    """
    Routes events to appropriate agents
    
    Mapping:
    - error → Code Agent
    - crash → Self-Healing Agent
    - overload → Scaling Agent
    - anomaly → Monitoring Agent
    - attack → Security Agent
    """
    
    def __init__(self):
        self.routing_map = self._initialize_routing_map()
        logger.info("DecisionRouter initialized")
    
    def _initialize_routing_map(self) -> Dict[EventType, AgentType]:
        """Initialize event to agent mapping"""
        return {
            EventType.ERROR: AgentType.CODE_AGENT,
            EventType.CRASH: AgentType.SELF_HEALING_AGENT,
            EventType.OVERLOAD: AgentType.SCALING_AGENT,
            EventType.ANOMALY: AgentType.MONITORING_AGENT,
            EventType.ATTACK: AgentType.SECURITY_AGENT
        }
    
    def classify_event(self, event: Dict[str, Any]) -> EventType:
        """
        Classify event type
        
        Args:
            event: Event information
        
        Returns:
            Event type
        """
        event_type_str = event.get("type", "").lower()
        
        if "error" in event_type_str or "code_error" in event_type_str:
            return EventType.ERROR
        elif "crash" in event_type_str or "pod_crash" in event_type_str or "failure" in event_type_str:
            return EventType.CRASH
        elif "overload" in event_type_str or "high_load" in event_type_str or "resource_exhaustion" in event_type_str:
            return EventType.OVERLOAD
        elif "anomaly" in event_type_str or "unusual" in event_type_str:
            return EventType.ANOMALY
        elif "attack" in event_type_str or "security" in event_type_str or "breach" in event_type_str:
            return EventType.ATTACK
        else:
            return EventType.UNKNOWN
    
    def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route event to appropriate agent
        
        Args:
            event: Event information
        
        Returns:
            Routing information
        """
        event_type = self.classify_event(event)
        
        if event_type == EventType.UNKNOWN:
            # Default to self-healing agent for unknown events
            target_agent = AgentType.SELF_HEALING_AGENT
            logger.warning(f"Unknown event type, routing to {target_agent.value}")
        else:
            target_agent = self.routing_map.get(event_type, AgentType.SELF_HEALING_AGENT)
        
        routing = {
            "event_type": event_type.value,
            "target_agent": target_agent.value,
            "routing_confidence": 1.0 if event_type != EventType.UNKNOWN else 0.5,
            "reasoning": f"Event type '{event_type.value}' routed to {target_agent.value}"
        }
        
        logger.info(f"Event routed: {event_type.value} → {target_agent.value}")
        
        return routing
    
    def get_agent_for_event(self, event: Dict[str, Any]) -> str:
        """
        Get agent name for event
        
        Args:
            event: Event information
        
        Returns:
            Agent name
        """
        routing = self.route_event(event)
        return routing["target_agent"]
    
    def get_supporting_agents(self, event: Dict[str, Any]) -> List[str]:
        """
        Get supporting agents that should also be notified
        
        Args:
            event: Event information
        
        Returns:
            List of supporting agent names
        """
        event_type = self.classify_event(event)
        primary_agent = self.routing_map.get(event_type)
        
        supporting = []
        
        # All events should notify monitoring agent
        if primary_agent != AgentType.MONITORING_AGENT:
            supporting.append(AgentType.MONITORING_AGENT.value)
        
        # Critical events should notify security agent
        if event.get("severity") in ["high", "critical"]:
            if primary_agent != AgentType.SECURITY_AGENT:
                supporting.append(AgentType.SECURITY_AGENT.value)
        
        # Crashes might need scaling agent if resource-related
        if event_type == EventType.CRASH:
            if "resource" in str(event).lower():
                supporting.append(AgentType.SCALING_AGENT.value)
        
        return supporting


class AdaptiveRouter(DecisionRouter):
    """
    Adaptive router that learns optimal routing based on outcomes
    """
    
    def __init__(self):
        super().__init__()
        self.routing_history = []
        self.agent_performance = {}  # Track agent performance per event type
    
    def update_routing_performance(
        self,
        event_type: EventType,
        agent: AgentType,
        success: bool
    ):
        """
        Update routing performance
        
        Args:
            event_type: Type of event
            agent: Agent used
            success: Whether routing was successful
        """
        key = (event_type, agent)
        if key not in self.agent_performance:
            self.agent_performance[key] = {
                "successes": 0,
                "failures": 0,
                "count": 0
            }
        
        perf = self.agent_performance[key]
        perf["count"] += 1
        if success:
            perf["successes"] += 1
        else:
            perf["failures"] += 1
        
        logger.debug(f"Updated routing performance: {event_type.value} → {agent.value}: success={success}")
    
    def route_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route event with adaptive learning
        
        Args:
            event: Event information
        
        Returns:
            Routing information
        """
        event_type = self.classify_event(event)
        
        # Get default routing
        default_agent = self.routing_map.get(event_type, AgentType.SELF_HEALING_AGENT)
        
        # Check if we have performance data for this event type
        best_agent = default_agent
        best_score = 0.0
        
        for (et, agent), perf in self.agent_performance.items():
            if et == event_type and perf["count"] > 0:
                success_rate = perf["successes"] / perf["count"]
                if success_rate > best_score:
                    best_score = success_rate
                    best_agent = agent
        
        # Use best agent if significantly better, otherwise use default
        if best_score > 0.7 and best_agent != default_agent:
            target_agent = best_agent
            routing_confidence = best_score
        else:
            target_agent = default_agent
            routing_confidence = 1.0 if event_type != EventType.UNKNOWN else 0.5
        
        routing = {
            "event_type": event_type.value,
            "target_agent": target_agent.value,
            "routing_confidence": routing_confidence,
            "reasoning": f"Event type '{event_type.value}' routed to {target_agent.value} (adaptive)",
            "adaptive": True
        }
        
        logger.info(f"Event routed (adaptive): {event_type.value} → {target_agent.value}")
        
        return routing
