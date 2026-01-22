"""
Machine Learning-Based Intent Detection
Lightweight ML model for command classification using keyword features
"""

import json
import os
from collections import Counter


class MLIntentDetector:
    """
    Lightweight ML-based intent classifier
    Uses keyword frequency and pattern matching to classify commands
    No external ML libraries required - pure Python implementation
    """
    
    def __init__(self):
        self.intent_keywords = {
            "system": {
                "keywords": ["ls", "dir", "list", "pwd", "cd", "cls", "clear", "show", "files", "directory"],
                "weight": 1.0
            },
            "open_app": {
                "keywords": ["open", "launch", "run", "start", "execute", "chrome", "firefox", "vscode", "notepad", "teams", "edge"],
                "weight": 1.0
            },
            "open_file": {
                "keywords": ["open", "show", "view", "read", "edit", ".py", ".txt", ".md", ".yaml", ".json"],
                "weight": 1.0
            },
            "system_control": {
                "keywords": ["volume", "brightness", "mute", "bluetooth", "wifi", "lock", "sleep", "shutdown", "restart", "power"],
                "weight": 1.0
            },
            "knowledge": {
                "keywords": ["what", "why", "how", "tell", "explain", "is", "are", "define", "learn", "google", "search"],
                "weight": 1.0
            },
            "chat": {
                "keywords": ["hello", "hi", "hey", "thanks", "thank", "bye", "goodbye", "how are you", "who are you", "what are you"],
                "weight": 1.0
            },
            "system_control_connect": {
                "keywords": ["connect", "pair", "link", "bluetooth", "device", "wifi", "network"],
                "weight": 1.0
            }
        }
        
        self.model_path = "ai/ml_model.json"
        self.load_model()
    
    def extract_features(self, command):
        """Extract features from command for ML classification"""
        cmd_lower = command.lower().strip()
        words = cmd_lower.split()
        
        features = {
            "word_count": len(words),
            "has_dots": "." in cmd_lower,
            "has_special_chars": any(c in cmd_lower for c in [":", "\\", "/"]),
            "first_word": words[0] if words else "",
            "keywords_present": {}
        }
        
        # Count keyword occurrences for each intent
        for intent, data in self.intent_keywords.items():
            keyword_count = sum(1 for keyword in data["keywords"] if keyword in cmd_lower)
            features["keywords_present"][intent] = keyword_count
        
        return features
    
    def predict_intent(self, command):
        """
        Predict intent using keyword-based ML classification
        Returns (predicted_intent, confidence_score)
        """
        features = self.extract_features(command)
        cmd_lower = command.lower().strip()
        
        # Score each intent
        intent_scores = {}
        
        for intent, data in self.intent_keywords.items():
            score = 0
            keyword_count = features["keywords_present"].get(intent, 0)
            
            # Higher score for more keywords matched
            score += keyword_count * 10
            
            # Specific patterns boost
            if intent == "open_file" and features["has_dots"]:
                score += 20
            
            if intent == "system_control_connect" and any(x in cmd_lower for x in ["connect", "pair"]):
                score += 15
            
            if intent == "system" and any(x in cmd_lower for x in ["ls", "dir", "pwd", "cd", "list"]):
                score += 15
            
            if intent == "open_app" and any(x in cmd_lower for x in ["chrome", "vscode", "firefox", "edge", "teams"]):
                score += 15
            
            if intent == "knowledge" and any(x in cmd_lower for x in ["what", "how", "why", "explain"]):
                score += 15
            
            if intent == "chat" and any(x in cmd_lower for x in ["hello", "hi", "hey", "thanks", "bye"]):
                score += 20
            
            intent_scores[intent] = score
        
        # Find best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return "unknown", 0.0
        
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]
        
        # Normalize to 0-100 confidence
        max_possible_score = 100
        confidence = min((best_score / max_possible_score) * 100, 100.0)
        
        return best_intent, confidence
    
    def train_on_commands(self, commands_data):
        """
        Train on a dataset of commands for better classification
        commands_data: list of {"command": str, "intent": str}
        """
        # Update keyword weights based on training data
        intent_command_map = {}
        
        for item in commands_data:
            intent = item.get("intent")
            command = item.get("command", "").lower()
            
            if intent not in intent_command_map:
                intent_command_map[intent] = []
            
            intent_command_map[intent].append(command)
        
        # Boost weights for intents with training data
        for intent, commands in intent_command_map.items():
            if intent in self.intent_keywords:
                self.intent_keywords[intent]["weight"] *= 1.1
        
        self.save_model()
    
    def save_model(self):
        """Save trained model to file"""
        try:
            model_data = {
                "intent_keywords": self.intent_keywords
            }
            with open(self.model_path, 'w') as f:
                json.dump(model_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save model: {e}")
    
    def load_model(self):
        """Load trained model from file if exists"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'r') as f:
                    model_data = json.load(f)
                    self.intent_keywords = model_data.get("intent_keywords", self.intent_keywords)
        except Exception as e:
            print(f"Warning: Could not load model, using defaults: {e}")


# Global ML detector instance
ml_detector = MLIntentDetector()


def detect_intent(command):
    """
    Use ML to detect command intent
    Returns dict with intent and confidence
    """
    intent, confidence = ml_detector.predict_intent(command)
    return {
        "intent": intent,
        "confidence": confidence,
        "source": "ml"
    }


def train_ml_model(commands_data):
    """Train the ML model on command data"""
    ml_detector.train_on_commands(commands_data)
