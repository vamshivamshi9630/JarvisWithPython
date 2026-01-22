def answer(query):
    """
    Handle knowledge queries:
    1. Try OpenAI first (for web, general knowledge, etc.)
    2. Fall back to local knowledge only if OpenAI fails
    """
    from ai.llm import openai_answer
    from ai.local_llm import local_answer
    
    # Try OpenAI first
    try:
        result = openai_answer(query)
        # If result is None, it means the function printed directly
        return result
    except Exception as e:
        # If OpenAI fails, try local knowledge
        try:
            result = local_answer(query)
            return result
        except Exception as e2:
            # If local also fails, provide friendly message
            return f"🤔 I couldn't find information about '{query}'. Try asking more specifically or check your internet connection for OpenAI lookups."
