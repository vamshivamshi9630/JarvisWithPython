"""
Self-Learning Memory Store - Enables JARVIS to learn from experience

Features:
1. User Preferences & Patterns - How the user likes to do things
2. Tool Effectiveness - Which tools work best for different tasks
3. Learned Phrase Mappings - User language patterns to actions
4. Dual persistence: JSON (fast, human-readable) + SQLite (queryable, structured)
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryStore:
    """
    Self-learning memory system for JARVIS.
    
    Tracks:
    - User preferences and behavior patterns
    - Tool execution outcomes and effectiveness
    - Learned mappings between user phrases and optimal actions
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize the memory store.
        
        Args:
            storage_dir: Directory for JSON and SQLite files (default: ./memory/)
        """
        self.storage_dir = Path(storage_dir or "./memory")
        self.storage_dir.mkdir(exist_ok=True)
        
        self.json_file = self.storage_dir / "memories.json"
        self.db_file = self.storage_dir / "memories.db"
        
        # Load or initialize JSON storage
        self.memories = self._load_json()
        
        # Initialize SQLite
        self._init_database()
        
        logger.debug(f"Memory store initialized at {self.storage_dir}")
    
    # ==================== JSON PERSISTENCE ====================
    
    def _load_json(self) -> Dict[str, Any]:
        """Load memories from JSON file"""
        if self.json_file.exists():
            try:
                with open(self.json_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load JSON memories: {e}")
        
        # Initialize default structure
        return {
            "user_preferences": {},
            "behavior_patterns": defaultdict(list),
            "tool_outcomes": defaultdict(list),
            "phrase_mappings": {},
            "last_updated": datetime.now().isoformat(),
        }
    
    def _save_json(self):
        """Save memories to JSON file"""
        try:
            self.memories["last_updated"] = datetime.now().isoformat()
            with open(self.json_file, 'w') as f:
                json.dump(self.memories, f, indent=2, default=str)
            logger.debug("Memories saved to JSON")
        except Exception as e:
            logger.error(f"Failed to save JSON memories: {e}")
    
    # ==================== SQLITE PERSISTENCE ====================
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Behavior patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS behavior_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    occurrence_count INTEGER DEFAULT 1,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tool outcomes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_name TEXT,
                    task_type TEXT,
                    parameters TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Phrase mappings table (learned language patterns)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phrase_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_phrase TEXT UNIQUE,
                    action TEXT,
                    parameters TEXT,
                    confidence REAL DEFAULT 0.5,
                    usage_count INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.5,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.debug("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    # ==================== USER PREFERENCES ====================
    
    def learn_preference(self, key: str, value: Any):
        """
        Learn and store a user preference.
        
        Args:
            key: Preference key (e.g., "preferred_browser")
            value: Preference value (e.g., "Chrome")
        """
        # JSON storage
        if "user_preferences" not in self.memories:
            self.memories["user_preferences"] = {}
        self.memories["user_preferences"][key] = {
            "value": value,
            "learned_at": datetime.now().isoformat(),
        }
        self._save_json()
        
        # SQLite storage
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences (key, value, frequency, last_updated)
                VALUES (?, ?, COALESCE((SELECT frequency FROM user_preferences WHERE key = ?), 0) + 1, CURRENT_TIMESTAMP)
            """, (key, json.dumps(value), key))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store preference in DB: {e}")
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Retrieve a learned user preference"""
        if "user_preferences" in self.memories and key in self.memories["user_preferences"]:
            try:
                return self.memories["user_preferences"][key]["value"]
            except:
                pass
        
        # Try SQLite as fallback
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return json.loads(result[0])
        except Exception as e:
            logger.debug(f"Failed to retrieve preference from DB: {e}")
        
        return None
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all learned preferences"""
        prefs = {}
        if "user_preferences" in self.memories:
            for key, data in self.memories["user_preferences"].items():
                prefs[key] = data.get("value")
        return prefs
    
    # ==================== BEHAVIOR PATTERNS ====================
    
    def record_action_sequence(self, sequence_name: str, actions: List[str]):
        """
        Record a sequence of actions the user frequently performs.
        
        Args:
            sequence_name: Name of the sequence (e.g., "morning_routine")
            actions: List of action names in order
        """
        if "behavior_patterns" not in self.memories:
            self.memories["behavior_patterns"] = {}
        
        if sequence_name not in self.memories["behavior_patterns"]:
            self.memories["behavior_patterns"][sequence_name] = []
        
        self.memories["behavior_patterns"][sequence_name].append({
            "actions": actions,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_json()
        
        # SQLite storage
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO behavior_patterns (pattern_type, pattern_data, occurrence_count, last_seen)
                VALUES (?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(rowid) DO UPDATE SET occurrence_count = occurrence_count + 1, last_seen = CURRENT_TIMESTAMP
            """, (sequence_name, json.dumps(actions)))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store pattern in DB: {e}")
    
    def get_action_patterns(self, count: int = 5) -> Dict[str, List[Any]]:
        """Get learned behavior patterns"""
        patterns = {}
        if "behavior_patterns" in self.memories:
            for pattern_name, occurrences in self.memories["behavior_patterns"].items():
                patterns[pattern_name] = occurrences[-count:] if occurrences else []
        return patterns
    
    # ==================== TOOL EFFECTIVENESS ====================
    
    def record_tool_outcome(self, tool_name: str, task_type: str, 
                           parameters: Dict[str, Any], success: bool, 
                           execution_time: float = 0.0):
        """
        Record the outcome of a tool execution for learning effectiveness.
        
        Args:
            tool_name: Name of the tool executed
            task_type: Type of task (e.g., "file_open", "app_launch")
            parameters: Parameters used
            success: Whether execution succeeded
            execution_time: Time taken to execute (seconds)
        """
        if "tool_outcomes" not in self.memories:
            self.memories["tool_outcomes"] = defaultdict(list)
        
        outcome = {
            "tool": tool_name,
            "task_type": task_type,
            "parameters": parameters,
            "success": success,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat(),
        }
        self.memories["tool_outcomes"][tool_name].append(outcome)
        self._save_json()
        
        # SQLite storage
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tool_outcomes 
                (tool_name, task_type, parameters, success, execution_time)
                VALUES (?, ?, ?, ?, ?)
            """, (tool_name, task_type, json.dumps(parameters), success, execution_time))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store tool outcome in DB: {e}")
    
    def get_tool_effectiveness(self, tool_name: str) -> Dict[str, Any]:
        """
        Analyze effectiveness of a tool across all uses.
        
        Returns:
            {
                "total_uses": int,
                "success_rate": float (0-1),
                "avg_execution_time": float,
                "task_types": {task_type: success_rate}
            }
        """
        outcomes = self.memories.get("tool_outcomes", {}).get(tool_name, [])
        
        if not outcomes:
            return {
                "total_uses": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "task_types": {},
            }
        
        total = len(outcomes)
        successes = sum(1 for o in outcomes if o.get("success", False))
        avg_time = sum(o.get("execution_time", 0) for o in outcomes) / total if total > 0 else 0
        
        # Breakdown by task type
        task_breakdown = defaultdict(lambda: {"success": 0, "total": 0})
        for outcome in outcomes:
            task_type = outcome.get("task_type", "unknown")
            task_breakdown[task_type]["total"] += 1
            if outcome.get("success"):
                task_breakdown[task_type]["success"] += 1
        
        task_types = {
            task_type: task_data["success"] / task_data["total"]
            for task_type, task_data in task_breakdown.items()
        }
        
        return {
            "total_uses": total,
            "success_rate": successes / total,
            "avg_execution_time": avg_time,
            "task_types": task_types,
        }
    
    # ==================== PHRASE MAPPINGS (Learned Language) ====================
    
    def learn_phrase_mapping(self, user_phrase: str, action: str, 
                            parameters: Dict[str, Any] = None, confidence: float = 0.7):
        """
        Learn a mapping between user language and action/tool.
        
        Example:
            "open my downloads folder" -> action="open_folder", parameters={"path": "~/Downloads"}
        
        Args:
            user_phrase: Natural language phrase (normalized)
            action: Action or tool to execute
            parameters: Parameters for the action
            confidence: Confidence in the mapping (0-1)
        """
        if "phrase_mappings" not in self.memories:
            self.memories["phrase_mappings"] = {}
        
        self.memories["phrase_mappings"][user_phrase] = {
            "action": action,
            "parameters": parameters or {},
            "confidence": confidence,
            "learned_at": datetime.now().isoformat(),
        }
        self._save_json()
        
        # SQLite storage
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO phrase_mappings 
                (user_phrase, action, parameters, confidence, usage_count, last_used)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT usage_count FROM phrase_mappings WHERE user_phrase = ?), 0) + 1,
                    CURRENT_TIMESTAMP)
            """, (user_phrase, action, json.dumps(parameters or {}), confidence, user_phrase))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store phrase mapping in DB: {e}")
    
    def find_phrase_mapping(self, user_phrase: str) -> Optional[Dict[str, Any]]:
        """
        Find a learned phrase mapping.
        
        Returns:
            {"action": str, "parameters": dict, "confidence": float} or None
        """
        if "phrase_mappings" in self.memories and user_phrase in self.memories["phrase_mappings"]:
            mapping = self.memories["phrase_mappings"][user_phrase]
            return {
                "action": mapping.get("action"),
                "parameters": mapping.get("parameters", {}),
                "confidence": mapping.get("confidence", 0.5),
            }
        return None
    
    def get_high_confidence_mappings(self, min_confidence: float = 0.8) -> Dict[str, Dict[str, Any]]:
        """Get all learned phrase mappings above a confidence threshold"""
        if "phrase_mappings" not in self.memories:
            return {}
        
        return {
            phrase: mapping
            for phrase, mapping in self.memories["phrase_mappings"].items()
            if mapping.get("confidence", 0) >= min_confidence
        }
    
    # ==================== LEARNING FROM EXECUTION ====================
    
    def learn_from_execution(self, user_input: str, action: str, 
                            parameters: Dict[str, Any], success: bool,
                            execution_time: float = 0.0):
        """
        Automatically learn from a successful execution.
        
        Args:
            user_input: Original user input
            action: Action that was executed
            parameters: Parameters used
            success: Whether it succeeded
            execution_time: Time taken
        """
        # Record tool outcome for effectiveness tracking
        self.record_tool_outcome(action, "user_request", parameters, success, execution_time)
        
        # If successful, try to learn the phrase mapping
        if success:
            # Normalize phrase (lowercase, strip extra whitespace)
            normalized_phrase = user_input.lower().strip()
            
            # Find existing confidence or start with moderate confidence
            existing = self.find_phrase_mapping(normalized_phrase)
            new_confidence = min(0.99, (existing.get("confidence", 0.5) + 0.2) if existing else 0.7)
            
            self.learn_phrase_mapping(
                normalized_phrase,
                action,
                parameters,
                confidence=new_confidence
            )
    
    # ==================== MEMORY STATISTICS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about learned memories"""
        return {
            "preferences_count": len(self.memories.get("user_preferences", {})),
            "patterns_count": len(self.memories.get("behavior_patterns", {})),
            "phrase_mappings_count": len(self.memories.get("phrase_mappings", {})),
            "tool_outcomes_count": sum(
                len(outcomes) 
                for outcomes in self.memories.get("tool_outcomes", {}).values()
            ),
            "last_updated": self.memories.get("last_updated"),
        }
    
    def clear_memory(self):
        """Clear all learned memories (use with caution!)"""
        self.memories = {
            "user_preferences": {},
            "behavior_patterns": {},
            "tool_outcomes": {},
            "phrase_mappings": {},
            "last_updated": datetime.now().isoformat(),
        }
        self._save_json()
        
        # Clear database
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_preferences")
            cursor.execute("DELETE FROM behavior_patterns")
            cursor.execute("DELETE FROM tool_outcomes")
            cursor.execute("DELETE FROM phrase_mappings")
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
    
    def export_memories(self) -> Dict[str, Any]:
        """Export all memories as dictionary"""
        return {
            "user_preferences": self.memories.get("user_preferences", {}),
            "behavior_patterns": dict(self.memories.get("behavior_patterns", {})),
            "phrase_mappings": self.memories.get("phrase_mappings", {}),
            "tool_outcomes": dict(self.memories.get("tool_outcomes", {})),
        }


# Global memory store instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store(storage_dir: str = None) -> MemoryStore:
    """Get or create the global memory store instance"""
    global _memory_store
    if _memory_store is None:
        _memory_store = MemoryStore(storage_dir)
    return _memory_store


def reset_memory_store():
    """Reset the global memory store (for testing)"""
    global _memory_store
    _memory_store = None
