"""
Context Manager - Tracks AI state, open applications, and previous actions
Enables the AI to remember context and execute multi-step commands intelligently
Integrated with Long-Term Vector Memory for persistent learning.
"""

from datetime import datetime
from collections import deque
import json

# Import memory stores
try:
    from core.memory_store import get_memory_store
    MEMORY_STORE = get_memory_store()
except Exception as e:
    MEMORY_STORE = None

try:
    from core.vector_store import get_vector_store
    VECTOR_STORE = get_vector_store()
except Exception as e:
    VECTOR_STORE = None


class ContextManager:
    """Manages execution context, history, and application state"""
    
    def __init__(self, max_history=20):
        self.max_history = max_history
        self.action_history = deque(maxlen=max_history)  # Track last N actions
        self.open_apps = {}  # {app_name: (pid, open_time, window_info)}
        self.current_app = None  # Currently focused app
        self.current_directory = None  # Current working directory
        self.variables = {}  # Store extracted variables from commands
        self.session_start = datetime.now()
        self.last_action = None
        self.conversation_history = deque(maxlen=50)  # Track chat history
        
    def add_action(self, action_type, details, success=True):
        """Record an action for context tracking"""
        action = {
            "type": action_type,
            "details": details,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        self.action_history.append(action)
        self.last_action = action
        return action
    
    def add_open_app(self, app_name, pid=None, window_info=None):
        """Track opened applications"""
        self.open_apps[app_name.lower()] = {
            "pid": pid,
            "open_time": datetime.now().isoformat(),
            "window_info": window_info,
        }
        self.current_app = app_name.lower()
    
    def remove_open_app(self, app_name):
        """Remove app from tracking when closed"""
        if app_name.lower() in self.open_apps:
            del self.open_apps[app_name.lower()]
            if self.current_app == app_name.lower():
                self.current_app = None
    
    def set_current_app(self, app_name):
        """Set focus to an application"""
        app_lower = app_name.lower() if app_name else None
        if app_lower and app_lower in self.open_apps:
            self.current_app = app_lower
            return True
        return False
    
    def get_current_app(self):
        """Get the currently focused application"""
        return self.current_app
    
    def is_app_open(self, app_name):
        """Check if an app is already open"""
        return app_name.lower() in self.open_apps
    
    def get_open_apps(self):
        """Get list of open applications"""
        return list(self.open_apps.keys())
    
    def store_variable(self, key, value):
        """Store a variable for later use context"""
        self.variables[key] = {
            "value": value,
            "stored_at": datetime.now().isoformat(),
        }
    
    def get_variable(self, key):
        """Retrieve a stored variable"""
        if key in self.variables:
            return self.variables[key]["value"]
        return None
    
    def add_to_conversation(self, role, content):
        """Track conversation history for context"""
        self.conversation_history.append({
            "role": role,  # "user", "assistant", "system"
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_recent_conversation(self, count=5):
        """Get recent conversation for context"""
        recent = list(self.conversation_history)[-count:]
        return recent
    
    def get_action_history(self, count=5):
        """Get recent action history"""
        recent = list(self.action_history)[-count:]
        return recent
    
    def get_context_summary(self):
        """Generate a context summary for the AI to understand current state"""
        return {
            "current_app": self.current_app,
            "open_apps": self.get_open_apps(),
            "variables": self.variables,
            "last_action": self.last_action,
            "session_duration": str(datetime.now() - self.session_start),
            "recent_actions": self.get_action_history(3),
        }
    
    def get_context(self):
        """Alias for get_context_summary() - used by Planner"""
        return self.get_context_summary()
    
    def clear_session(self):
        """Clear session data"""
        self.action_history.clear()
        self.open_apps.clear()
        self.current_app = None
        self.variables.clear()
    
    # ==================== SELF-LEARNING METHODS ====================
    
    def learn_user_preference(self, key: str, value: str):
        """Learn and store a user preference"""
        if MEMORY_STORE:
            MEMORY_STORE.learn_preference(key, value)
    
    def learn_action_sequence(self, sequence_name: str, actions: list):
        """Learn a frequently-performed action sequence"""
        if MEMORY_STORE:
            MEMORY_STORE.record_action_sequence(sequence_name, actions)
    
    def learn_from_action(self, user_input: str, tool_name: str, parameters: dict, 
                         success: bool, execution_time: float = 0.0):
        """
        Learn from a successful action execution.
        This improves future planning by tracking what works.
        """
        if MEMORY_STORE:
            MEMORY_STORE.learn_from_execution(user_input, tool_name, parameters, success, execution_time)
    
    def get_learned_preferences(self) -> dict:
        """Get all learned user preferences"""
        if MEMORY_STORE:
            return MEMORY_STORE.get_all_preferences()
        return {}
    
    def get_memory_stats(self) -> dict:
        """Get statistics about what JARVIS has learned"""
        if MEMORY_STORE:
            return MEMORY_STORE.get_stats()
        return {}
    
    # ==================== VECTOR MEMORY METHODS ====================
    
    def teach_fact(self, fact: str) -> bool:
        """
        Teach JARVIS a permanent fact to remember.
        
        Example:
            context.teach_fact("Earth has one moon")
            
        Args:
            fact: The fact to learn
            
        Returns:
            Success status
        """
        if VECTOR_STORE:
            return VECTOR_STORE.teach_fact(fact)
        return False
    
    def teach_knowledge(self, knowledge: str) -> bool:
        """
        Teach JARVIS general knowledge.
        
        Example:
            context.teach_knowledge("Python is a programming language")
            
        Args:
            knowledge: The knowledge to learn
            
        Returns:
            Success status
        """
        if VECTOR_STORE:
            return VECTOR_STORE.teach_knowledge(knowledge)
        return False
    
    def search_memory(self, query: str, k: int = 3) -> list:
        """
        Search long-term memory for relevant information.
        
        Args:
            query: What to search for
            k: Number of results
            
        Returns:
            List of (memory_text, similarity) tuples
        """
        if VECTOR_STORE:
            return VECTOR_STORE.search(query, k)
        return []
    
    def get_memory_context(self, query: str, k: int = 3) -> str:
        """
        Get formatted context block from memory for prompt injection.
        
        Args:
            query: What to search for
            k: Number of memories to include
            
        Returns:
            Formatted context string ready for LLM
        """
        if VECTOR_STORE:
            return VECTOR_STORE.get_context_block(query, k)
        return ""
    
    def save_memory(self) -> bool:
        """Save all memories to disk"""
        if VECTOR_STORE:
            return VECTOR_STORE.save()
        return False
    
    def get_vector_memory_stats(self) -> dict:
        """Get statistics about vector memory"""
        if VECTOR_STORE:
            return VECTOR_STORE.get_stats()
        return {}


# Global context instance
context = ContextManager()
