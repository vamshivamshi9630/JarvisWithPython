"""
Local Knowledge Base - Used as fallback when OpenAI is unavailable
Provides quick answers for specific topics
"""

LOCAL_KNOWLEDGE = {
    "flutter": {
        "default": "Flutter is a cross-platform UI framework by Google for building native applications for mobile, web, and desktop from a single codebase using the Dart language.",
        "detailed": """Flutter - Comprehensive Overview

Flutter is Google's open-source framework for building fast, beautiful, native applications.

**Key Features:**
• Cross-platform: Single codebase for iOS, Android, Web, Windows, macOS, Linux
• Hot Reload: See changes instantly without restarting the app
• Rich Widget Library: Pre-built Material Design & Cupertino widgets
• High Performance: Compiled to native code, smooth 60/120 FPS
• Strong Type Safety: Dart language with null safety

**Architecture:**
• Widget-based UI: Everything is a widget (Stateless/Stateful)
• State Management: Provider, Riverpod, BLoC, GetX patterns
• Layered Architecture: Framework, Engine, Platform channels

**Use Cases:** Mobile apps, Web applications, Desktop apps, Embedded systems

**Popular Apps:** Google Ads, Google Home, BMW app, eBay, Alibaba""",
    },
    "jarvis": {
        "default": "JARVIS is your AI Personal Assistant. I can open apps, files, run commands, and answer questions!",
    },
    "python": {
        "default": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
    },
}


def local_answer(query):
    """Get answer from local knowledge base"""
    query_lower = query.lower().strip()
    
    # Check for detailed variations
    detailed_keywords = ["detail", "explain", "comprehensive", "advanced", "in detail", "tell me more"]
    is_detailed = any(kw in query_lower for kw in detailed_keywords)
    
    # Search for matching topics
    for topic, info in LOCAL_KNOWLEDGE.items():
        if topic in query_lower:
            if is_detailed and "detailed" in info:
                answer = info["detailed"]
            else:
                answer = info.get("default", "")
            
            if answer:
                print(f"💡 {answer}")
                return answer
    
    # If nothing found in local knowledge
    raise ValueError(f"No local knowledge available for: {query}")

