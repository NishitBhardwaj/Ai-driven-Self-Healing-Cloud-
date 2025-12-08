"""
Graph Neural Network Model
PyTorch Geometric GAT (Graph Attention Network) for failure probability prediction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool, global_max_pool
from torch_geometric.data import Data, Batch
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GATModel(nn.Module):
    """
    Graph Attention Network (GAT) for dependency modeling
    
    Uses multi-head attention to learn node representations
    that capture service dependencies and failure propagation patterns
    """
    
    def __init__(
        self,
        input_dim: int = 7,
        hidden_dim: int = 64,
        output_dim: int = 32,
        num_layers: int = 3,
        num_heads: int = 4,
        dropout: float = 0.1
    ):
        super(GATModel, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.dropout = dropout
        
        # Build GAT layers
        self.convs = nn.ModuleList()
        self.batch_norms = nn.ModuleList()
        
        # Input layer
        self.convs.append(
            GATConv(input_dim, hidden_dim, heads=num_heads, dropout=dropout, concat=True)
        )
        self.batch_norms.append(nn.BatchNorm1d(hidden_dim * num_heads))
        
        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(
                GATConv(hidden_dim * num_heads, hidden_dim, heads=num_heads, dropout=dropout, concat=True)
            )
            self.batch_norms.append(nn.BatchNorm1d(hidden_dim * num_heads))
        
        # Output layer (single head for final representation)
        self.convs.append(
            GATConv(hidden_dim * num_heads, output_dim, heads=1, dropout=dropout, concat=False)
        )
        
        # Dropout
        self.dropout_layer = nn.Dropout(dropout)
        
        logger.info(f"GAT Model initialized: layers={num_layers}, hidden_dim={hidden_dim}, heads={num_heads}")
    
    def forward(self, data: Data) -> torch.Tensor:
        """
        Forward pass through the GAT
        
        Args:
            data: PyG Data object with node features and edge indices
        
        Returns:
            Node embeddings
        """
        x, edge_index = data.x, data.edge_index
        
        # Apply GAT layers
        for i, conv in enumerate(self.convs[:-1]):
            x = conv(x, edge_index)
            x = self.batch_norms[i](x)
            x = F.relu(x)
            x = self.dropout_layer(x)
        
        # Final layer
        x = self.convs[-1](x, edge_index)
        
        return x


class FailureProbabilityPredictor(nn.Module):
    """
    Predicts failure probability for each node using GAT
    
    Uses Graph Attention Network to learn failure patterns
    """
    
    def __init__(
        self,
        gat_model: GATModel,
        hidden_dim: int = 64
    ):
        super(FailureProbabilityPredictor, self).__init__()
        
        self.gat_model = gat_model
        
        # Failure probability classifier
        self.classifier = nn.Sequential(
            nn.Linear(gat_model.output_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()  # Output probability [0, 1]
        )
        
        logger.info("Failure Probability Predictor initialized")
    
    def forward(self, data: Data) -> torch.Tensor:
        """
        Predict failure probability for each node
        
        Args:
            data: PyG Data object
        
        Returns:
            Failure probabilities [num_nodes, 1]
        """
        # Get node embeddings from GAT
        node_embeddings = self.gat_model(data)
        
        # Classify failure probability
        failure_probs = self.classifier(node_embeddings)
        
        return failure_probs.squeeze(1)  # [num_nodes]
    
    def predict_failure_probability(self, data: Data) -> torch.Tensor:
        """
        Get failure probability for each node
        
        Args:
            data: PyG Data object
        
        Returns:
            Failure probabilities [num_nodes]
        """
        with torch.no_grad():
            probs = self.forward(data)
        return probs


class DependencyAnalyzer(nn.Module):
    """
    Analyzes service dependencies and critical paths using GAT
    """
    
    def __init__(self, gat_model: GATModel, hidden_dim: int = 64):
        super(DependencyAnalyzer, self).__init__()
        
        self.gat_model = gat_model
        
        # Criticality predictor
        self.criticality_predictor = nn.Sequential(
            nn.Linear(gat_model.output_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
        logger.info("Dependency Analyzer initialized")
    
    def forward(self, data: Data) -> torch.Tensor:
        """
        Predict service criticality
        
        Args:
            data: PyG Data object
        
        Returns:
            Criticality scores for each node [num_nodes]
        """
        node_embeddings = self.gat_model(data)
        criticality = self.criticality_predictor(node_embeddings)
        return criticality.squeeze()
    
    def get_critical_services(self, data: Data, threshold: float = 0.7) -> List[int]:
        """
        Get list of critical service indices
        
        Args:
            data: PyG Data object
            threshold: Criticality threshold
        
        Returns:
            List of critical service indices
        """
        with torch.no_grad():
            criticality = self.forward(data)
            critical_indices = (criticality > threshold).nonzero(as_tuple=True)[0].tolist()
        return critical_indices


class ImpactPredictor(nn.Module):
    """
    Predicts impact of node failures on dependent nodes using GAT
    """
    
    def __init__(self, gat_model: GATModel, hidden_dim: int = 64):
        super(ImpactPredictor, self).__init__()
        
        self.gat_model = gat_model
        
        # Impact predictor (node pair -> impact score)
        self.impact_predictor = nn.Sequential(
            nn.Linear(gat_model.output_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        logger.info("Impact Predictor initialized")
    
    def forward(self, data: Data, source_node: int) -> torch.Tensor:
        """
        Predict impact of source node failure on all other nodes
        
        Args:
            data: PyG Data object
            source_node: Index of source node that fails
        
        Returns:
            Impact scores for all nodes [num_nodes]
        """
        node_embeddings = self.gat_model(data)
        source_embedding = node_embeddings[source_node]
        
        # Concatenate source embedding with each node embedding
        num_nodes = node_embeddings.size(0)
        source_expanded = source_embedding.unsqueeze(0).expand(num_nodes, -1)
        combined = torch.cat([source_expanded, node_embeddings], dim=1)
        
        impact_scores = self.impact_predictor(combined)
        return impact_scores.squeeze()
    
    def get_impact_ranking(self, data: Data, source_node: int, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Get top-k most impacted nodes
        
        Args:
            data: PyG Data object
            source_node: Index of source node
            top_k: Number of top impacts to return
        
        Returns:
            List of (node_index, impact_score) tuples
        """
        with torch.no_grad():
            impact_scores = self.forward(data, source_node)
            top_impacts = torch.topk(impact_scores, min(top_k, len(impact_scores)))
            
            return [(idx.item(), score.item()) for idx, score in zip(top_impacts.indices, top_impacts.values)]
