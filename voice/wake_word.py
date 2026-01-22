def extract_command(text: str, wake_word="jarvis"):
    """
    Removes wake word if present and returns cleaned command
    """
    if not text:
        return None

    text = text.lower().strip()

    if wake_word in text:
        return text.replace(wake_word, "", 1).strip()

    return text
