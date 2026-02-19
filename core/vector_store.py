"""
Vector Memory Store - Semantic Memory with FAISS

Maintains searchable vector embeddings of all interactions, knowledge,
and learned facts. Enables semantic search for relevant context.

Architecture:
- Text → Embedding (SentenceTransformer, 384-dim)
- Store in FAISS (fast nearest-neighbor search)
- Persist to disk (survive restart)
- Inject into prompts (enhance LLM context)
"""

import numpy as np
import pickle
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import FAISS and SentenceTransformer
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not installed. Install with: pip install faiss-cpu")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")


class MemoryEntry:
    """Single memory entry with metadata"""
    
    def __init__(self, text: str, entry_type: str = "interaction", 
                 source: str = "user", timestamp: str = None):
        """
        Args:
            text: The memory content
            entry_type: "interaction", "knowledge", "fact", "skill"
            source: Where it came from ("user", "ai", "system")
            timestamp: When it was learned (auto-set if None)
        """
        self.text = text
        self.entry_type = entry_type
        self.source = source
        self.timestamp = timestamp or datetime.now().isoformat()
        self.embedding = None  # Will be set by VectorStore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "text": self.text,
            "entry_type": self.entry_type,
            "source": self.source,
            "timestamp": self.timestamp,
        }
    
    def __repr__(self) -> str:
        return f"MemoryEntry({self.entry_type}): {self.text[:50]}..."


class VectorStore:
    """
    Vector-based memory store using FAISS and SentenceTransformer.
    
    Features:
    - Semantic search (find similar memories)
    - Persistent storage (survives restart)
    - Multiple memory types (interactions, knowledge, facts)
    - Metadata tracking (timestamps, sources)
    """
    
    def __init__(self, storage_dir: str = None, embedding_dim: int = 384):
        """
        Initialize vector store.
        
        Args:
            storage_dir: Directory for storage files (default: ./memory_vectors/)
            embedding_dim: Dimension of embeddings (default: 384 for all-MiniLM-L6-v2)
        """
        # Check dependencies
        if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.error("FAISS and sentence-transformers are required.")
            raise ImportError("Install with: pip install faiss-cpu sentence-transformers")
        
        self.storage_dir = Path(storage_dir or "./memory_vectors")
        self.storage_dir.mkdir(exist_ok=True)
        
        self.embedding_dim = embedding_dim
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # FAISS index (L2 distance - faster than cosine for this model)
        self.index: Optional[faiss.IndexFlatL2] = None
        self.entries: List[MemoryEntry] = []
        
        # Load existing memories if available
        self.load()
        
        # If no index exists, create empty one
        if self.index is None:
            self.index = faiss.IndexFlatL2(embedding_dim)
        
        logger.debug(f"VectorStore initialized at {self.storage_dir}")
    
    # ==================== MEMORY OPERATIONS ====================
    
    def add(self, text: str, entry_type: str = "interaction", source: str = "user") -> MemoryEntry:
        """
        Add text to memory with embedding.
        
        Args:
            text: Content to remember
            entry_type: "interaction", "knowledge", "fact", "skill"
            source: "user", "ai", "system"
            
        Returns:
            MemoryEntry that was added
        """
        if not text or len(text.strip()) == 0:
            logger.debug("Ignored empty memory entry")
            return None
        
        # Create entry
        entry = MemoryEntry(text, entry_type, source)
        
        # Generate embedding
        try:
            embedding = self.model.encode(text, convert_to_numpy=True).astype("float32")
            entry.embedding = embedding
        except Exception as e:
            logger.error(f"Failed to encode memory: {e}")
            return None
        
        # Add to FAISS index
        try:
            self.index.add(np.array([embedding]))
            self.entries.append(entry)
            logger.debug(f"Memory added: {entry_type} from {source}")
        except Exception as e:
            logger.error(f"Failed to add to FAISS index: {e}")
            return None
        
        return entry
    
    def search(self, query: str, k: int = 3, min_similarity: float = 0.0) -> List[Tuple[str, float]]:
        """
        Search for similar memories.
        
        Args:
            query: Search query
            k: Number of results to return
            min_similarity: Minimum similarity score (higher = more similar)
            
        Returns:
            List of (memory_text, distance) tuples
            (Lower distance = more similar)
        """
        if not query or len(self.entries) == 0:
            return []
        
        try:
            # Encode query
            query_embedding = self.model.encode(query, convert_to_numpy=True).astype("float32")
            
            # Search FAISS
            k_actual = min(k, len(self.entries))
            distances, indices = self.index.search(np.array([query_embedding]), k_actual)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.entries):
                    entry = self.entries[idx]
                    distance = distances[0][i]
                    
                    # Convert distance to similarity score (0-1, higher is better)
                    # Lower distance = higher similarity
                    similarity = 1.0 / (1.0 + distance)
                    
                    results.append((entry.text, similarity))
            
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_by_type(self, query: str, entry_type: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Search within specific memory type.
        
        Args:
            query: Search query
            entry_type: Filter by type ("interaction", "knowledge", "fact", "skill")
            k: Number of results
            
        Returns:
            Filtered search results
        """
        all_results = self.search(query, k * 2)  # Get more to filter
        
        filtered = [
            (text, sim) for text, sim in all_results
            if any(e.text == text and e.entry_type == entry_type for e in self.entries)
        ]
        
        return filtered[:k]
    
    def get_context_block(self, query: str, k: int = 3, 
                         separator: str = "\n---\n") -> str:
        """
        Get formatted context block for injection into prompts.
        
        Args:
            query: What to search for
            k: Number of memories to include
            separator: How to join memories
            
        Returns:
            Formatted string ready for prompt injection
        """
        results = self.search(query, k)
        
        if not results:
            return ""
        
        context_lines = []
        for i, (text, similarity) in enumerate(results, 1):
            # Format with similarity score
            confidence = f"{(similarity * 100):.0f}%"
            context_lines.append(f"[Memory {i} - confidence: {confidence}]\n{text}")
        
        return separator.join(context_lines)
    
    # ==================== MEMORY TYPES ====================
    
    def add_interaction(self, user_input: str, ai_response: str = None):
        """
        Record a user-AI interaction.
        
        Args:
            user_input: What user asked/did
            ai_response: What AI responded (optional)
        """
        # Store user input
        self.add(user_input, entry_type="interaction", source="user")
        
        # Store AI response if provided
        if ai_response:
            self.add(ai_response, entry_type="interaction", source="ai")
    
    def teach_fact(self, fact: str) -> bool:
        """
        Teach the system a fact it should remember.
        
        Args:
            fact: Factual information to learn
            
        Returns:
            Success status
        """
        entry = self.add(fact, entry_type="fact", source="user")
        return entry is not None
    
    def teach_knowledge(self, knowledge: str) -> bool:
        """
        Teach the system general knowledge.
        
        Args:
            knowledge: Knowledge to learn
            
        Returns:
            Success status
        """
        entry = self.add(knowledge, entry_type="knowledge", source="user")
        return entry is not None
    
    def teach_skill(self, skill_desc: str) -> bool:
        """
        Teach the system about a skill mapping.
        
        Args:
            skill_desc: Description of what the skill does
            
        Returns:
            Success status
        """
        entry = self.add(skill_desc, entry_type="skill", source="system")
        return entry is not None
    
    # ==================== PERSISTENCE ====================
    
    def save(self) -> bool:
        """
        Save memory to disk (FAISS index + metadata).
        
        Returns:
            Success status
        """
        try:
            # Save FAISS index
            index_path = self.storage_dir / "memory.index"
            faiss.write_index(self.index, str(index_path))
            logger.debug(f"FAISS index saved to {index_path}")
            
            # Save metadata (entries without embeddings to save space)
            metadata_path = self.storage_dir / "memory.pkl"
            metadata = [entry.to_dict() for entry in self.entries]
            
            with open(metadata_path, "wb") as f:
                pickle.dump(metadata, f)
            logger.debug(f"Memory metadata saved to {metadata_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
            return False
    
    def load(self) -> bool:
        """
        Load memory from disk.
        
        Returns:
            Success status
        """
        try:
            index_path = self.storage_dir / "memory.index"
            metadata_path = self.storage_dir / "memory.pkl"
            
            if not index_path.exists() or not metadata_path.exists():
                logger.debug("No existing memory to load")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            logger.debug(f"Loaded FAISS index from {index_path}")
            
            # Load metadata
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)
            
            # Reconstruct entries
            self.entries = []
            for entry_dict in metadata:
                entry = MemoryEntry(
                    text=entry_dict["text"],
                    entry_type=entry_dict.get("entry_type", "interaction"),
                    source=entry_dict.get("source", "user"),
                    timestamp=entry_dict.get("timestamp")
                )
                self.entries.append(entry)
            
            logger.debug(f"Loaded {len(self.entries)} memory entries")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return False
    
    # ==================== STATISTICS & MANAGEMENT ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        type_counts = {}
        source_counts = {}
        
        for entry in self.entries:
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
            source_counts[entry.source] = source_counts.get(entry.source, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "by_type": type_counts,
            "by_source": source_counts,
            "index_size": self.index.ntotal,
            "embedding_dimension": self.embedding_dim,
        }
    
    def clear(self) -> bool:
        """Clear all memory (WARNING: permanent!)"""
        try:
            self.entries = []
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            logger.warning("All memory cleared!")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False
    
    def export(self) -> Dict[str, Any]:
        """Export all memories as dictionary"""
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "stats": self.get_stats(),
        }
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories as list of dicts"""
        return [entry.to_dict() for entry in self.entries]
    
    def get_memories_by_type(self, entry_type: str) -> List[Dict[str, Any]]:
        """Get all memories of specific type"""
        return [
            entry.to_dict() for entry in self.entries
            if entry.entry_type == entry_type
        ]
    
    def __len__(self) -> int:
        """Number of memories stored"""
        return len(self.entries)
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"VectorStore({len(self.entries)} entries, {stats['index_size']} indexed)"


# Global instance
_vector_store: Optional[VectorStore] = None


def get_vector_store(storage_dir: str = None) -> Optional[VectorStore]:
    """Get or create global vector store instance"""
    global _vector_store
    if _vector_store is None:
        try:
            _vector_store = VectorStore(storage_dir)
        except ImportError as e:
            logger.error(f"Cannot initialize vector store: {e}")
            return None
    return _vector_store


def reset_vector_store():
    """Reset global vector store (for testing)"""
    global _vector_store
    _vector_store = None
