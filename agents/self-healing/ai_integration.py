"""
AI Engine Integration for Self-Healing Agent
Uses RL, GNN, LLM reasoning
"""

import sys
import os
import numpy as np
from typing import Dict, List, Optional, Any
import logging

# Add AI engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_engine.rl.agent import RLAgent
from ai_engine.gnn.gnn_predictor import GNNPredictor
from ai_engine.gnn.graph_builder import GraphBuilder, DependencyGraph
from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine
from ai_engine.llm_reasoning.safety_layer import SafetyLayer

logger = logging.getLogger(__name__)


class SelfHealingAIIntegration:
    """
    AI Engine Integration for Self-Healing Agent
    
    Uses:
    - RL Agent for action selection
    - GNN for dependency analysis
    - LLM reasoning for decision-making
    """
    
    def __init__(
        self,
        rl_checkpoint: Optional[str] = None,
        gnn_checkpoint: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize AI integration
        
        Args:
            rl_checkpoint: Path to trained RL agent checkpoint
            gnn_checkpoint: Path to trained GNN checkpoint
            openrouter_api_key: OpenRouter API key
            gemini_api_key: Gemini API key
        """
        # Initialize RL Agent
        self.rl_agent = RLAgent(state_dim=6, action_dim=7)
        if rl_checkpoint and os.path.exists(rl_checkpoint):
            self.rl_agent.load_checkpoint(rl_checkpoint)
        self.rl_agent.eval()
        
        # Initialize GNN Predictor
        self.gnn_predictor = GNNPredictor()
        if gnn_checkpoint and os.path.exists(gnn_checkpoint):
            self.gnn_predictor.load_models(gnn_checkpoint)
        
        # Initialize LLM Reasoning Engine
        self.reasoning_engine = ReasoningEngine(
            openrouter_api_key=openrouter_api_key,
            gemini_api_key=gemini_api_key,
            use_openrouter=True,
            use_gemini=True,
            use_cot=True
        )
        
        # Initialize Safety Layer
        self.safety_layer = SafetyLayer()
        
        logger.info("Self-Healing AI Integration initialized")
    
    def decide_healing_action(
        self,
        failure_info: Dict[str, Any],
        system_state: Dict[str, Any],
        dependency_graph_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Decide healing action using RL, GNN, and LLM
        
        Args:
            failure_info: Failure information
            system_state: Current system state
            dependency_graph_data: Dependency graph data (Kubernetes + LocalStack)
        
        Returns:
            Healing decision with action, confidence, and reasoning
        """
        # Step 1: Build dependency graph if provided
        dependency_graph = None
        gnn_suggestion = None
        
        if dependency_graph_data:
            try:
                dependency_graph = GraphBuilder.build_combined(
                    kubernetes_resources=dependency_graph_data.get("kubernetes", {}),
                    localstack_resources=dependency_graph_data.get("localstack", {})
                )
                
                # Get GNN failure propagation prediction
                failed_service = failure_info.get("service_id")
                failure_probs = self.gnn_predictor.predict_failure_propagation(
                    dependency_graph,
                    failed_service
                )
                
                # Get GNN recommendation
                gnn_suggestion = self.gnn_predictor.combine_recommendations(
                    graph=dependency_graph,
                    gnn_failure_probs=failure_probs,
                    system_state=system_state
                )
            except Exception as e:
                logger.error(f"GNN analysis failed: {e}")
        
        # Step 2: Get RL recommendation
        rl_suggestion = None
        try:
            state_array = self._state_to_array(system_state)
            action, confidence = self.rl_agent.choose_action(state_array, training=False)
            
            action_map = {
                0: "scale_up",
                1: "scale_down",
                2: "restart_pod",
                3: "rebuild_deployment",
                4: "trigger_heal",
                5: "trigger_code_fix",
                6: "do_nothing"
            }
            
            rl_suggestion = {
                "action": action_map.get(action, "do_nothing"),
                "confidence": float(confidence),
                "source": "rl_agent"
            }
        except Exception as e:
            logger.error(f"RL recommendation failed: {e}")
        
        # Step 3: Get LLM reasoning
        llm_recommendation = None
        try:
            llm_recommendation = self.reasoning_engine.reason_about_failure(
                failure_info=failure_info,
                system_state=system_state,
                available_actions=["restart_pod", "rebuild_deployment", "replace_pod", "trigger_heal"],
                rl_suggestion=rl_suggestion,
                gnn_suggestion=gnn_suggestion
            )
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
        
        # Step 4: Combine recommendations
        recommendations = []
        if rl_suggestion:
            recommendations.append(rl_suggestion)
        if gnn_suggestion:
            recommendations.append({
                "action": gnn_suggestion.get("action", "no_action"),
                "confidence": gnn_suggestion.get("confidence", 0.5),
                "source": "gnn"
            })
        if llm_recommendation:
            recommendations.append({
                "action": llm_recommendation.get("action", "no_action"),
                "confidence": llm_recommendation.get("confidence", 0.5),
                "source": "llm_reasoning",
                "reasoning": llm_recommendation.get("reasoning", "")
            })
        
        # Select best recommendation
        if recommendations:
            best_rec = max(recommendations, key=lambda r: r.get("confidence", 0.0))
            final_action = best_rec.get("action", "do_nothing")
            final_confidence = best_rec.get("confidence", 0.5)
        else:
            final_action = "do_nothing"
            final_confidence = 0.0
        
        # Step 5: Apply safety checks
        decision = {
            "action": final_action,
            "confidence": final_confidence,
            "recommendations": recommendations,
            "rl_suggestion": rl_suggestion,
            "gnn_suggestion": gnn_suggestion,
            "llm_recommendation": llm_recommendation
        }
        
        safe_decision = self.safety_layer.apply_safety_checks(decision, system_state)
        
        logger.info(f"Healing decision: {safe_decision.get('action')} (confidence: {safe_decision.get('confidence', 0):.2f})")
        
        return safe_decision
    
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

