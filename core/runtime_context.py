"""
Runtime Context - Tracks system state for desktop automation

Maintains:
- Active application
- Current URL (if browser is open)
- Running applications
- Last executed action

This enables context-aware decision making across multi-step commands.
"""

import logging

logger = logging.getLogger(__name__)


class RuntimeContext:
    """
    Maintains runtime state for the automation system.
    
    This context is updated after each action and used by executor
    to make intelligent decisions about next steps.
    """
    
    def __init__(self):
        """Initialize empty runtime context"""
        self.active_app = None          # Currently focused application
        self.current_url = None         # Current browser URL if browser is open
        self.running_apps = []          # List of running application names
        self.last_action = None         # Last executed action
        self.action_history = []        # History of recent actions
        self.clipboard = ""             # Clipboard content
        self.screen_state = {}          # Additional screen state info
        
        logger.debug("RuntimeContext initialized")
    
    def update_app(self, app_name: str):
        """
        Update the active application.
        
        Args:
            app_name: Name of the active application
        """
        self.active_app = app_name
        logger.debug(f"Active app updated: {app_name}")
    
    def update_url(self, url: str):
        """
        Update the current browser URL.
        
        Args:
            url: Current URL
        """
        self.current_url = url
        logger.debug(f"URL updated: {url}")
    
    def set_running_apps(self, apps: list):
        """
        Update list of running applications.
        
        Args:
            apps: List of application names or PIDs
        """
        self.running_apps = apps
        logger.debug(f"Running apps: {len(apps)} applications")
    
    def update_last_action(self, action_dict: dict):
        """
        Record the last executed action.
        
        Args:
            action_dict: Action details (tool, parameters, result)
        """
        self.last_action = action_dict
        self.action_history.append(action_dict)
        
        # Keep only last 50 actions
        if len(self.action_history) > 50:
            self.action_history = self.action_history[-50:]
        
        logger.debug(f"Action recorded: {action_dict.get('action', 'unknown')}")
    
    def is_browser_open(self) -> bool:
        """Check if a browser is currently active"""
        return self.active_app and \
               any(browser in self.active_app.lower() 
                   for browser in ['chrome', 'firefox', 'edge', 'safari'])
    
    def is_app_running(self, app_name: str) -> bool:
        """
        Check if a specific application is running.
        
        Args:
            app_name: Application name to check
            
        Returns:
            True if application is running
        """
        return any(app_name.lower() in app.lower() 
                  for app in self.running_apps)
    
    def get_state_summary(self) -> dict:
        """
        Get a summary of current system state.
        
        Returns:
            Dictionary with current context info
        """
        return {
            "active_app": self.active_app,
            "current_url": self.current_url,
            "running_apps_count": len(self.running_apps),
            "browser_open": self.is_browser_open(),
            "last_action": self.last_action,
            "action_history_length": len(self.action_history)
        }
    
    def reset(self):
        """Reset runtime context"""
        self.active_app = None
        self.current_url = None
        self.running_apps = []
        self.last_action = None
        self.action_history = []
        self.clipboard = ""
        self.screen_state = {}
        logger.debug("RuntimeContext reset")
