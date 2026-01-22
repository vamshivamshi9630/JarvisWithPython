"""
Natural Language Understanding (NLU) Module
Provides intelligent command parsing with fuzzy matching and context awareness
"""

from difflib import SequenceMatcher, get_close_matches
import re


class NLUEngine:
    """Natural Language Understanding engine for JARVIS"""
    
    def __init__(self):
        # Fuzzy matching threshold (0-1)
        self.similarity_threshold = 0.70
        # Typo correction threshold
        self.typo_threshold = 0.75
    
    def correct_typo(self, text, known_words, threshold=None):
        """
        Correct typos using fuzzy matching against known words
        Returns corrected word if match found, else original
        """
        if threshold is None:
            threshold = self.typo_threshold
        
        text_lower = text.lower().strip()
        
        # Use difflib to find close matches
        matches = get_close_matches(text_lower, known_words, n=1, cutoff=threshold)
        
        if matches:
            return matches[0]
        return text
    
    def fuzzy_match(self, text, options, threshold=None):
        """
        Find the best match from options using fuzzy string matching
        Returns (best_match, confidence_score)
        """
        if threshold is None:
            threshold = self.similarity_threshold
            
        best_match = None
        best_score = 0
        
        text_lower = text.lower().strip()
        
        for option in options:
            option_lower = option.lower()
            score = SequenceMatcher(None, text_lower, option_lower).ratio()
            
            if score > best_score:
                best_score = score
                best_match = option
        
        if best_score >= threshold:
            return best_match, best_score
        return None, best_score
    
    def extract_app_name(self, command):
        """
        Extract app name from command with variations support
        Examples: "open firefox", "launch chrome", "start vscode"
        """
        app_keywords = ["open", "launch", "start", "run", "execute"]
        
        cmd_lower = command.lower()
        
        # Try to find app keyword
        for keyword in app_keywords:
            if keyword in cmd_lower:
                # Extract what comes after the keyword
                parts = cmd_lower.split(keyword, 1)
                if len(parts) > 1:
                    app_name = parts[1].strip()
                    # Remove "app", "application", etc.
                    app_name = re.sub(r'\s*(app|application|program)?\s*$', '', app_name)
                    return app_name.strip()
        
        return None
    
    def extract_file_name(self, command):
        """
        Extract file name from command with variations
        Examples: "open config.yaml", "show jarvis.py", "view readme.md"
        """
        # Look for file extensions
        file_patterns = [
            r'open\s+([^\s]+\.\w+)',
            r'show\s+([^\s]+\.\w+)',
            r'view\s+([^\s]+\.\w+)',
            r'edit\s+([^\s]+\.\w+)',
            r'read\s+([^\s]+\.\w+)',
        ]
        
        cmd_lower = command.lower()
        
        for pattern in file_patterns:
            match = re.search(pattern, cmd_lower)
            if match:
                return match.group(1)
        
        return None
    
    def extract_directory(self, command):
        """
        Extract directory name from navigation commands
        Examples: "go to users", "cd desktop", "navigate to ai"
        """
        nav_keywords = ["go to", "cd", "navigate", "change to", "go into"]
        
        cmd_lower = command.lower()
        
        for keyword in nav_keywords:
            if keyword in cmd_lower:
                parts = cmd_lower.split(keyword, 1)
                if len(parts) > 1:
                    directory = parts[1].strip()
                    # Clean up
                    directory = re.sub(r'directory|folder|path|$', '', directory).strip()
                    return directory
        
        return None
    
    def extract_device_name(self, command):
        """
        Extract device name from connection commands
        Examples: "connect to airpods", "pair with mouse", "connect device samsung"
        """
        patterns = [
            r'(?:connect to|pair with|connect device)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+to|$)',
            r'(?:connect to|pair with|connect device)\s+(.+?)(?:\s+to|$)',
        ]
        
        cmd_lower = command.lower()
        
        for pattern in patterns:
            match = re.search(pattern, cmd_lower)
            if match:
                device = match.group(1).strip()
                # Remove extra words
                device = re.sub(r'\s*(device|bluetooth|to)?\s*$', '', device).strip()
                return device
        
        return None
    
    def extract_network_name(self, command):
        """
        Extract WiFi network name from connection commands
        Examples: "connect to wifi Home", "join network MyWifi"
        """
        patterns = [
            r'(?:connect to|join)\s+(?:wifi|network|internet)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+with|\s+password|$)',
            r'(?:connect to|join)\s+([^\s]+(?:\s+[^\s]+)*?)(?:\s+wifi|\s+network|$)',
        ]
        
        cmd_lower = command.lower()
        
        for pattern in patterns:
            match = re.search(pattern, cmd_lower)
            if match:
                network = match.group(1).strip()
                # Remove extra words
                network = re.sub(r'\s*(wifi|network)?\s*$', '', network).strip()
                return network
        
        return None
    
    def extract_knowledge_query(self, command):
        """
        Clean up knowledge query for better API calls
        Examples: "what is flutter" -> "flutter", "explain python" -> "python"
        """
        # Remove common question prefixes
        prefixes = [
            r'^(what\s+is|what\'s|explain|tell me|how to|show me|find|search)\s+',
            r'^(about|concerning|regarding)\s+',
        ]
        
        query = command.lower().strip()
        
        for prefix in prefixes:
            query = re.sub(prefix, '', query, flags=re.IGNORECASE)
        
        return query.strip()
    
    def calculate_intent_confidence(self, command, intent_type):
        """
        Calculate confidence score for detected intent (0-100)
        """
        cmd_lower = command.lower()
        confidence = 100
        
        # Reduce confidence for ambiguous commands
        if len(cmd_lower) < 2:
            confidence -= 30
        
        # Boost confidence for explicit keywords
        if intent_type == "system" and any(x in cmd_lower for x in ["ls", "pwd", "dir", "cd"]):
            confidence += 10
        elif intent_type == "open_app" and any(x in cmd_lower for x in ["open", "launch", "run"]):
            confidence += 10
        elif intent_type == "knowledge" and any(x in cmd_lower for x in ["what", "how", "explain"]):
            confidence += 10
        
        return min(confidence, 100)


# Global NLU instance
nlu = NLUEngine()


def understand_command(command, intent_type=None):
    """
    Enhanced command understanding with NLU
    Returns dict with parsed information and confidence score
    """
    result = {
        "original": command,
        "confidence": nlu.calculate_intent_confidence(command, intent_type),
        "parsed_data": {}
    }
    
    if intent_type == "open_app":
        app_name = nlu.extract_app_name(command)
        if app_name:
            result["parsed_data"]["app_name"] = app_name
    
    elif intent_type == "open_file":
        file_name = nlu.extract_file_name(command)
        if file_name:
            result["parsed_data"]["file_name"] = file_name
    
    elif intent_type == "system" and "cd" in command.lower():
        directory = nlu.extract_directory(command)
        if directory:
            result["parsed_data"]["directory"] = directory
    
    elif intent_type == "connect_device":
        device_name = nlu.extract_device_name(command)
        if device_name:
            result["parsed_data"]["device_name"] = device_name
    
    elif intent_type == "connect_wifi":
        network_name = nlu.extract_network_name(command)
        if network_name:
            result["parsed_data"]["network_name"] = network_name
    
    elif intent_type == "knowledge":
        query = nlu.extract_knowledge_query(command)
        result["parsed_data"]["query"] = query
    
    return result
