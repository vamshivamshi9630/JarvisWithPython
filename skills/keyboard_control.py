"""
Keyboard and Automation Control
Handles typing, keyboard shortcuts, mouse movements, and system automation
"""

import time
import subprocess
from typing import List, Tuple


class KeyboardController:
    """Control keyboard, shortcuts, and text input"""
    
    # Keyboard shortcuts mapping
    SHORTCUTS = {
        "win+l": "rundll32.exe user32.dll,LockWorkStation",
        "screenshot": "powershell -Command 'Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.SendKeys]::SendWait(\"%{PRTSC}\")'",
        "alt+tab": "explorer",
        "ctrl+alt+delete": "taskmgr",
    }
    
    # Special keys
    SPECIAL_KEYS = {
        "enter": "ENTER",
        "tab": "TAB",
        "backspace": "BACKSPACE",
        "delete": "DELETE",
        "escape": "ESCAPE",
        "space": "SPACE",
    }
    
    @staticmethod
    def type_text(text: str, delay: float = 0.05):
        """Type text with optional character delay"""
        try:
            # Use PowerShell for more reliable text input
            # Escape special SendKeys characters: + ^ % ~ { }
            escaped_text = text
            for char in ['+', '^', '%', '~', '{', '}']:
                escaped_text = escaped_text.replace(char, '{' + char + '}')
            
            # Escape quotes for PowerShell
            escaped_text = escaped_text.replace('"', '`"')
            
            cmd = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{escaped_text}")'
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                capture_output=True,
                timeout=5
            )
            return f"✓ Typed: {text[:50]}"
        except Exception as e:
            return f"❌ Failed to type text: {str(e)}"
    
    @staticmethod
    def press_key(key: str):
        """Press a single key or key combination"""
        try:
            key_lower = key.lower().strip()
            
            # Handle special single keys
            if key_lower in KeyboardController.SPECIAL_KEYS:
                key_code = KeyboardController.SPECIAL_KEYS[key_lower]
                cmd = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{{{key_code}}}")'
            # Handle keyboard combinations like Ctrl+A, Alt+Tab
            elif "+" in key_lower:
                parts = key_lower.split("+")
                modifiers = []
                main_key = None
                
                for part in parts:
                    part = part.strip()
                    if part == "ctrl":
                        modifiers.append("^")
                    elif part == "alt":
                        modifiers.append("%")
                    elif part == "shift":
                        modifiers.append("+")
                    else:
                        main_key = part
                
                modifier_str = "".join(modifiers)
                cmd = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{modifier_str}{main_key}")'
            else:
                cmd = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{key_lower}")'
            
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                capture_output=True,
                timeout=5
            )
            return f"✓ Pressed: {key}"
        except Exception as e:
            return f"❌ Failed to press key: {str(e)}"
    
    @staticmethod
    def press_keys_sequence(keys: List[str], delay: float = 0.5):
        """Press a sequence of keys with delays between them"""
        results = []
        for key in keys:
            result = KeyboardController.press_key(key)
            results.append(result)
            time.sleep(delay)
        return "\n".join(results)
    
    @staticmethod
    def execute_shortcut(shortcut: str):
        """Execute system shortcuts"""
        shortcut_lower = shortcut.lower().strip()
        
        if shortcut_lower == "win+l":
            try:
                subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return "✓ Screen locked"
            except:
                return "❌ Failed to lock screen"
        
        elif shortcut_lower == "screenshot":
            try:
                subprocess.run(["powershell", "-Command", "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\"%{PRTSC}\")"], capture_output=True)
                return "✓ Screenshot taken"
            except:
                return "❌ Failed to take screenshot"
        
        elif shortcut_lower == "ctrl+c":
            return KeyboardController.press_key("ctrl+c")
        
        elif shortcut_lower == "ctrl+v":
            return KeyboardController.press_key("ctrl+v")
        
        elif shortcut_lower == "ctrl+a":
            return KeyboardController.press_key("ctrl+a")
        
        elif shortcut_lower == "ctrl+z":
            return KeyboardController.press_key("ctrl+z")
        
        else:
            return f"❌ Unknown shortcut: {shortcut}"


class AutomationController:
    """High-level automation sequences"""
    
    @staticmethod
    def type_and_press_enter(text: str):
        """Type text and press Enter"""
        KeyboardController.type_text(text)
        time.sleep(0.3)
        return KeyboardController.press_key("enter")
    
    @staticmethod
    def select_all_and_delete():
        """Select all and delete"""
        KeyboardController.press_key("ctrl+a")
        time.sleep(0.1)
        KeyboardController.press_key("delete")
        return "✓ Content cleared"
    
    @staticmethod
    def copy_to_clipboard(text: str):
        """Copy text to clipboard using PowerShell"""
        try:
            cmd = f"'{text}' | Set-Clipboard"
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                capture_output=True,
                timeout=5
            )
            return f"✓ Copied to clipboard: {text[:30]}"
        except Exception as e:
            return f"❌ Failed to copy: {str(e)}"
    
    @staticmethod
    def paste_from_clipboard():
        """Paste from clipboard"""
        return KeyboardController.press_key("ctrl+v")
    
    @staticmethod
    def search_and_type(search_term: str):
        """Open search dialog and search for term"""
        KeyboardController.press_key("ctrl+f")
        time.sleep(0.5)
        KeyboardController.type_text(search_term)
        return f"✓ Searched for: {search_term}"


# Export keyboard and automation controls
keyboard = KeyboardController()
automation = AutomationController()
