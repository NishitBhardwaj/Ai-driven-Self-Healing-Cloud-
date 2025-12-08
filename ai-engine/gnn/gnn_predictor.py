"""
GNN Predictor
Combines GNN failure probability, RL suggested action, and LLM reasoning
→ Output final action recommendation
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import logging

from .graph_builder import DependencyGraph, GraphBuilder
from .gnn_model import GATModel, FailureProbabilityPredictor, DependencyAnalyzer, ImpactPredictor

logger = logging.getLogger(__name__)


class GNNPredictor:
    """
    High-level predictor using GNN models
    
    Combines:
    - GNN failure probability prediction
    - RL suggested action
    - LLM reasoning
    → Final action recommendation
    """
    
    def __init__(
        self,
        gat_model: Optional[GATModel] = None,
        failure_predictor: Optional[FailureProbabilityPredictor] = None,
        dependency_analyzer: Optional[DependencyAnalyzer] = None,
        impact_predictor: Optional[ImpactPredictor] = None,
        device: str = "cpu"
    ):
        self.device = torch.device(device)
        
        # Initialize GAT model
        if gat_model is None:
            gat_model = GATModel(input_dim=7, hidden_dim=64, output_dim=32, num_layers=3, num_heads=4)
        self.gat_model = gat_model.to(self.device)
        self.gat_model.eval()
        
        # Initialize failure predictor
        if failure_predictor is None:
            failure_predictor = FailureProbabilityPredictor(self.gat_model)
        self.failure_predictor = failure_predictor.to(self.device)
        self.failure_predictor.eval()
        
        # Initialize dependency analyzer
        if dependency_analyzer is None:
            dependency_analyzer = DependencyAnalyzer(self.gat_model)
        self.dependency_analyzer = dependency_analyzer.to(self.device)
        self.dependency_analyzer.eval()
        
        # Initialize impact predictor
        if impact_predictor is None:
            impact_predictor = ImpactPredictor(self.gat_model)
        self.impact_predictor = impact_predictor.to(self.device)
        self.impact_predictor.eval()
        
        logger.info("GNN Predictor initialized")
    
    def predict_failure_propagation(
        self,
        graph: DependencyGraph,
        failed_node: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Predict which nodes will fail due to propagation
        
        Args:
            graph: Dependency graph
            failed_node: Node that has failed (optional)
        
        Returns:
            Dictionary mapping node IDs to failure probabilities
        """
        # Convert graph to PyG format
        data = graph.to_pyg_data().to(self.device)
        
        # Get failure probabilities
        with torch.no_grad():
            failure_probs = self.failure_predictor.predict_failure_probability(data)
        
        # Map to node IDs
        node_ids = list(graph.graph.nodes())
        failure_dict = {node_id: prob.item() for node_id, prob in zip(node_ids, failure_probs)}
        
        # If a specific node failed, update its probability
        if failed_node and failed_node in failure_dict:
            failure_dict[failed_node] = 1.0
        
        logger.debug(f"Predicted failure propagation for {len(failure_dict)} nodes")
        
        return failure_dict
    
    def analyze_dependencies(self, graph: DependencyGraph) -> Dict[str, float]:
        """
        Analyze node criticality based on dependencies
        
        Args:
            graph: Dependency graph
        
        Returns:
            Dictionary mapping node IDs to criticality scores
        """
        data = graph.to_pyg_data().to(self.device)
        
        with torch.no_grad():
            criticality = self.dependency_analyzer.forward(data)
        
        node_ids = list(graph.graph.nodes())
        criticality_dict = {node_id: score.item() for node_id, score in zip(node_ids, criticality)}
        
        logger.debug(f"Analyzed criticality for {len(criticality_dict)} nodes")
        
        return criticality_dict
    
    def get_critical_nodes(
        self,
        graph: DependencyGraph,
        threshold: float = 0.7,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Get critical nodes based on dependency analysis
        
        Args:
            graph: Dependency graph
            threshold: Criticality threshold
            top_k: Number of top critical nodes to return
        
        Returns:
            List of (node_id, criticality_score) tuples, sorted by criticality
        """
        criticality_dict = self.analyze_dependencies(graph)
        
        # Filter by threshold and sort
        critical_nodes = [
            (node_id, score) for node_id, score in criticality_dict.items()
            if score >= threshold
        ]
        
        # Sort by criticality (descending)
        critical_nodes.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k
        return critical_nodes[:top_k]
    
    def predict_impact(
        self,
        graph: DependencyGraph,
        failed_node: str
    ) -> Dict[str, float]:
        """
        Predict impact of a node failure on other nodes
        
        Args:
            graph: Dependency graph
            failed_node: Node that failed
        
        Returns:
            Dictionary mapping node IDs to impact scores
        """
        if failed_node not in graph.graph:
            logger.warning(f"Node {failed_node} not in graph")
            return {}
        
        data = graph.to_pyg_data().to(self.device)
        node_ids = list(graph.graph.nodes())
        source_idx = node_ids.index(failed_node)
        
        with torch.no_grad():
            impact_scores = self.impact_predictor.forward(data, source_idx)
        
        impact_dict = {node_id: score.item() for node_id, score in zip(node_ids, impact_scores)}
        
        logger.info(f"Predicted impact of {failed_node} failure on {len(impact_dict)} nodes")
        
        return impact_dict
    
    def get_critical_nodes(
        self,
        graph: DependencyGraph,
        threshold: float = 0.7,
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float]]:
        """
        Get critical nodes based on dependency analysis
        
        Args:
            graph: Dependency graph
            threshold: Criticality threshold
            top_k: Return top K nodes (if None, return all above threshold)
        
        Returns:
            List of (node_id, criticality_score) tuples
        """
        criticality_dict = self.analyze_dependencies(graph)
        
        # Filter by threshold and sort
        critical_nodes = [
            (node_id, score) for node_id, score in criticality_dict.items()
            if score >= threshold
        ]
        critical_nodes.sort(key=lambda x: x[1], reverse=True)
        
        if top_k is not None:
            critical_nodes = critical_nodes[:top_k]
        
        logger.info(f"Identified {len(critical_nodes)} critical nodes")
        
        return critical_nodes
    
    def combine_recommendations(
        self,
        graph: DependencyGraph,
        gnn_failure_probs: Dict[str, float],
        rl_action: Optional[Dict[str, Any]] = None,
        llm_reasoning: Optional[Dict[str, Any]] = None,
        system_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Combine GNN failure probability, RL suggested action, and LLM reasoning
        → Output final action recommendation
        
        Args:
            graph: Dependency graph
            gnn_failure_probs: GNN failure probabilities for each node
            rl_action: RL suggested action (optional)
            llm_reasoning: LLM reasoning and recommendation (optional)
            system_state: Current system state (optional)
        
        Returns:
            Final action recommendation with confidence and reasoning
        """
        # Analyze critical nodes
        critical_nodes = self.get_critical_nodes(graph, threshold=0.7, top_k=5)
        
        # Find nodes with high failure probability
        high_risk_nodes = [
            (node_id, prob) for node_id, prob in gnn_failure_probs.items()
            if prob > 0.7
        ]
        high_risk_nodes.sort(key=lambda x: x[1], reverse=True)
        
        # Combine recommendations with weights
        recommendations = []
        weights = {}
        
        # GNN recommendation (based on failure probability and criticality)
        if high_risk_nodes:
            most_at_risk = high_risk_nodes[0][0]
            gnn_recommendation = self._generate_gnn_recommendation(
                graph, most_at_risk, gnn_failure_probs[most_at_risk]
            )
            recommendations.append(gnn_recommendation)
            weights['gnn'] = 0.4
        
        # RL recommendation
        if rl_action:
            rl_recommendation = {
                'action': rl_action.get('action', 'no_action'),
                'confidence': rl_action.get('confidence', 0.5),
                'source': 'rl_agent',
                'reasoning': f"RL agent suggests: {rl_action.get('action', 'no_action')}"
            }
            recommendations.append(rl_recommendation)
            weights['rl'] = 0.35
        
        # LLM recommendation
        if llm_reasoning:
            llm_recommendation = {
                'action': llm_reasoning.get('action', 'no_action'),
                'confidence': llm_reasoning.get('confidence', 0.5),
                'source': 'llm_reasoning',
                'reasoning': llm_reasoning.get('reasoning', ''),
                'explanation': llm_reasoning.get('explanation', '')
            }
            recommendations.append(llm_recommendation)
            weights['llm'] = 0.25
        
        # Combine recommendations
        if not recommendations:
            return {
                'action': 'do_nothing',
                'confidence': 0.0,
                'reasoning': 'No recommendations available',
                'sources': []
            }
        
        # Weighted combination
        action_scores = {}
        for rec in recommendations:
            action = rec['action']
            confidence = rec.get('confidence', 0.5)
            source = rec.get('source', 'unknown')
            weight = weights.get(source, 0.33)
            
            if action not in action_scores:
                action_scores[action] = {
                    'total_score': 0.0,
                    'total_weight': 0.0,
                    'sources': [],
                    'reasonings': []
                }
            
            action_scores[action]['total_score'] += confidence * weight
            action_scores[action]['total_weight'] += weight
            action_scores[action]['sources'].append(source)
            action_scores[action]['reasonings'].append(rec.get('reasoning', ''))
        
        # Select best action
        best_action = max(
            action_scores.items(),
            key=lambda x: x[1]['total_score'] / max(x[1]['total_weight'], 1e-8)
        )
        
        final_confidence = best_action[1]['total_score'] / max(best_action[1]['total_weight'], 1e-8)
        
        # Combine reasonings
        combined_reasoning = " | ".join(best_action[1]['reasonings'])
        
        # Add GNN-specific insights
        if high_risk_nodes:
            combined_reasoning += f" | GNN detected high failure risk: {high_risk_nodes[0][0]} (prob: {high_risk_nodes[0][1]:.2f})"
        
        if critical_nodes:
            combined_reasoning += f" | Critical nodes identified: {len(critical_nodes)}"
        
        final_recommendation = {
            'action': best_action[0],
            'confidence': float(final_confidence),
            'reasoning': combined_reasoning,
            'sources': best_action[1]['sources'],
            'gnn_insights': {
                'high_risk_nodes': high_risk_nodes[:3],
                'critical_nodes': critical_nodes[:3],
                'failure_probs': dict(list(gnn_failure_probs.items())[:5])
            },
            'rl_action': rl_action,
            'llm_reasoning': llm_reasoning
        }
        
        logger.info(f"Final recommendation: {best_action[0]} (confidence: {final_confidence:.2f})")
        
        return final_recommendation
    
    def _generate_gnn_recommendation(
        self,
        graph: DependencyGraph,
        node_id: str,
        failure_prob: float
    ) -> Dict[str, Any]:
        """
        Generate action recommendation based on GNN analysis
        
        Args:
            graph: Dependency graph
            node_id: Node with high failure probability
            failure_prob: Failure probability
        
        Returns:
            GNN recommendation
        """
        node_features = graph.get_node_features(node_id)
        node_type = graph.graph.nodes[node_id].get('node_type', 'unknown')
        
        # Determine action based on node type and failure probability
        if failure_prob > 0.9:
            if node_type == 'pod':
                action = 'restart_pod'
            elif node_type == 'service':
                action = 'rebuild_deployment'
            elif node_type == 'lambda':
                action = 'trigger_heal'
            else:
                action = 'trigger_heal'
        elif failure_prob > 0.7:
            action = 'trigger_heal'
        else:
            action = 'do_nothing'
        
        return {
            'action': action,
            'confidence': failure_prob,
            'source': 'gnn',
            'reasoning': f"GNN predicts {node_id} has {failure_prob:.2%} failure probability. Node type: {node_type}."
        }
    
    def get_healing_priority(
        self,
        graph: DependencyGraph,
        failed_nodes: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Recommend healing priority based on impact analysis
        
        Args:
            graph: Dependency graph
            failed_nodes: List of failed node IDs
        
        Returns:
            List of (node_id, priority_score) tuples, sorted by priority
        """
        priorities = []
        
        for failed_node in failed_nodes:
            if failed_node not in graph.graph:
                continue
            
            # Get impact
            impact_dict = self.predict_impact(graph, failed_node)
            total_impact = sum(impact_dict.values())
            
            # Get criticality
            criticality_dict = self.analyze_dependencies(graph)
            criticality = criticality_dict.get(failed_node, 0.5)
            
            # Get failure probability
            failure_probs = self.predict_failure_propagation(graph, failed_node)
            failure_prob = failure_probs.get(failed_node, 0.5)
            
            # Priority = weighted combination
            priority_score = 0.4 * total_impact + 0.3 * criticality + 0.3 * failure_prob
            priorities.append((failed_node, priority_score))
        
        # Sort by priority (highest first)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Recommended healing priority for {len(priorities)} nodes")
        
        return priorities
    
    def load_models(self, checkpoint_dir: str):
        """Load trained models from checkpoint"""
        import os
        from pathlib import Path
        
        checkpoint_path = Path(checkpoint_dir)
        
        gat_path = checkpoint_path / "gat_model.pth"
        if gat_path.exists():
            self.gat_model.load_state_dict(torch.load(gat_path, map_location=self.device))
            logger.info(f"Loaded GAT model from {gat_path}")
        
        failure_path = checkpoint_path / "failure_predictor.pth"
        if failure_path.exists():
            self.failure_predictor.load_state_dict(torch.load(failure_path, map_location=self.device))
            logger.info(f"Loaded failure predictor from {failure_path}")
        
        analyzer_path = checkpoint_path / "dependency_analyzer.pth"
        if analyzer_path.exists():
            self.dependency_analyzer.load_state_dict(torch.load(analyzer_path, map_location=self.device))
            logger.info(f"Loaded dependency analyzer from {analyzer_path}")
        
        impact_path = checkpoint_path / "impact_predictor.pth"
        if impact_path.exists():
            self.impact_predictor.load_state_dict(torch.load(impact_path, map_location=self.device))
            logger.info(f"Loaded impact predictor from {impact_path}")
    
    def save_models(self, checkpoint_dir: str):
        """Save trained models to checkpoint"""
        from pathlib import Path
        
        checkpoint_path = Path(checkpoint_dir)
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        torch.save(self.gat_model.state_dict(), checkpoint_path / "gat_model.pth")
        torch.save(self.failure_predictor.state_dict(), checkpoint_path / "failure_predictor.pth")
        torch.save(self.dependency_analyzer.state_dict(), checkpoint_path / "dependency_analyzer.pth")
        torch.save(self.impact_predictor.state_dict(), checkpoint_path / "impact_predictor.pth")
        
        logger.info(f"Models saved to {checkpoint_dir}")
