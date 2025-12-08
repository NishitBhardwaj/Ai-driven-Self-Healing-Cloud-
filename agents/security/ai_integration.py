"""
AI Engine Integration for Security Agent
Uses GNN dependencies + LLM threat model
"""

import sys
import os
from typing import Dict, List, Optional, Any
import logging

# Add AI engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_engine.gnn.gnn_predictor import GNNPredictor
from ai_engine.gnn.graph_builder import GraphBuilder, DependencyGraph
from ai_engine.llm_reasoning.reasoning_engine import ReasoningEngine

logger = logging.getLogger(__name__)


class SecurityAIIntegration:
    """
    AI Engine Integration for Security Agent
    
    Uses:
    - GNN for dependency analysis
    - LLM for threat modeling
    """
    
    def __init__(
        self,
        gnn_checkpoint: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        """
        Initialize AI integration
        
        Args:
            gnn_checkpoint: Path to trained GNN checkpoint
            openrouter_api_key: OpenRouter API key
            gemini_api_key: Gemini API key
        """
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
        
        logger.info("Security AI Integration initialized")
    
    def detect_threat(
        self,
        security_logs: List[Dict[str, Any]],
        dependency_graph_data: Optional[Dict[str, Any]] = None,
        network_traffic: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect security threats using GNN dependencies + LLM threat model
        
        Args:
            security_logs: Security logs to analyze
            dependency_graph_data: Dependency graph data
            network_traffic: Network traffic data
        
        Returns:
            Threat detection result
        """
        # Step 1: Analyze dependencies using GNN
        dependency_analysis = {}
        if dependency_graph_data:
            try:
                dependency_graph = GraphBuilder.build_combined(
                    kubernetes_resources=dependency_graph_data.get("kubernetes", {}),
                    localstack_resources=dependency_graph_data.get("localstack", {})
                )
                
                # Get critical nodes
                critical_nodes = self.gnn_predictor.get_critical_nodes(
                    dependency_graph,
                    threshold=0.7,
                    top_k=10
                )
                
                # Analyze impact of potential attacks
                dependency_analysis = {
                    "critical_nodes": critical_nodes,
                    "dependency_graph": dependency_graph
                }
            except Exception as e:
                logger.error(f"GNN dependency analysis failed: {e}")
        
        # Step 2: Use LLM for threat modeling
        threat_analysis = None
        try:
            # Classify threat using LLM
            threat_info = {
                "type": "security_threat",
                "logs": security_logs,
                "network_traffic": network_traffic,
                "critical_services": [node[0] for node in dependency_analysis.get("critical_nodes", [])]
            }
            
            threat_classification = self.reasoning_engine.classify_error(
                error_info=threat_info,
                system_state={"security_logs": security_logs}
            )
            
            # Generate threat response plan
            threat_plan = self.reasoning_engine.generate_healing_plan(
                error_classification=threat_classification,
                system_state={"security_logs": security_logs, "network_traffic": network_traffic},
                available_actions=["block_ip", "isolate_service", "revoke_access", "alert_admin"]
            )
            
            # Evaluate risk
            risk_evaluation = self.reasoning_engine.evaluate_risk(
                action=threat_plan.get("action", "no_action"),
                context={"threat": threat_classification, "dependency_analysis": dependency_analysis}
            )
            
            threat_analysis = {
                "threat_classification": threat_classification,
                "threat_plan": threat_plan,
                "risk_evaluation": risk_evaluation
            }
        except Exception as e:
            logger.error(f"LLM threat analysis failed: {e}")
        
        # Step 3: Combine GNN and LLM analysis
        result = {
            "threat_detected": threat_analysis is not None and threat_analysis.get("threat_classification", {}).get("severity") in ["high", "critical"],
            "threat_type": threat_analysis.get("threat_classification", {}).get("error_type", "unknown") if threat_analysis else "unknown",
            "severity": threat_analysis.get("threat_classification", {}).get("severity", "low") if threat_analysis else "low",
            "recommended_action": threat_analysis.get("threat_plan", {}).get("action", "no_action") if threat_analysis else "no_action",
            "confidence": threat_analysis.get("threat_plan", {}).get("confidence", 0.0) if threat_analysis else 0.0,
            "dependency_analysis": dependency_analysis,
            "threat_analysis": threat_analysis,
            "critical_services_at_risk": [node[0] for node in dependency_analysis.get("critical_nodes", [])]
        }
        
        logger.info(f"Threat detection: detected={result['threat_detected']}, type={result['threat_type']}, severity={result['severity']}")
        
        return result
    
    def validate_security_policy(
        self,
        policy: Dict[str, Any],
        dependency_graph_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate security policy using GNN + LLM
        
        Args:
            policy: Security policy to validate
            dependency_graph_data: Dependency graph data
        
        Returns:
            Policy validation result
        """
        # Analyze dependencies
        dependency_analysis = {}
        if dependency_graph_data:
            try:
                dependency_graph = GraphBuilder.build_combined(
                    kubernetes_resources=dependency_graph_data.get("kubernetes", {}),
                    localstack_resources=dependency_graph_data.get("localstack", {})
                )
                
                # Get critical nodes that need protection
                critical_nodes = self.gnn_predictor.get_critical_nodes(dependency_graph, threshold=0.7)
                dependency_analysis["critical_nodes"] = critical_nodes
            except Exception as e:
                logger.error(f"GNN analysis failed: {e}")
        
        # Use LLM to evaluate policy
        policy_evaluation = self.reasoning_engine.evaluate_risk(
            action="validate_policy",
            context={"policy": policy, "dependency_analysis": dependency_analysis}
        )
        
        return {
            "policy_valid": policy_evaluation.get("is_safe", True),
            "risk_level": policy_evaluation.get("risk_level", "low"),
            "issues": policy_evaluation.get("safety_concerns", []),
            "recommendations": policy_evaluation.get("recommended_safeguards", []),
            "dependency_analysis": dependency_analysis
        }

