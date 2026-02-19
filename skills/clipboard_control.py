"""
Clipboard Control Module

Clipboard operations:
- Read clipboard
- Write to clipboard
- Monitor clipboard changes
- Clear clipboard
"""

import pyperclip
from typing import Dict, Any


def read_clipboard() -> Dict[str, Any]:
    """Read content from clipboard"""
    try:
        content = pyperclip.paste()
        return {
            "content": content,
            "length": len(content),
            "message": f"Clipboard: {content[:100]}..." if len(content) > 100 else f"Clipboard: {content}"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not read clipboard"}


def write_clipboard(text: str) -> Dict[str, Any]:
    """Write text to clipboard"""
    try:
        pyperclip.copy(text)
        return {
            "text": text,
            "length": len(text),
            "message": f"Copied {len(text)} characters to clipboard"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not write to clipboard"}


def clear_clipboard() -> Dict[str, Any]:
    """Clear clipboard"""
    try:
        pyperclip.copy("")
        return {"message": "Clipboard cleared"}
    except Exception as e:
        return {"error": str(e), "message": "Could not clear clipboard"}


def append_clipboard(text: str) -> Dict[str, Any]:
    """Append text to existing clipboard content"""
    try:
        current = pyperclip.paste()
        new_content = current + text
        pyperclip.copy(new_content)
        return {
            "appended": text,
            "total_length": len(new_content),
            "message": f"Appended to clipboard"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not append to clipboard"}


def get_clipboard_length() -> Dict[str, Any]:
    """Get clipboard content length"""
    try:
        content = pyperclip.paste()
        return {
            "length": len(content),
            "characters": len(content),
            "message": f"Clipboard has {len(content)} characters"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not get clipboard length"}
