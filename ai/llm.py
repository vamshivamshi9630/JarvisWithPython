import os

def openai_answer(query):
    """Get answer from OpenAI API"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set. Set it with: export OPENAI_API_KEY='your-key'")

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI library not installed. Run: pip install openai")

    client = OpenAI(api_key=key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": query}],
            temperature=0.7,
            max_tokens=500
        )

        answer_text = response.choices[0].message.content
        print(f"🌐 {answer_text}")
        return answer_text

    except Exception as e:
        raise RuntimeError(f"OpenAI API error: {str(e)}")
