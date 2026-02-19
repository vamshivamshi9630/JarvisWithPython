"""
Browser Automation using Selenium

Handles automated browser control:
- Open browser
- Navigate to URLs
- Search (YouTube, Google, etc)
- Find elements and interact
- Extract information

Used for structured browser-based automation tasks.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserAutomation:
    """
    Selenium-based browser automation.
    
    Provides high-level browser control for desktop automation.
    """
    
    def __init__(self):
        """Initialize browser automation setup"""
        self.driver = None
        self.current_url = None
        
        try:
            from selenium import webdriver
            self.webdriver = webdriver
        except ImportError:
            logger.warning("Selenium not installed. Browser automation unavailable.")
            self.webdriver = None
    
    def open_browser(self, browser_type: str = "chrome") -> str:
        """
        Open a browser instance.
        
        Args:
            browser_type: "chrome", "firefox", "edge", etc
            
        Returns:
            Status message
        """
        if self.driver:
            logger.debug("Browser already open")
            return "Browser already open"
        
        try:
            if not self.webdriver:
                return "Selenium not installed"
            
            if browser_type.lower() == "chrome":
                self.driver = self.webdriver.Chrome()
            elif browser_type.lower() == "firefox":
                self.driver = self.webdriver.Firefox()
            elif browser_type.lower() == "edge":
                self.driver = self.webdriver.Edge()
            else:
                self.driver = self.webdriver.Chrome()  # Default
            
            logger.info(f"Browser opened: {browser_type}")
            return f"{browser_type.capitalize()} browser launched"
            
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            return f"Failed to open browser: {e}"
    
    def navigate(self, url: str) -> str:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to (with or without https://)
            
        Returns:
            Status message
        """
        try:
            if not self.driver:
                self.open_browser()
            
            # Add https:// if not present
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            
            self.driver.get(url)
            self.current_url = url
            
            logger.info(f"Navigated to: {url}")
            return f"Navigated to {url}"
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return f"Failed to navigate: {e}"
    
    def search_youtube(self, query: str) -> str:
        """
        Search YouTube for a query.
        
        Args:
            query: Search query
            
        Returns:
            Status message
        """
        try:
            if not self.driver:
                self.open_browser()
            
            # Navigate to YouTube if not already there
            if "youtube" not in self.driver.current_url:
                self.navigate("youtube.com")
            
            # Find search box and search
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            logger.info(f"YouTube search: {query}")
            return f"Searched YouTube for: {query}"
            
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return f"Failed to search YouTube: {e}"
    
    def search_google(self, query: str) -> str:
        """
        Search Google for a query.
        
        Args:
            query: Search query
            
        Returns:
            Status message
        """
        try:
            if not self.driver:
                self.open_browser()
            
            # Navigate to Google if needed
            if "google" not in self.driver.current_url:
                self.navigate("google.com")
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            
            search_box = self.driver.find_element(By.NAME, "q")
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            logger.info(f"Google search: {query}")
            return f"Searched Google for: {query}"
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return f"Failed to search Google: {e}"
    
    def get_page_title(self) -> Optional[str]:
        """
        Get current page title.
        
        Returns:
            Page title or None
        """
        try:
            if not self.driver:
                return None
            return self.driver.title
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return None
    
    def close_browser(self) -> str:
        """
        Close the browser.
        
        Returns:
            Status message
        """
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.current_url = None
                logger.info("Browser closed")
                return "Browser closed"
            return "No browser open"
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")
            return f"Failed to close browser: {e}"


# Global browser automation instance
_browser_automation = None


def get_browser_automation() -> BrowserAutomation:
    """Get or create global browser automation instance"""
    global _browser_automation
    if _browser_automation is None:
        _browser_automation = BrowserAutomation()
    return _browser_automation
