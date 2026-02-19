"""
System Monitor - OS State Tracking

Monitors:
- Active window
- Running applications
- System processes
- Desktop state

Used to update RuntimeContext with current system state.
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    Monitors OS and system state.
    
    Provides information about running applications, active windows, etc.
    """
    
    def __init__(self):
        """Initialize system monitor"""
        try:
            import psutil
            self.psutil = psutil
        except ImportError:
            logger.warning("psutil not installed. App monitoring unavailable.")
            self.psutil = None
        
        try:
            import pygetwindow as gw
            self.gw = gw
        except ImportError:
            logger.warning("pygetwindow not installed. Window monitoring unavailable.")
            self.gw = None
    
    def get_running_apps(self) -> List[str]:
        """
        Get list of running applications.
        
        Returns:
            List of process names
        """
        if not self.psutil:
            logger.warning("psutil unavailable")
            return []
        
        try:
            apps = []
            for proc in self.psutil.process_iter(['name', 'pid']):
                try:
                    apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            logger.debug(f"Found {len(apps)} running processes")
            return apps
            
        except Exception as e:
            logger.error(f"Failed to get running apps: {e}")
            return []
    
    def get_active_window(self) -> Optional[str]:
        """
        Get the title of the currently active window.
        
        Returns:
            Window title or None
        """
        if not self.gw:
            logger.warning("pygetwindow unavailable")
            return None
        
        try:
            active_window = self.gw.getActiveWindow()
            if active_window:
                title = active_window.title
                logger.debug(f"Active window: {title}")
                return title
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    def is_app_running(self, app_name: str) -> bool:
        """
        Check if a specific application is running.
        
        Args:
            app_name: Application name to check
            
        Returns:
            True if running
        """
        running_apps = self.get_running_apps()
        app_lower = app_name.lower()
        
        return any(app_lower in app.lower() for app in running_apps)
    
    def get_browser_type(self) -> Optional[str]:
        """
        Detect if a browser is open and which one.
        
        Returns:
            "chrome", "firefox", "edge", or None
        """
        try:
            active = self.get_active_window()
            if not active:
                return None
            
            active_lower = active.lower()
            
            if "chrome" in active_lower:
                return "chrome"
            elif "firefox" in active_lower:
                return "firefox"
            elif "edge" in active_lower:
                return "edge"
            elif "safari" in active_lower:
                return "safari"
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to detect browser: {e}")
            return None
    
    def get_window_count(self, app_name: str) -> int:
        """
        Get number of open windows for an application.
        
        Args:
            app_name: Application name
            
        Returns:
            Number of windows
        """
        if not self.gw:
            return 0
        
        try:
            windows = self.gw.getWindowsWithTitle(app_name)
            return len(windows)
        except Exception as e:
            logger.debug(f"Failed to count windows: {e}")
            return 0


# Global system monitor instance
_system_monitor = None


def get_system_monitor() -> SystemMonitor:
    """Get or create global system monitor instance"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor
