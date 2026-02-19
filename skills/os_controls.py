"""
OS-Level Controls - Keyboard and Mouse Automation

Handles:
- Typing text
- Pressing keys
- Mouse movements
- Window focus

Uses pyautogui for cross-platform keyboard/mouse control.
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class OSControls:
    """
    OS-level keyboard and mouse control.
    
    Provides direct control of keyboard and mouse for automation.
    """
    
    def __init__(self):
        """Initialize OS controls"""
        try:
            import pyautogui
            self.pyautogui = pyautogui
            # Disable safety features for faster operation
            self.pyautogui.FAILSAFE = False
            self.pyautogui.PAUSE = 0.1
        except ImportError:
            logger.warning("pyautogui not installed. Keyboard/mouse control unavailable.")
            self.pyautogui = None
    
    def type_text(self, text: str, interval: float = 0.05) -> str:
        """
        Type text character by character.
        
        Args:
            text: Text to type
            interval: Time between key presses (seconds)
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            # Small delay before typing
            time.sleep(0.5)
            
            # Type each character
            for char in text:
                self.pyautogui.write(char)
                time.sleep(interval)
            
            logger.info(f"Typed: {text[:50]}...")
            return f"Typed: {text}"
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return f"Failed to type: {e}"
    
    def press_key(self, key: str) -> str:
        """
        Press a single key.
        
        Args:
            key: Key name ("enter", "tab", "escape", etc)
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            # Map common key names
            key_map = {
                "enter": "return",
                "return": "return",
                "tab": "tab",
                "space": "space",
                "backspace": "backspace",
                "delete": "delete",
                "escape": "esc",
                "esc": "esc",
                "ctrl": "ctrl",
                "shift": "shift",
                "alt": "alt",
                "left": "left",
                "right": "right",
                "up": "up",
                "down": "down",
                "home": "home",
                "end": "end",
                "pageup": "pageup",
                "pagedown": "pagedown",
            }
            
            key_lower = key.lower().strip()
            actual_key = key_map.get(key_lower, key_lower)
            
            self.pyautogui.press(actual_key)
            
            logger.info(f"Pressed key: {actual_key}")
            return f"Pressed: {actual_key}"
            
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return f"Failed to press key: {e}"
    
    def hotkey(self, *keys: str) -> str:
        """
        Press multiple keys simultaneously (hotkey).
        
        Args:
            keys: Keys to press together ("ctrl", "c")
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            self.pyautogui.hotkey(*keys)
            logger.info(f"Hotkey: {'+'.join(keys)}")
            return f"Pressed hotkey: {'+'.join(keys)}"
            
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            return f"Failed to press hotkey: {e}"
    
    def move_mouse(self, x: int, y: int, duration: float = 0.5) -> str:
        """
        Move mouse to coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to take for movement
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            self.pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Mouse moved to: {x}, {y}")
            return f"Mouse moved to ({x}, {y})"
            
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return f"Failed to move mouse: {e}"
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = "left") -> str:
        """
        Click at coordinates.
        
        Args:
            x: X coordinate (current position if None)
            y: Y coordinate (current position if None)
            button: "left", "right", or "middle"
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            if x is not None and y is not None:
                self.pyautogui.click(x, y, button=button)
                logger.info(f"Clicked at ({x}, {y})")
                return f"Clicked at ({x}, {y})"
            else:
                self.pyautogui.click(button=button)
                logger.info(f"Clicked (current position)")
                return f"Clicked (current position)"
            
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return f"Failed to click: {e}"
    
    def double_click(self, x: Optional[int] = None, 
                    y: Optional[int] = None) -> str:
        """
        Double-click at coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Status message
        """
        if not self.pyautogui:
            return "pyautogui not installed"
        
        try:
            if x is not None and y is not None:
                self.pyautogui.doubleClick(x, y)
                return f"Double-clicked at ({x}, {y})"
            else:
                self.pyautogui.doubleClick()
                return "Double-clicked (current position)"
            
        except Exception as e:
            logger.error(f"Failed to double-click: {e}")
            return f"Failed to double-click: {e}"
    
    def wait(self, seconds: float) -> str:
        """
        Wait for specified time.
        
        Args:
            seconds: Time to wait
            
        Returns:
            Status message
        """
        try:
            time.sleep(seconds)
            logger.debug(f"Waited {seconds} seconds")
            return f"Waited {seconds} seconds"
        except Exception as e:
            return f"Failed to wait: {e}"


# Global OS controls instance
_os_controls = None


def get_os_controls() -> OSControls:
    """Get or create global OS controls instance"""
    global _os_controls
    if _os_controls is None:
        _os_controls = OSControls()
    return _os_controls
