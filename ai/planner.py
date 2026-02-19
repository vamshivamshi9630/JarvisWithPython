"""
AI Planner - Converts natural language goals into structured action plans

Uses local LLM (TinyLlama) for offline reasoning.
This module ONLY creates plans. It does NOT execute anything.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from core.tool_registry import get_tool_registry
from ai.local_llm import get_local_llm

logger = logging.getLogger(__name__)

# Import memory store for learning and context
try:
    from core.memory_store import get_memory_store
    MEMORY_STORE = get_memory_store()
except Exception as e:
    logger.debug(f"Memory store not available: {e}")
    MEMORY_STORE = None


class Planner:
    """
    Converts user goals into structured action plans using local LLM.
    
    The thinking engine - decides WHAT and in WHAT ORDER.
    Does NOT execute anything - that's the executor's job.
    """
    
    def __init__(self, tool_registry=None):
        """
        Initialize the planner.
        
        Args:
            tool_registry: Tool registry (if None, uses global)
        """
        self.tool_registry = tool_registry or get_tool_registry()
        self.llm = get_local_llm()
    
    def plan(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Convert user input into structured action plan.
        
        Args:
            user_input: User's natural language request
            context: Current system state/context
            
        Returns:
            {"goal": str, "steps": [{"tool": str, "parameters": {...}, "reason": str}]}
        """
        # GUARD: Check if model exists before attempting to plan
        model_path = Path(__file__).parent.parent / "models" / "tinyllama.gguf"
        if not model_path.exists():
            logger.warning(f"Model not found at {model_path}")
            logger.warning("Only simple direct commands will work. Model must be restored.")
            return {"goal": "no_model", "steps": []}
        
        logger.debug(f"Planning: '{user_input}'")
        
        # Build tools description for LLM
        tools_description = self._format_tools_for_prompt()
        
        # Build context string with learned preferences
        context_str = ""
        if context:
            open_apps = context.get("open_apps", [])
            current_app = context.get("current_app", "")
            if open_apps:
                context_str = f"Currently open apps: {', '.join(open_apps)}"
            if current_app:
                context_str += f"\nCurrently focused app: {current_app}"
        
        # Add learned user preferences to context
        if MEMORY_STORE:
            prefs = MEMORY_STORE.get_all_preferences()
            if prefs:
                context_str += "\n\nUser Preferences:\n"
                for key, value in prefs.items():
                    context_str += f"- {key}: {value}\n"
        
        # Call LLM for planning
        try:
            start_time = time.time()
            response = self.llm.plan(user_input, tools_description, context_str)
            elapsed_time = time.time() - start_time
            
            print(f"[LLM TIME] {elapsed_time:.2f}s")
            logger.debug(f"[LLM TIME] Planning took {elapsed_time:.2f}s")
            
            # Safety check: if response is None or empty, return fallback
            if not response or not isinstance(response, dict):
                logger.warning(f"LLM returned invalid response")
                return {"goal": "fallback", "steps": []}
            
            # Ensure response has required fields
            if "goal" not in response:
                response["goal"] = "Execute requested task"
            if "steps" not in response:
                response["steps"] = []
            
            # Log the plan
            if response.get("steps"):
                logger.debug(f"Plan created: {len(response['steps'])} steps")
            else:
                logger.debug(f"No plan steps generated")
            
            return response
            
        except Exception as e:
            logger.debug(f"Planning error: {e}")
            # Return fallback plan instead of crashing
            return {"goal": "fallback", "steps": []}

    
    def _format_tools_for_prompt(self) -> str:
        """Format available tools for LLM prompt."""
        # Use the tool registry's built-in prompt formatter
        return self.tool_registry.get_for_prompt()



# Global instance
_planner_instance = None


def get_planner() -> Planner:
    """Get or create global planner instance."""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = Planner()
    return _planner_instance

