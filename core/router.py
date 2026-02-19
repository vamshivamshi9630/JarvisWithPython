"""
Router: Input Classification

Routes user input into 4 categories to prevent unnecessary LLM calls:
1. "structured_direct" - Multi-step commands with direct verbs (no LLM)
2. "direct_action" - Single direct command (no LLM)
3. "goal" - Abstract request (requires LLM)
4. "chat" - Simple greeting (no tools)

This is the FIRST gate in the orchestrator.
"""

import logging

logger = logging.getLogger(__name__)

# Import memory store for learned phrase mappings
try:
    from core.memory_store import get_memory_store
    MEMORY_STORE = get_memory_store()
except Exception as e:
    logger.debug(f"Memory store not available: {e}")
    MEMORY_STORE = None


class Router:
    """Input router for JARVIS agent"""
    
    # Direct action verbs (can execute without LLM)
    DIRECT_VERBS = [
        "open", "close", "mute", "unmute",
        "play", "pause", "stop",
        "shutdown", "restart",
        "volume", "lock",
        "search", "go to",
        "check", "delete", "create", "list", "show",
        "increase", "decrease", "set", "get",
        "kill", "run", "clear", "copy", "move",
        "rename", "copy", "ping", "restart",
        "toggle", "enable", "disable"
    ]
    
    # Connectors indicating multi-step commands
    CONNECTORS = [" and ", " then ", ",", "&&"]
    
    # Abstract words requiring LLM reasoning
    ABSTRACT_WORDS = [
        "plan", "build",
        "analyze", "figure out",
        "organize", "automate",
        "summarize", "explain",
        "help me", "how to", "teach me"
    ]
    
    # Chat responses - simple greetings (no tools)
    CHAT_PATTERNS = {
        "hi": "Hello! How can I help you?",
        "hello": "Hello! How can I help you?",
        "hey": "Hey! What can I do for you?",
        "how are you": "I'm working perfectly offline!",
        "thanks": "You're welcome!",
        "thank you": "You're welcome!",
        "ok": "Got it!",
        "okay": "Got it!",
    }
    
    # System info keywords - quick info queries and control keywords
    SYSTEM_INFO_KEYWORDS = {
        # Info queries
        "battery": "get_battery",
        "ram": "get_ram_usage",
        "memory": "get_ram_usage",
        "cpu": "get_cpu_usage",
        "disk": "get_disk_usage",
        "temperature": "get_cpu_temp",
        "temp": "get_cpu_temp",
        "boot": "get_boot_time",
        "ip": "get_ip",
        "wifi": "get_wifi_name",
        "processes": "list_processes",
        "internet": "check_internet",
        "speed": "speed_test",
        "disk space": "get_disk_usage",
        
        # Control keywords
        "brightness": "set_brightness",
        "volume": "set_volume",
    }
    
    # Direct actions - map input directly to tool calls
    DIRECT_ACTIONS = {
        "open notepad": ("open_application", {"app_name": "notepad"}),
        "open chrome": ("open_application", {"app_name": "chrome"}),
        "open firefox": ("open_application", {"app_name": "firefox"}),
        "open vscode": ("open_application", {"app_name": "vscode"}),
        "open vs code": ("open_application", {"app_name": "vscode"}),
        "open file explorer": ("open_application", {"app_name": "explorer"}),
        "open explorer": ("open_application", {"app_name": "explorer"}),
        "lock screen": ("lock_screen", {}),
        "lock": ("lock_screen", {}),
        "mute": ("mute", {}),
        "unmute": ("unmute", {}),
        "volume up": ("increase_volume", {"step": 5}),
        "volume down": ("decrease_volume", {"step": 5}),
        "brightness up": ("increase_brightness", {"step": 10}),
        "brightness down": ("decrease_brightness", {"step": 10}),
        "clear temp": ("clear_temp", {}),
        "get ip": ("get_ip", {}),
        "check internet": ("check_internet", {}),
        "get battery": ("get_battery", {}),
        "get ram": ("get_ram_usage", {}),
        "get cpu": ("get_cpu_usage", {}),
        "get disk": ("get_disk_usage", {}),
        "list processes": ("list_processes", {}),
        "show processes": ("list_processes", {}),
    }

    @staticmethod
    def classify(text: str) -> str:
        """
        Classify input to prevent unnecessary LLM calls.
        
        Returns:
        "structured_direct" - Multi-step with direct verbs (parse, don't plan)
        "direct_action" - Single direct command (execute, don't plan)
        "goal" - Abstract request (use LLM planner)
        "chat" - Simple greeting (respond, no tools)

        """
        text_lower = text.lower().strip()
        
        # Check for learned phrase mappings (self-learning memory)
        if MEMORY_STORE:
            learned_mapping = MEMORY_STORE.find_phrase_mapping(text_lower)
            if learned_mapping and learned_mapping.get("confidence", 0) > 0.6:
                logger.debug(f"Route: direct_action (learned mapping, confidence: {learned_mapping.get('confidence')})")
                return "direct_action"
        
        # Check for exact chat matches first
        if text_lower in Router.CHAT_PATTERNS:
            logger.debug("Route: chat (exact match)")
            return "chat"
        
        # Check for exact direct action matches
        if text_lower in Router.DIRECT_ACTIONS:
            logger.debug("Route: direct_action (exact match)")
            return "direct_action"
        
        # Check for system info keywords (battery, cpu, ram, disk, ip, etc.)
        for keyword in Router.SYSTEM_INFO_KEYWORDS.keys():
            if keyword in text_lower:
                logger.debug(f"Route: direct_action (system info keyword: {keyword})")
                return "direct_action"
        
        # Check for "is X running?" pattern
        if "running" in text_lower or ("is " in text_lower and "?" in text_lower):
            logger.debug("Route: direct_action (running/is question)")
            return "direct_action"
        
        # Check for structured multi-step with direct verbs
        has_connector = any(conn in text_lower for conn in Router.CONNECTORS)
        has_direct_verb = any(verb in text_lower for verb in Router.DIRECT_VERBS)
        
        if has_connector and has_direct_verb:
            logger.debug("Route: structured_direct (connector + verb)")
            return "structured_direct"
        
        # Check for single direct action (starts with verb)
        if any(text_lower.startswith(verb) for verb in Router.DIRECT_VERBS):
            logger.debug("Route: direct_action (starts with verb)")
            return "direct_action"
        
        # Check for abstract goal (contains abstract words)
        has_abstract_word = any(word in text_lower for word in Router.ABSTRACT_WORDS)
        
        if has_abstract_word:
            logger.debug("Route: goal (abstract words)")
            return "goal"
        
        # Default to chat for unknown input
        logger.debug("Route: chat (default)")
        return "chat"

    @staticmethod
    def get_chat_response(text: str) -> str:
        """Get response for chat input"""
        from skills.chat import is_greeting, get_greeting_response, is_small_talk, get_small_talk_response
        
        text_lower = text.lower().strip()
        
        # Check exact match first
        if text_lower in Router.CHAT_PATTERNS:
            return Router.CHAT_PATTERNS[text_lower]
        
        # Check greetings with fuzzy match
        if is_greeting(text):
            return get_greeting_response(text)
        
        # Check small talk
        if is_small_talk(text):
            return get_small_talk_response(text)
        
        # Default
        return "I'm not sure about that. Can you rephrase?"

    @staticmethod
    def get_direct_action(text: str) -> tuple:
        """
        Get tool name and params for direct action.
        
        Handles:
        - Hardcoded actions
        - Dynamic app patterns (open X, close X)
        - System info queries (battery, ram, cpu, etc.)
        - File operations
        - Network queries
        """
        text_lower = text.lower().strip()
        
        # Check hardcoded actions first
        if text_lower in Router.DIRECT_ACTIONS:
            return Router.DIRECT_ACTIONS[text_lower]
        
        # Check learned phrase mappings (self-learning memory)
        if MEMORY_STORE:
            learned_mapping = MEMORY_STORE.find_phrase_mapping(text_lower)
            if learned_mapping:
                action = learned_mapping.get("action")
                parameters = learned_mapping.get("parameters", {})
                if action:
                    logger.debug(f"Using learned mapping for: {text_lower} -> {action}")
                    return (action, parameters)
        
        # ===== SYSTEM INFO QUERIES =====
        # "battery entha?", "battery status?", "check battery"
        for keyword, tool in Router.SYSTEM_INFO_KEYWORDS.items():
            if keyword in text_lower:
                return (tool, {})
        
        # ===== APP CONTROL =====
        # "open X"
        if text_lower.startswith("open "):
            app_name = text_lower.replace("open ", "", 1).strip()
            return ("open_application", {"app_name": app_name})
        
        # "close X"
        if text_lower.startswith("close "):
            app_name = text_lower.replace("close ", "", 1).strip()
            return ("close_application", {"app_name": app_name})
        
        # "kill X" (process)
        if text_lower.startswith("kill "):
            process_name = text_lower.replace("kill ", "", 1).strip()
            return ("kill_process", {"name": process_name, "force": True})
        
        # ===== VOLUME & BRIGHTNESS =====
        # "volume 50", "set volume to 60"
        if "volume" in text_lower:
            if any(x in text_lower for x in ["up", "increase", "higher"]):
                return ("increase_volume", {"step": 5})
            elif any(x in text_lower for x in ["down", "decrease", "lower"]):
                return ("decrease_volume", {"step": 5})
            elif any(char.isdigit() for char in text_lower):
                # Extract number
                import re
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    return ("set_volume", {"level": int(numbers[0])})
        
        # "brightness 50", "brightness up"
        if "brightness" in text_lower:
            if any(x in text_lower for x in ["up", "increase", "higher"]):
                return ("increase_brightness", {"step": 10})
            elif any(x in text_lower for x in ["down", "decrease", "lower"]):
                return ("decrease_brightness", {"step": 10})
            elif any(char.isdigit() for char in text_lower):
                import re
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    return ("set_brightness", {"level": int(numbers[0])})
        
        # ===== FILE OPERATIONS =====
        # "create file X", "create X.txt"
        if text_lower.startswith("create file ") or text_lower.startswith("new file "):
            filename = text_lower.replace("create file ", "").replace("new file ", "", 1).strip()
            return ("create_file", {"path": filename, "content": ""})
        
        # "delete file X"
        if text_lower.startswith("delete file ") or text_lower.startswith("delete "):
            filename = text_lower.replace("delete file ", "").replace("delete ", "", 1).strip()
            return ("delete_file", {"path": filename})
        
        # "list files X", "show files"
        if any(x in text_lower for x in ["list files", "show files", "files in"]):
            folder = "."
            if " in " in text_lower:
                folder = text_lower.split(" in ")[-1].strip()
            return ("list_files", {"folder": folder})
        
        # "search files X"
        if text_lower.startswith("search ") or text_lower.startswith("find "):
            pattern = text_lower.replace("search ", "").replace("find ", "", 1).strip()
            return ("search_files", {"folder": ".", "pattern": pattern})
        
        # ===== NETWORK =====
        # "ping X"
        if text_lower.startswith("ping "):
            website = text_lower.replace("ping ", "", 1).strip()
            return ("ping", {"website": website})
        
        # ===== PROCESS MONITORING =====
        # "is X running?", "check if X running"
        if "running" in text_lower:
            import re
            words = text_lower.split()
            if len(words) > 1:
                app_name = ' '.join(w for w in words if w not in ["is", "running", "check", "if"])
                return ("check_running", {"app_name": app_name})
        
        # "find process X"
        if text_lower.startswith("find process "):
            process_name = text_lower.replace("find process ", "", 1).strip()
            return ("find_process", {"name": process_name})
        
        # No match found
        return None

