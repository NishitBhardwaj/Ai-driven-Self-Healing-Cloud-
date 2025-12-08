"""
Memory System for Meta-Agent
Implement: short-term memory, long-term embeddings, decision archives
"""

from typing import Dict, List, Optional, Any, Tuple
from collections import deque
import json
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    Short-term memory for recent events and decisions
    
    Stores:
    - Recent events (last N events)
    - Recent decisions (last N decisions)
    - Active recovery plans
    """
    
    def __init__(self, max_events: int = 100, max_decisions: int = 50):
        """
        Initialize short-term memory
        
        Args:
            max_events: Maximum number of events to store
            max_decisions: Maximum number of decisions to store
        """
        self.max_events = max_events
        self.max_decisions = max_decisions
        
        self.recent_events = deque(maxlen=max_events)
        self.recent_decisions = deque(maxlen=max_decisions)
        self.active_plans = {}  # plan_id -> plan
        
        logger.info(f"ShortTermMemory initialized: max_events={max_events}, max_decisions={max_decisions}")
    
    def store_event(self, event: Dict[str, Any]):
        """Store recent event"""
        event["stored_at"] = datetime.now().isoformat()
        self.recent_events.append(event)
        logger.debug(f"Event stored in short-term memory: {event.get('type', 'unknown')}")
    
    def store_decision(self, decision: Dict[str, Any]):
        """Store recent decision"""
        decision["stored_at"] = datetime.now().isoformat()
        self.recent_decisions.append(decision)
        logger.debug(f"Decision stored in short-term memory: {decision.get('action', 'unknown')}")
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent events"""
        events = list(self.recent_events)
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        return events[-limit:]
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get recent decisions"""
        return list(self.recent_decisions)[-limit:]
    
    def add_active_plan(self, plan_id: str, plan: Dict[str, Any]):
        """Add active recovery plan"""
        plan["plan_id"] = plan_id
        plan["created_at"] = datetime.now().isoformat()
        self.active_plans[plan_id] = plan
        logger.debug(f"Active plan added: {plan_id}")
    
    def remove_active_plan(self, plan_id: str):
        """Remove completed plan"""
        if plan_id in self.active_plans:
            del self.active_plans[plan_id]
            logger.debug(f"Active plan removed: {plan_id}")
    
    def get_active_plans(self) -> Dict[str, Dict]:
        """Get all active plans"""
        return self.active_plans.copy()


class LongTermEmbeddings:
    """
    Long-term memory using embeddings
    
    Stores:
    - Decision embeddings
    - Pattern embeddings
    - Similarity-based retrieval
    """
    
    def __init__(self, embedding_dim: int = 128):
        """
        Initialize long-term embeddings
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.decision_embeddings = {}  # decision_id -> embedding
        self.pattern_embeddings = {}  # pattern_id -> embedding
        self.embeddings_metadata = {}  # id -> metadata
        
        logger.info(f"LongTermEmbeddings initialized: embedding_dim={embedding_dim}")
    
    def store_decision_embedding(
        self,
        decision_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ):
        """
        Store decision embedding
        
        Args:
            decision_id: Decision identifier
            embedding: Embedding vector
            metadata: Associated metadata
        """
        if embedding.shape[0] != self.embedding_dim:
            # Resize if needed
            if embedding.shape[0] < self.embedding_dim:
                padding = np.zeros(self.embedding_dim - embedding.shape[0])
                embedding = np.concatenate([embedding, padding])
            else:
                embedding = embedding[:self.embedding_dim]
        
        self.decision_embeddings[decision_id] = embedding
        self.embeddings_metadata[decision_id] = metadata
        logger.debug(f"Decision embedding stored: {decision_id}")
    
    def store_pattern_embedding(
        self,
        pattern_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ):
        """
        Store pattern embedding
        
        Args:
            pattern_id: Pattern identifier
            embedding: Embedding vector
            metadata: Associated metadata
        """
        if embedding.shape[0] != self.embedding_dim:
            if embedding.shape[0] < self.embedding_dim:
                padding = np.zeros(self.embedding_dim - embedding.shape[0])
                embedding = np.concatenate([embedding, padding])
            else:
                embedding = embedding[:self.embedding_dim]
        
        self.pattern_embeddings[pattern_id] = embedding
        self.embeddings_metadata[pattern_id] = metadata
        logger.debug(f"Pattern embedding stored: {pattern_id}")
    
    def find_similar_decisions(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find similar decisions using embeddings
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of similar decisions to return
        
        Returns:
            List of (decision_id, similarity_score, metadata) tuples
        """
        if not self.decision_embeddings:
            return []
        
        # Normalize query embedding
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        similarities = []
        for decision_id, embedding in self.decision_embeddings.items():
            # Normalize embedding
            emb_norm = embedding / (np.linalg.norm(embedding) + 1e-8)
            
            # Cosine similarity
            similarity = np.dot(query_norm, emb_norm)
            similarities.append((
                decision_id,
                float(similarity),
                self.embeddings_metadata.get(decision_id, {})
            ))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def find_similar_patterns(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find similar patterns using embeddings
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of similar patterns to return
        
        Returns:
            List of (pattern_id, similarity_score, metadata) tuples
        """
        if not self.pattern_embeddings:
            return []
        
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-8)
        
        similarities = []
        for pattern_id, embedding in self.pattern_embeddings.items():
            emb_norm = embedding / (np.linalg.norm(embedding) + 1e-8)
            similarity = np.dot(query_norm, emb_norm)
            similarities.append((
                pattern_id,
                float(similarity),
                self.embeddings_metadata.get(pattern_id, {})
            ))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]


class DecisionArchive:
    """
    Decision archives for long-term storage
    
    Stores:
    - All decisions with outcomes
    - Decision patterns
    - Performance metrics
    """
    
    def __init__(self, max_size: int = 100000):
        """
        Initialize decision archive
        
        Args:
            max_size: Maximum number of decisions to archive
        """
        self.max_size = max_size
        self.archives = {}  # decision_id -> archive_entry
        self.patterns = {}  # pattern_id -> pattern_data
        
        logger.info(f"DecisionArchive initialized: max_size={max_size}")
    
    def archive_decision(
        self,
        decision_id: str,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        outcome: Optional[Dict[str, Any]] = None,
        success: Optional[bool] = None
    ):
        """
        Archive a decision
        
        Args:
            decision_id: Decision identifier
            decision: Decision made
            context: Context at time of decision
            outcome: Outcome information
            success: Whether decision was successful
        """
        archive_entry = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context,
            "outcome": outcome,
            "success": success
        }
        
        self.archives[decision_id] = archive_entry
        
        # Enforce max size
        if len(self.archives) > self.max_size:
            # Remove oldest entries
            sorted_entries = sorted(
                self.archives.items(),
                key=lambda x: x[1].get("timestamp", "")
            )
            for old_id, _ in sorted_entries[:len(self.archives) - self.max_size]:
                del self.archives[old_id]
        
        logger.debug(f"Decision archived: {decision_id}")
    
    def extract_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any]
    ):
        """
        Extract and store a pattern
        
        Args:
            pattern_id: Pattern identifier
            pattern_data: Pattern data
        """
        self.patterns[pattern_id] = {
            "pattern_id": pattern_id,
            "timestamp": datetime.now().isoformat(),
            "data": pattern_data
        }
        logger.debug(f"Pattern extracted: {pattern_id}")
    
    def get_decision(self, decision_id: str) -> Optional[Dict]:
        """Get archived decision"""
        return self.archives.get(decision_id)
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict]:
        """Get pattern"""
        return self.patterns.get(pattern_id)
    
    def search_decisions(
        self,
        query: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict]:
        """
        Search decisions by criteria
        
        Args:
            query: Search criteria
            limit: Maximum results
        
        Returns:
            List of matching decisions
        """
        results = []
        
        for decision_id, archive in self.archives.items():
            match = True
            
            # Match on action
            if "action" in query:
                if archive["decision"].get("action") != query["action"]:
                    match = False
            
            # Match on success
            if "success" in query:
                if archive.get("success") != query["success"]:
                    match = False
            
            # Match on time range
            if "start_time" in query:
                if archive["timestamp"] < query["start_time"]:
                    match = False
            
            if "end_time" in query:
                if archive["timestamp"] > query["end_time"]:
                    match = False
            
            if match:
                results.append(archive)
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return results[:limit]


class MetaAgentMemory:
    """
    Complete memory system for Meta-Agent
    
    Combines:
    - Short-term memory
    - Long-term embeddings
    - Decision archives
    """
    
    def __init__(
        self,
        short_term_max_events: int = 100,
        short_term_max_decisions: int = 50,
        embedding_dim: int = 128,
        archive_max_size: int = 100000
    ):
        """
        Initialize meta-agent memory
        
        Args:
            short_term_max_events: Max events in short-term memory
            short_term_max_decisions: Max decisions in short-term memory
            embedding_dim: Dimension of embeddings
            archive_max_size: Max size of decision archive
        """
        self.short_term = ShortTermMemory(short_term_max_events, short_term_max_decisions)
        self.long_term_embeddings = LongTermEmbeddings(embedding_dim)
        self.decision_archive = DecisionArchive(archive_max_size)
        
        logger.info("MetaAgentMemory initialized")
    
    def store_event(self, event: Dict[str, Any]):
        """Store event in short-term memory"""
        self.short_term.store_event(event)
    
    def store_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any],
        decision_id: Optional[str] = None
    ) -> str:
        """
        Store decision in all memory systems
        
        Args:
            decision: Decision made
            context: Context
            decision_id: Optional decision ID
        
        Returns:
            Decision ID
        """
        if decision_id is None:
            decision_id = f"decision_{len(self.decision_archive.archives)}_{datetime.now().isoformat()}"
        
        # Store in short-term memory
        self.short_term.store_decision(decision)
        
        # Generate embedding (simplified - in practice would use actual embedding model)
        embedding = self._generate_embedding(decision, context)
        
        # Store in long-term embeddings
        self.long_term_embeddings.store_decision_embedding(
            decision_id,
            embedding,
            {"decision": decision, "context": context}
        )
        
        # Archive decision
        self.decision_archive.archive_decision(decision_id, decision, context)
        
        return decision_id
    
    def update_decision_outcome(
        self,
        decision_id: str,
        outcome: Dict[str, Any],
        success: bool
    ):
        """
        Update decision outcome
        
        Args:
            decision_id: Decision ID
            outcome: Outcome information
            success: Whether successful
        """
        # Update archive
        if decision_id in self.decision_archive.archives:
            self.decision_archive.archives[decision_id]["outcome"] = outcome
            self.decision_archive.archives[decision_id]["success"] = success
    
    def retrieve_similar_decisions(
        self,
        query_decision: Dict[str, Any],
        query_context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar past decisions
        
        Args:
            query_decision: Current decision
            query_context: Current context
            top_k: Number of similar decisions
        
        Returns:
            List of similar decisions with outcomes
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query_decision, query_context)
        
        # Find similar decisions
        similar = self.long_term_embeddings.find_similar_decisions(query_embedding, top_k)
        
        # Get full decision data from archive
        results = []
        for decision_id, similarity, metadata in similar:
            archived = self.decision_archive.get_decision(decision_id)
            if archived:
                archived["similarity"] = similarity
                results.append(archived)
        
        return results
    
    def _generate_embedding(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> np.ndarray:
        """
        Generate embedding for decision and context
        
        Args:
            decision: Decision
            context: Context
        
        Returns:
            Embedding vector
        """
        # Simplified embedding generation
        # In practice, would use actual embedding model (e.g., sentence transformers)
        
        # Extract features
        action = decision.get("action", "no_action")
        confidence = decision.get("confidence", 0.0)
        cpu = context.get("cpu_usage", 0.0)
        memory = context.get("memory_usage", 0.0)
        error_rate = context.get("error_rate", 0.0)
        
        # Create feature vector
        features = np.array([
            hash(action) % 1000 / 1000.0,  # Action encoding
            confidence,
            cpu / 100.0,
            memory / 100.0,
            error_rate / 100.0
        ])
        
        # Pad to embedding dimension
        embedding_dim = self.long_term_embeddings.embedding_dim
        if len(features) < embedding_dim:
            padding = np.random.normal(0, 0.1, embedding_dim - len(features))
            embedding = np.concatenate([features, padding])
        else:
            embedding = features[:embedding_dim]
        
        return embedding
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term": {
                "events": len(self.short_term.recent_events),
                "decisions": len(self.short_term.recent_decisions),
                "active_plans": len(self.short_term.active_plans)
            },
            "long_term_embeddings": {
                "decision_embeddings": len(self.long_term_embeddings.decision_embeddings),
                "pattern_embeddings": len(self.long_term_embeddings.pattern_embeddings)
            },
            "decision_archive": {
                "archived_decisions": len(self.decision_archive.archives),
                "patterns": len(self.decision_archive.patterns)
            }
        }
