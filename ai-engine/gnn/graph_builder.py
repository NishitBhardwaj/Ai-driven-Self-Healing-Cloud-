"""
Graph Builder for Dependency Modeling
Builds graph from Kubernetes + LocalStack with services, pods, databases, S3, Lambda
"""

import networkx as nx
import numpy as np
import torch
from torch_geometric.data import Data
from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the dependency graph"""
    SERVICE = "service"
    POD = "pod"
    DATABASE = "database"
    S3 = "s3"
    LAMBDA = "lambda"


class EdgeType(Enum):
    """Types of edges in the dependency graph"""
    API_CALL = "api_call"
    DATA_FLOW = "data_flow"
    DEPENDENCY_LOAD = "dependency_load"


class GraphBuilder:
    """
    Builder for creating dependency graphs from Kubernetes and LocalStack
    
    Nodes:
    - services (Kubernetes services)
    - pods (Kubernetes pods)
    - databases (DynamoDB, RDS, etc.)
    - S3 (S3 buckets)
    - Lambda (Lambda functions)
    
    Edges:
    - API calls (service-to-service communication)
    - data flow (data transfer between components)
    - dependency load (how much one component depends on another)
    """
    
    @staticmethod
    def build_from_kubernetes(
        deployments: List[Dict],
        services: List[Dict],
        pods: List[Dict],
        configmaps: Optional[List[Dict]] = None
    ) -> 'DependencyGraph':
        """
        Build dependency graph from Kubernetes resources
        
        Args:
            deployments: List of Kubernetes deployment information
            services: List of Kubernetes service information
            pods: List of Kubernetes pod information
            configmaps: Optional list of ConfigMap information
        
        Returns:
            DependencyGraph
        """
        graph = DependencyGraph()
        
        # Add service nodes
        for service in services:
            service_name = service.get('name', '')
            service_type = service.get('type', 'service')
            
            features = {
                'cpu_usage': service.get('cpu_usage', 0.0),
                'memory_usage': service.get('memory_usage', 0.0),
                'health_score': service.get('health_score', 1.0),
                'request_rate': service.get('request_rate', 0.0),
                'error_rate': service.get('error_rate', 0.0),
                'is_healthy': service.get('is_healthy', True),
                'has_failure': service.get('has_failure', False),
                'replicas': service.get('replicas', 1),
                'node_type': NodeType.SERVICE.value
            }
            
            graph.add_node(service_name, NodeType.SERVICE, features)
        
        # Add pod nodes
        for pod in pods:
            pod_name = pod.get('name', '')
            service_name = pod.get('service', pod.get('app', ''))
            
            features = {
                'cpu_usage': pod.get('cpu_usage', 0.0),
                'memory_usage': pod.get('memory_usage', 0.0),
                'health_score': 1.0 if pod.get('is_healthy', True) else 0.0,
                'request_rate': 0.0,
                'error_rate': pod.get('error_rate', 0.0),
                'is_healthy': pod.get('is_healthy', True),
                'has_failure': pod.get('has_failure', False),
                'restart_count': pod.get('restart_count', 0),
                'node_type': NodeType.POD.value,
                'service': service_name
            }
            
            graph.add_node(pod_name, NodeType.POD, features)
            
            # Add edge from pod to service (dependency_load)
            if service_name and service_name in graph.graph:
                graph.add_edge(
                    pod_name, service_name,
                    EdgeType.DEPENDENCY_LOAD,
                    weight=1.0,
                    features={'load_factor': 1.0}
                )
        
        # Add dependencies from service labels/annotations
        for service in services:
            service_name = service.get('name', '')
            dependencies = service.get('dependencies', [])
            
            for dep in dependencies:
                if dep in graph.graph:
                    # API call edge
                    graph.add_edge(
                        service_name, dep,
                        EdgeType.API_CALL,
                        weight=service.get('dependency_weight', 1.0),
                        features={
                            'request_count': service.get('request_count', 0),
                            'latency': service.get('latency', 0.0),
                            'error_rate': service.get('error_rate', 0.0)
                        }
                    )
        
        logger.info(f"Built graph from Kubernetes: {len(graph.graph.nodes())} nodes, {len(graph.graph.edges())} edges")
        
        return graph
    
    @staticmethod
    def build_from_localstack(
        s3_buckets: List[Dict],
        lambda_functions: List[Dict],
        dynamodb_tables: List[Dict],
        sqs_queues: Optional[List[Dict]] = None,
        sns_topics: Optional[List[Dict]] = None
    ) -> 'DependencyGraph':
        """
        Build dependency graph from LocalStack resources
        
        Args:
            s3_buckets: List of S3 bucket information
            lambda_functions: List of Lambda function information
            dynamodb_tables: List of DynamoDB table information
            sqs_queues: Optional list of SQS queue information
            sns_topics: Optional list of SNS topic information
        
        Returns:
            DependencyGraph
        """
        graph = DependencyGraph()
        
        # Add S3 bucket nodes
        for bucket in s3_buckets:
            bucket_name = bucket.get('name', '')
            features = {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'health_score': 1.0,
                'request_rate': bucket.get('request_count', 0.0),
                'error_rate': bucket.get('error_rate', 0.0),
                'is_healthy': bucket.get('is_healthy', True),
                'has_failure': bucket.get('has_failure', False),
                'storage_used': bucket.get('storage_used', 0.0),
                'node_type': NodeType.S3.value
            }
            graph.add_node(bucket_name, NodeType.S3, features)
        
        # Add Lambda function nodes
        for func in lambda_functions:
            func_name = func.get('name', '')
            features = {
                'cpu_usage': func.get('cpu_usage', 0.0),
                'memory_usage': func.get('memory_usage', 0.0),
                'health_score': 1.0 if func.get('is_healthy', True) else 0.0,
                'request_rate': func.get('invocation_count', 0.0),
                'error_rate': func.get('error_rate', 0.0),
                'is_healthy': func.get('is_healthy', True),
                'has_failure': func.get('has_failure', False),
                'execution_time': func.get('execution_time', 0.0),
                'node_type': NodeType.LAMBDA.value
            }
            graph.add_node(func_name, NodeType.LAMBDA, features)
            
            # Add edges from Lambda to S3 (data flow)
            s3_deps = func.get('s3_dependencies', [])
            for s3_bucket in s3_deps:
                if s3_bucket in graph.graph:
                    graph.add_edge(
                        func_name, s3_bucket,
                        EdgeType.DATA_FLOW,
                        weight=1.0,
                        features={'data_size': func.get('data_size', 0.0)}
                    )
        
        # Add DynamoDB table nodes
        for table in dynamodb_tables:
            table_name = table.get('name', '')
            features = {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'health_score': 1.0,
                'request_rate': table.get('request_count', 0.0),
                'error_rate': table.get('error_rate', 0.0),
                'is_healthy': table.get('is_healthy', True),
                'has_failure': table.get('has_failure', False),
                'item_count': table.get('item_count', 0),
                'node_type': NodeType.DATABASE.value
            }
            graph.add_node(table_name, NodeType.DATABASE, features)
            
            # Add edges from Lambda to DynamoDB (data flow)
            lambda_deps = table.get('lambda_dependencies', [])
            for lambda_func in lambda_deps:
                if lambda_func in graph.graph:
                    graph.add_edge(
                        lambda_func, table_name,
                        EdgeType.DATA_FLOW,
                        weight=1.0,
                        features={'operation_count': table.get('operation_count', 0.0)}
                    )
        
        logger.info(f"Built graph from LocalStack: {len(graph.graph.nodes())} nodes, {len(graph.graph.edges())} edges")
        
        return graph
    
    @staticmethod
    def build_combined(
        kubernetes_resources: Dict,
        localstack_resources: Dict
    ) -> 'DependencyGraph':
        """
        Build combined dependency graph from both Kubernetes and LocalStack
        
        Args:
            kubernetes_resources: Dict with 'deployments', 'services', 'pods', 'configmaps'
            localstack_resources: Dict with 's3_buckets', 'lambda_functions', 'dynamodb_tables', etc.
        
        Returns:
            Combined DependencyGraph
        """
        # Build Kubernetes graph
        k8s_graph = GraphBuilder.build_from_kubernetes(
            deployments=kubernetes_resources.get('deployments', []),
            services=kubernetes_resources.get('services', []),
            pods=kubernetes_resources.get('pods', []),
            configmaps=kubernetes_resources.get('configmaps', [])
        )
        
        # Build LocalStack graph
        ls_graph = GraphBuilder.build_from_localstack(
            s3_buckets=localstack_resources.get('s3_buckets', []),
            lambda_functions=localstack_resources.get('lambda_functions', []),
            dynamodb_tables=localstack_resources.get('dynamodb_tables', []),
            sqs_queues=localstack_resources.get('sqs_queues', []),
            sns_topics=localstack_resources.get('sns_topics', [])
        )
        
        # Combine graphs
        combined_graph = DependencyGraph()
        
        # Add all nodes
        for node in k8s_graph.graph.nodes():
            combined_graph.graph.add_node(node, **k8s_graph.graph.nodes[node])
            combined_graph.node_features[node] = k8s_graph.node_features.get(node, {}).copy()
        
        for node in ls_graph.graph.nodes():
            combined_graph.graph.add_node(node, **ls_graph.graph.nodes[node])
            combined_graph.node_features[node] = ls_graph.node_features.get(node, {}).copy()
        
        # Add all edges
        for source, target in k8s_graph.graph.edges():
            combined_graph.graph.add_edge(source, target, **k8s_graph.graph[source][target])
            edge_key = (source, target)
            if edge_key in k8s_graph.edge_features:
                combined_graph.edge_features[edge_key] = k8s_graph.edge_features[edge_key].copy()
        
        for source, target in ls_graph.graph.edges():
            combined_graph.graph.add_edge(source, target, **ls_graph.graph[source][target])
            edge_key = (source, target)
            if edge_key in ls_graph.edge_features:
                combined_graph.edge_features[edge_key] = ls_graph.edge_features[edge_key].copy()
        
        # Add cross-cloud dependencies (e.g., service -> Lambda, service -> S3)
        services = kubernetes_resources.get('services', [])
        lambda_funcs = localstack_resources.get('lambda_functions', [])
        s3_buckets = localstack_resources.get('s3_buckets', [])
        
        for service in services:
            service_name = service.get('name', '')
            # Check if service calls Lambda
            lambda_deps = service.get('lambda_dependencies', [])
            for lambda_func in lambda_deps:
                if lambda_func in combined_graph.graph:
                    combined_graph.add_edge(
                        service_name, lambda_func,
                        EdgeType.API_CALL,
                        weight=1.0,
                        features={'request_count': service.get('request_count', 0)}
                    )
            
            # Check if service uses S3
            s3_deps = service.get('s3_dependencies', [])
            for s3_bucket in s3_deps:
                if s3_bucket in combined_graph.graph:
                    combined_graph.add_edge(
                        service_name, s3_bucket,
                        EdgeType.DATA_FLOW,
                        weight=1.0,
                        features={'data_size': service.get('data_size', 0.0)}
                    )
        
        logger.info(f"Built combined graph: {len(combined_graph.graph.nodes())} nodes, {len(combined_graph.graph.edges())} edges")
        
        return combined_graph


class DependencyGraph:
    """
    Dependency graph for cloud infrastructure
    
    Models relationships between:
    - Services (Kubernetes)
    - Pods (Kubernetes)
    - Databases (DynamoDB, etc.)
    - S3 buckets
    - Lambda functions
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_features = {}
        self.edge_features = {}
        
        logger.info("Dependency graph initialized")
    
    def add_node(self, node_id: str, node_type: NodeType, features: Optional[Dict] = None):
        """
        Add a node to the graph
        
        Args:
            node_id: Unique node identifier
            node_type: Type of node (SERVICE, POD, DATABASE, S3, LAMBDA)
            features: Node features
        """
        self.graph.add_node(node_id, node_type=node_type.value)
        self.node_features[node_id] = features or {}
        logger.debug(f"Added {node_type.value} node: {node_id}")
    
    def add_edge(self, source: str, target: str, edge_type: EdgeType,
                 weight: float = 1.0, features: Optional[Dict] = None):
        """
        Add an edge between nodes
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of edge (API_CALL, DATA_FLOW, DEPENDENCY_LOAD)
            weight: Edge weight
            features: Edge features
        """
        if source not in self.graph or target not in self.graph:
            logger.warning(f"Cannot add edge: nodes {source} or {target} not in graph")
            return
        
        self.graph.add_edge(source, target, 
                           edge_type=edge_type.value,
                           weight=weight)
        edge_key = (source, target)
        self.edge_features[edge_key] = features or {}
        logger.debug(f"Added {edge_type.value} edge: {source} -> {target}")
    
    def get_node_features(self, node_id: str) -> Dict:
        """Get features for a node"""
        return self.node_features.get(node_id, {})
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighboring nodes"""
        return list(self.graph.neighbors(node_id))
    
    def get_dependencies(self, node_id: str) -> List[str]:
        """Get nodes this node depends on"""
        return list(self.graph.predecessors(node_id))
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get nodes that depend on this node"""
        return list(self.graph.successors(node_id))
    
    def to_pyg_data(self) -> Data:
        """
        Convert to PyTorch Geometric Data format
        
        Returns:
            PyG Data object
        """
        # Node mapping
        node_list = list(self.graph.nodes())
        node_to_idx = {node: idx for idx, node in enumerate(node_list)}
        
        # Node features: [cpu_usage, memory_usage, health_score, request_rate, error_rate, is_healthy, has_failure]
        node_features = []
        for node in node_list:
            features = self.node_features.get(node, {})
            feature_vector = [
                features.get('cpu_usage', 0.0),
                features.get('memory_usage', 0.0),
                features.get('health_score', 1.0),
                features.get('request_rate', 0.0),
                features.get('error_rate', 0.0),
                float(features.get('is_healthy', True)),
                float(features.get('has_failure', False))
            ]
            node_features.append(feature_vector)
        
        node_features_tensor = torch.FloatTensor(node_features)
        
        # Edge indices and attributes
        edge_indices = []
        edge_attrs = []
        
        for source, target in self.graph.edges():
            source_idx = node_to_idx[source]
            target_idx = node_to_idx[target]
            edge_indices.append([source_idx, target_idx])
            
            # Edge attributes: [weight, is_api_call, is_data_flow, is_dependency_load, latency, request_count]
            edge_data = self.graph[source][target]
            edge_features = self.edge_features.get((source, target), {})
            
            edge_type = edge_data.get('edge_type', '')
            edge_attr = [
                edge_data.get('weight', 1.0),
                float(edge_type == EdgeType.API_CALL.value),
                float(edge_type == EdgeType.DATA_FLOW.value),
                float(edge_type == EdgeType.DEPENDENCY_LOAD.value),
                edge_features.get('latency', 0.0),
                edge_features.get('request_count', edge_features.get('operation_count', 0.0))
            ]
            edge_attrs.append(edge_attr)
        
        edge_index = torch.LongTensor(edge_indices).t().contiguous() if edge_indices else torch.empty((2, 0), dtype=torch.long)
        edge_attr = torch.FloatTensor(edge_attrs) if edge_attrs else torch.empty((0, 6), dtype=torch.float)
        
        # Create PyG Data object
        data = Data(
            x=node_features_tensor,
            edge_index=edge_index,
            edge_attr=edge_attr
        )
        
        return data
    
    def get_failure_impact(self, node_id: str) -> Dict:
        """
        Analyze impact of a node failure
        
        Args:
            node_id: Node that failed
        
        Returns:
            Dictionary with impact analysis
        """
        if node_id not in self.graph:
            return {'impacted_nodes': [], 'impact_score': 0.0}
        
        # Get all nodes that depend on this node (transitive)
        impacted = set()
        queue = [node_id]
        
        while queue:
            current = queue.pop(0)
            dependents = self.get_dependents(current)
            for dependent in dependents:
                if dependent not in impacted:
                    impacted.add(dependent)
                    queue.append(dependent)
        
        # Calculate impact score
        impact_score = len(impacted)
        for node in impacted:
            features = self.node_features.get(node, {})
            importance = features.get('health_score', 1.0)
            impact_score += importance
        
        return {
            'impacted_nodes': list(impacted),
            'impact_score': impact_score,
            'direct_dependents': self.get_dependents(node_id)
        }
