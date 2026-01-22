"""
Chat/Greeting module for JARVIS
Handles casual conversations and greetings
"""

GREETINGS = {
    "hi": "Hey! How can I help you?",
    "hello": "Hello! What do you need?",
    "hey": "Hey there! What's up?",
    "sup": "Yo! What's going on?",
    "whats up": "Not much! What can I do for you?",
    "how are you": "I'm doing great! How about you?",
    "thanks": "You're welcome! Anything else?",
    "thank you": "Happy to help! Need anything else?",
    "good morning": "Good morning! Let's get productive!",
    "good afternoon": "Good afternoon! What can I help with?",
    "good evening": "Good evening! What do you need?",
    "good night": "Good night! See you later!",
    "bye": "Goodbye! See you soon!",
    "goodbye": "Bye! Take care!",
    "see you": "See you later!",
    "later": "Catch you later!",
}

SMALL_TALK = {
    "how are you": "I'm doing great! Ready to help with anything.",
    "what are you": "I'm JARVIS, your AI assistant. I help you with commands, files, apps, and knowledge!",
    "who are you": "I'm JARVIS - your personal AI assistant. I can help with almost anything!",
    "what can you do": "I can open apps, files, run commands, and answer questions. Just ask!",
}


def is_greeting(text):
    """Check if text is a greeting"""
    text_lower = text.lower().strip()
    return text_lower in GREETINGS


def is_small_talk(text):
    """Check if text is small talk"""
    text_lower = text.lower().strip()
    for phrase in SMALL_TALK:
        if phrase in text_lower:
            return True
    return False


def get_greeting_response(text):
    """Get response for greeting"""
    text_lower = text.lower().strip()
    return GREETINGS.get(text_lower, "Hey! How can I help?")


def get_small_talk_response(text):
    """Get response for small talk"""
    text_lower = text.lower().strip()
    for phrase in SMALL_TALK:
        if phrase in text_lower:
            return SMALL_TALK[phrase]
    return "I'm not sure how to respond to that. What can I help you with?"
