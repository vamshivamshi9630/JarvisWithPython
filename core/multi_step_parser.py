"""
Multi-Step Command Parser

Handles structured multi-step commands WITHOUT LLM.

Example:
  "open chrome and go to youtube and play rajasaab songs"

Splits by connectors and returns as list of steps.
This avoids unnecessary LLM calls (30-90 second delays).

NOTE: This is deterministic and dumb. It just splits text.
Executor handles actual parsing and tool selection.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MultiStepParser:
    """Parses multi-step commands into structured actions (generic version)"""

    @staticmethod
    def parse(text: str) -> List[Dict[str, Any]]:
        """
        Parse multi-step command into list of structured actions.
        
        Generic parser that handles any application and command structure.
        Supports flexible multi-step variations:
        - open notepad++ and type hlo
        - open new tab in notepad++ and type hlo
        - open chrome and go to youtube and type songs
        
        Args:
            text: User input (natural language multi-step command)
            
        Returns:
            List of action dicts with structured format
        """
        connectors = [" and ", " then ", ",", "&&"]
        text = text.lower()
        
        # Replace all connectors with pipe delimiter
        for conn in connectors:
            text = text.replace(conn, "|")
        
        raw_steps = [s.strip() for s in text.split("|") if s.strip()]
        
        structured = []
        last_app = None
        
        for step in raw_steps:
            
            # Detect application names dynamically
            if "open" in step:
                words = step.replace("open", "").strip()
                if words:
                    last_app = words
                    structured.append({
                        "action": "open_application",
                        "target": words
                    })
                    continue
            
            # Detect navigation
            if "go to" in step:
                target = step.split("go to", 1)[1].strip()
                structured.append({
                    "action": "navigate",
                    "target": target,
                    "app": last_app
                })
                continue
            
            # Detect new tab
            if "new tab" in step:
                structured.append({
                    "action": "new_tab",
                    "target": last_app
                })
                continue
            
            # Detect typing
            if "type" in step:
                typed_text = step.split("type", 1)[1].strip()
                structured.append({
                    "action": "type_text",
                    "text": typed_text,
                    "target": last_app
                })
                continue
            
            # Fallback
            structured.append({
                "action": "raw",
                "text": step,
                "target": last_app
            })
        
        return structured
