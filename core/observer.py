"""
Observer: Environment Perception Module

Monitors system state and verifies action results.
Used by orchestrator to check if steps succeeded.
"""

import logging
import subprocess
import shutil
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class Observer:
    """
    Perceives the desktop environment and verifies action outcomes.
    
    Used by Orchestrator to:
    - Check if apps opened successfully
    - Verify URLs changed in browser
    - Detect system state changes
    - Enable replanning on failure
    """
    
    def __init__(self):
        """Initialize observer."""
        self.last_known_state = {}
    
    def get_active_window_title(self) -> str:
        """Get currently active window title."""
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -First 1 -ExpandProperty MainWindowTitle"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() or "Unknown"
        except Exception as e:
            logger.warning(f"Could not get active window: {e}")
            return "Unknown"
    
    def check_app_open(self, app_name: str) -> bool:
        """
        Check if an application is currently running.
        
        Args:
            app_name: Name of application (e.g., "chrome", "notepad", "code")
            
        Returns:
            True if app is running
        """
        try:
            # Map common names to process names
            app_map = {
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "notepad": "notepad",
                "vscode": "code",
                "code": "code",
                "explorer": "explorer",
                "word": "WINWORD",
                "excel": "EXCEL",
                "powershell": "powershell",
                "cmd": "cmd",
                "vlc": "vlc",
            }
            
            process_name = app_map.get(app_name.lower(), app_name.lower())
            
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            return process_name in result.stdout.lower()
            
        except Exception as e:
            logger.warning(f"Could not check app: {e}")
            return False
    
    def get_browser_url(self) -> Optional[str]:
        """
        Try to get current browser URL.
        
        This is a best-effort attempt and may not work in all cases.
        
        Returns:
            Current URL or None
        """
        try:
            # Try Chrome
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-Process chrome -ErrorAction SilentlyContinue | Get-Process"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                # Chrome is running, but getting exact URL is difficult
                # This is a placeholder
                return "chrome is open"
            
        except Exception:
            pass
        
        return None
    
    def take_screenshot(self, filepath: str = "screenshot.png") -> bool:
        """
        Take a screenshot of the screen.
        
        Args:
            filepath: Where to save the screenshot
            
        Returns:
            True if successful
        """
        try:
            script = f"""
            [Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
            $screen = [System.Windows.Forms.Screen]::PrimaryScreen
            $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.Point]::Empty, $screen.Bounds.Size)
            $bitmap.Save('{filepath}')
            $graphics.Dispose()
            $bitmap.Dispose()
            """
            
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=5
            )
            
            return Path(filepath).exists()
            
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            return False
    
    def get_system_state(self) -> Dict[str, Any]:
        """
        Get various system state indicators.
        
        Returns:
            Dictionary with system state info
        """
        state = {
            "active_window": self.get_active_window_title(),
            "open_apps": self._get_running_apps(),
            "time": self._get_time(),
        }
        
        return state
    
    def _get_running_apps(self) -> list:
        """Get list of running application process names."""
        try:
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            apps = []
            for line in result.stdout.split('\n'):
                if '.exe' in line:
                    app_name = line.split()[0].replace('.exe', '')
                    apps.append(app_name)
            
            return apps[:10]  # Top 10
            
        except Exception:
            return []
    
    def _get_time(self) -> str:
        """Get current time."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def verify(self, step: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if a step succeeded based on the result and system state.
        
        Args:
            step: The step that was executed
            result: The result from executor
            
        Returns:
            {"success": bool, "explanation": str, "state": dict}
        """
        tool_name = step.get("tool", "unknown")
        success = result.get("success", False)
        
        if success:
            return {
                "success": True,
                "explanation": f"{tool_name} executed successfully",
                "state": self.get_system_state()
            }
        
        # Tool reported failure - try to understand why
        error = result.get("error", "Unknown error")
        
        # Check specific failures
        if tool_name == "open_application":
            app_name = step.get("parameters", {}).get("app_name", "")
            is_open = self.check_app_open(app_name)
            
            if is_open:
                return {
                    "success": True,
                    "explanation": f"{app_name} is now open",
                    "state": self.get_system_state()
                }
            else:
                return {
                    "success": False,
                    "explanation": f"Failed to open {app_name}: {error}",
                    "state": self.get_system_state()
                }
        
        # Generic failure
        return {
            "success": False,
            "explanation": f"{tool_name} failed: {error}",
            "state": self.get_system_state()
        }


# Global observer instance
_observer_instance = None


def get_observer() -> Observer:
    """Get or create global observer instance."""
    global _observer_instance
    if _observer_instance is None:
        _observer_instance = Observer()
    return _observer_instance
