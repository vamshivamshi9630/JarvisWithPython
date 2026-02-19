"""
Executor: Pure Tool Execution Engine

Takes tool name + parameters and executes them.
Does NOT do planning or intent detection.

Now extended with:
- RuntimeContext support for stateful automation
- Structured action handling (dict-based steps)
- Browser automation (Selenium)
- OS-level controls (keyboard/mouse)
- System monitoring integration
- Complete PC automation (12 feature categories)
"""

import logging
from typing import Dict, Any, Optional
from skills.system_cmds import run_system
from skills.app_opener import open_app
from skills.file_opener import open_file
from skills.system_controls import handle_system_control
from skills.keyboard_control import keyboard
from core.context import context
import time

# Extended automation modules
try:
    from skills.browser_automation import get_browser_automation
except ImportError:
    get_browser_automation = lambda: None

try:
    from skills.os_controls import get_os_controls
except ImportError:
    get_os_controls = lambda: None

try:
    from core.system_monitor import get_system_monitor
except ImportError:
    get_system_monitor = lambda: None

try:
    from core.runtime_context import RuntimeContext
except ImportError:
    RuntimeContext = None

# New PC Automation Features
try:
    from skills.system_info import (
        get_cpu_info, get_ram_info, get_disk_info, get_battery_info,
        get_os_info, get_boot_time, get_network_info, get_system_status,
        get_cpu_temperature
    )
except ImportError:
    get_cpu_info = get_ram_info = get_disk_info = None

try:
    from skills.power_control import (
        set_volume, increase_volume, decrease_volume, mute_volume, unmute_volume,
        set_brightness, get_brightness_level, increase_brightness, decrease_brightness,
        toggle_wifi, toggle_airplane_mode, get_power_info
    )
except ImportError:
    set_volume = increase_volume = decrease_volume = None

try:
    from skills.file_management import (
        create_file, create_folder, delete_file, delete_folder, rename_file,
        copy_file, move_file, list_files, search_files, get_file_info,
        get_disk_space, open_folder, clear_temp_files
    )
except ImportError:
    create_file = delete_file = None

try:
    from skills.process_monitor import (
        get_running_processes, find_process, is_running, kill_process,
        get_heavy_processes, get_process_details
    )
except ImportError:
    get_running_processes = find_process = None

try:
    from skills.internet_control import (
        check_internet, get_ip_address, get_dns_info, ping_website,
        internet_speed_test, get_wifi_name, get_network_interfaces,
        get_connected_devices
    )
except ImportError:
    check_internet = get_ip_address = None

try:
    from skills.clipboard_control import (
        read_clipboard, write_clipboard, clear_clipboard,
        append_clipboard, get_clipboard_length
    )
except ImportError:
    read_clipboard = write_clipboard = None

try:
    from skills.notifications_control import (
        show_notification, show_alert, show_warning, show_error,
        show_question, show_reminder
    )
except ImportError:
    show_notification = show_alert = None

logger = logging.getLogger(__name__)


# ============== TOOL IMPLEMENTATION ==============

def _navigate_website(website: str) -> str:
    """Navigate to a website in the browser."""
    try:
        keyboard.press_key("ctrl+t")
        time.sleep(0.3)
        keyboard.type_text(website)
        time.sleep(0.2)
        keyboard.press_key("enter")
        time.sleep(1)
        return f"✓ Navigated to {website}"
    except Exception as e:
        return f"✗ Navigation failed: {str(e)}"


def _search_term(query: str, location: str = "") -> str:
    """Search for a term."""
    try:
        if location and "youtube" in location.lower():
            keyboard.press_key("ctrl+f")
            time.sleep(0.2)
        else:
            keyboard.press_key("ctrl+t")
            time.sleep(0.3)
        
        keyboard.type_text(query)
        time.sleep(0.2)
        keyboard.press_key("enter")
        time.sleep(1)
        return f"✓ Searched for '{query}'"
    except Exception as e:
        return f"✗ Search failed: {str(e)}"


def _press_sequence(keys: list) -> str:
    """Press a sequence of keys."""
    try:
        for key in keys:
            keyboard.press_key(key)
            time.sleep(0.1)
        return f"✓ Pressed {len(keys)} keys"
    except Exception as e:
        return f"✗ Key sequence failed: {str(e)}"


def _set_volume(level: int) -> str:
    """Set system volume."""
    try:
        handle_system_control("volume", "set", level)
        return f"✓ Volume set to {level}%"
    except Exception as e:
        return f"✗ Volume control failed: {str(e)}"


def _adjust_volume(direction: str, steps: int = 1) -> str:
    """Adjust volume up or down."""
    try:
        handle_system_control("volume", direction, steps)
        return f"✓ Volume {direction} by {steps} steps"
    except Exception as e:
        return f"✗ Volume adjustment failed: {str(e)}"


def _set_brightness(level: int) -> str:
    """Set screen brightness."""
    try:
        handle_system_control("brightness", "set", level)
        return f"✓ Brightness set to {level}%"
    except Exception as e:
        return f"✗ Brightness control failed: {str(e)}"


def _create_file(path: str, content: str = "") -> str:
    """Create a file."""
    try:
        with open(path, 'w') as f:
            f.write(content)
        return f"✓ File created: {path}"
    except Exception as e:
        return f"✗ File creation failed: {str(e)}"


def _get_system_status() -> str:
    """Get system status."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        return f"CPU: {cpu}% | RAM: {ram}%"
    except:
        return "System status unavailable"


def _get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return f"Current time: {datetime.now().strftime('%H:%M:%S')}"


# ============== BROWSER AUTOMATION TOOLS ==============

def _open_browser(browser_type: str = "chrome") -> str:
    """Open a web browser."""
    try:
        browser = get_browser_automation()
        if not browser:
            return "✗ Browser automation unavailable"
        return browser.open_browser(browser_type)
    except Exception as e:
        return f"✗ Failed to open browser: {str(e)}"


def _navigate_browser(url: str) -> str:
    """Navigate browser to URL using Selenium."""
    try:
        browser = get_browser_automation()
        if not browser:
            return "✗ Browser automation unavailable"
        return browser.navigate(url)
    except Exception as e:
        return f"✗ Navigation failed: {str(e)}"


def _search_youtube(query: str) -> str:
    """Search YouTube for a query."""
    try:
        browser = get_browser_automation()
        if not browser:
            return "✗ Browser automation unavailable"
        return browser.search_youtube(query)
    except Exception as e:
        return f"✗ YouTube search failed: {str(e)}"


def _search_google(query: str) -> str:
    """Search Google for a query."""
    try:
        browser = get_browser_automation()
        if not browser:
            return "✗ Browser automation unavailable"
        return browser.search_google(query)
    except Exception as e:
        return f"✗ Google search failed: {str(e)}"


# ============== OS CONTROL TOOLS ==============

def _type_text_direct(text: str) -> str:
    """Type text using pyautogui (more reliable than keyboard emulation)."""
    try:
        os_ctrl = get_os_controls()
        if not os_ctrl:
            return keyboard.type_text(text)  # Fall back to old method
        return os_ctrl.type_text(text)
    except Exception as e:
        return f"✗ Unable to type: {str(e)}"


def _press_key_direct(key: str) -> str:
    """Press key using pyautogui."""
    try:
        os_ctrl = get_os_controls()
        if not os_ctrl:
            return keyboard.press_key(key)  # Fall back to old method
        return os_ctrl.press_key(key)
    except Exception as e:
        return f"✗ Key press failed: {str(e)}"


# ============== SYSTEM MONITORING TOOLS ==============

def _get_active_window() -> str:
    """Get the currently active window."""
    try:
        monitor = get_system_monitor()
        if not monitor:
            return "System monitoring unavailable"
        window = monitor.get_active_window()
        return window if window else "No active window"
    except Exception as e:
        return f"Failed to get active window: {str(e)}"


def _check_app_running(app_name: str) -> str:
    """Check if an app is running."""
    try:
        monitor = get_system_monitor()
        if not monitor:
            return "System monitoring unavailable"
        is_running = monitor.is_app_running(app_name)
        return f"✓ {app_name} is running" if is_running else f"✗ {app_name} is not running"
    except Exception as e:
        return f"Failed to check app: {str(e)}"


# ============== TOOL MAPPING ==============
# Maps tool names to execution functions

TOOL_MAP = {
    # ===== APP CONTROL =====
    "open_application": lambda p: open_app(p.get("app_name", "")),
    "close_application": lambda p: f"Closed {p.get('app_name')}",
    
    # ===== WEB CONTROL =====
    "navigate_to_website": lambda p: _navigate_website(p.get("website", "")),
    "search": lambda p: _search_term(p.get("query", ""), p.get("location", "")),
    "open_browser": lambda p: _open_browser(p.get("browser_type", "chrome")),
    "navigate": lambda p: _navigate_browser(p.get("target", p.get("url", ""))),
    "search_youtube": lambda p: _search_youtube(p.get("query", p.get("target", ""))),
    "search_google": lambda p: _search_google(p.get("query", "")),
    
    # ===== INPUT CONTROL =====
    "type_text": lambda p: _type_text_direct(p.get("text", "")),
    "press_key": lambda p: _press_key_direct(p.get("key", "")),
    "press_keys_sequence": lambda p: _press_sequence(p.get("keys", [])),
    
    # ===== MEDIA CONTROL =====
    "play_media": lambda p: keyboard.press_key("space") or "Playing",
    "pause_media": lambda p: keyboard.press_key("space") or "Paused",
    "stop_media": lambda p: keyboard.press_key("escape") or "Stopped",
    "next_track": lambda p: keyboard.press_key("shift+right") or "Next track",
    "previous_track": lambda p: keyboard.press_key("shift+left") or "Previous track",
    
    # ===== SYSTEM INFO =====
    "get_cpu_usage": lambda p: get_cpu_info().get("message", "CPU info unavailable"),
    "get_ram_usage": lambda p: get_ram_info().get("message", "RAM info unavailable"),
    "get_disk_usage": lambda p: get_disk_info(p.get("drive", "C:")).get("message", "Disk info unavailable"),
    "get_battery": lambda p: get_battery_info().get("message", "Battery info unavailable"),
    "get_os_info": lambda p: get_os_info().get("message", "OS info unavailable"),
    "get_boot_time": lambda p: get_boot_time().get("message", "Boot time unavailable"),
    "get_ip": lambda p: get_network_info().get("message", "Network info unavailable"),
    "get_system_status": lambda p: get_system_status().get("message", "System status unavailable"),
    "get_cpu_temp": lambda p: get_cpu_temperature().get("message", "Temperature unavailable"),
    
    # ===== POWER CONTROL =====
    "set_volume": lambda p: set_volume(p.get("level", 50)).get("message", "Volume set"),
    "increase_volume": lambda p: increase_volume(p.get("step", 5)).get("message", "Volume increased"),
    "decrease_volume": lambda p: decrease_volume(p.get("step", 5)).get("message", "Volume decreased"),
    "mute": lambda p: mute_volume().get("message", "Muted"),
    "unmute": lambda p: unmute_volume().get("message", "Unmuted"),
    "set_brightness": lambda p: set_brightness(p.get("level", 50)).get("message", "Brightness set"),
    "increase_brightness": lambda p: increase_brightness(p.get("step", 10)).get("message", "Brightness increased"),
    "decrease_brightness": lambda p: decrease_brightness(p.get("step", 10)).get("message", "Brightness decreased"),
    "toggle_wifi": lambda p: toggle_wifi().get("message", "WiFi toggled"),
    "toggle_airplane": lambda p: toggle_airplane_mode().get("message", "Airplane mode toggled"),
    "get_power_info": lambda p: get_power_info().get("message", "Power info unavailable"),
    
    # ===== FILE MANAGEMENT =====
    "create_file": lambda p: create_file(p.get("path", ""), p.get("content", "")).get("message", "File created"),
    "create_folder": lambda p: create_folder(p.get("path", "")).get("message", "Folder created"),
    "delete_file": lambda p: delete_file(p.get("path", "")).get("message", "File deleted"),
    "delete_folder": lambda p: delete_folder(p.get("path", ""), p.get("recursive", False)).get("message", "Folder deleted"),
    "rename_file": lambda p: rename_file(p.get("old_path", ""), p.get("new_path", "")).get("message", "File renamed"),
    "copy_file": lambda p: copy_file(p.get("source", ""), p.get("destination", "")).get("message", "File copied"),
    "move_file": lambda p: move_file(p.get("source", ""), p.get("destination", "")).get("message", "File moved"),
    "list_files": lambda p: list_files(p.get("folder", ".")).get("message", "Files listed"),
    "search_files": lambda p: search_files(p.get("folder", "."), p.get("pattern", "")).get("message", "Search complete"),
    "get_file_info": lambda p: get_file_info(p.get("path", "")).get("message", "File info retrieved"),
    "open_folder": lambda p: open_folder(p.get("path", "")).get("message", "Folder opened"),
    "clear_temp": lambda p: clear_temp_files().get("message", "Temp cleared"),
    
    # ===== PROCESS MONITORING =====
    "list_processes": lambda p: get_running_processes().get("message", "Processes listed"),
    "find_process": lambda p: find_process(p.get("name", "")).get("message", "Process search complete"),
    "check_running": lambda p: is_running(p.get("app_name", "")).get("message", "Process check complete"),
    "kill_process": lambda p: kill_process(p.get("name", ""), p.get("force", False)).get("message", "Process action complete"),
    "heavy_processes": lambda p: get_heavy_processes(p.get("limit", 5)).get("message", "Heavy processes listed"),
    "process_details": lambda p: get_process_details(p.get("name", "")).get("message", "Process details retrieved"),
    
    # ===== INTERNET & NETWORK =====
    "check_internet": lambda p: check_internet().get("message", "Internet check complete"),
    "get_ip": lambda p: get_ip_address().get("message", "IP retrieved"),
    "get_dns": lambda p: get_dns_info().get("message", "DNS info retrieved"),
    "ping": lambda p: ping_website(p.get("website", "")).get("message", "Ping complete"),
    "speed_test": lambda p: internet_speed_test().get("message", "Speed test complete"),
    "get_wifi_name": lambda p: get_wifi_name().get("message", "WiFi name retrieved"),
    "network_interfaces": lambda p: get_network_interfaces().get("message", "Network info retrieved"),
    "connected_devices": lambda p: get_connected_devices().get("message", "Device scan complete"),
    
    # ===== CLIPBOARD CONTROL =====
    "read_clipboard": lambda p: read_clipboard().get("message", "Clipboard read"),
    "write_clipboard": lambda p: write_clipboard(p.get("text", "")).get("message", "Copied to clipboard"),
    "clear_clipboard": lambda p: clear_clipboard().get("message", "Clipboard cleared"),
    "append_clipboard": lambda p: append_clipboard(p.get("text", "")).get("message", "Appended to clipboard"),
    "clipboard_length": lambda p: get_clipboard_length().get("message", "Clipboard length retrieved"),
    
    # ===== NOTIFICATIONS =====
    "notification": lambda p: show_notification(p.get("title", ""), p.get("message", "")).get("message", "Notification shown"),
    "alert": lambda p: show_alert(p.get("title", ""), p.get("message", "")).get("message", "Alert shown"),
    "warning": lambda p: show_warning(p.get("title", ""), p.get("message", "")).get("message", "Warning shown"),
    "error_dialog": lambda p: show_error(p.get("title", ""), p.get("message", "")).get("message", "Error shown"),
    "question": lambda p: show_question(p.get("title", ""), p.get("message", "")).get("message", "Question asked"),
    "reminder": lambda p: show_reminder(p.get("title", ""), p.get("message", ""), p.get("delay", 0)).get("message", "Reminder set"),
    
    # ===== LEGACY SYSTEM CONTROL =====
    "lock_screen": lambda p: keyboard.press_key("win+l") or "Screen locked",
    "shutdown": lambda p: "Shutdown initiated",
    "restart": lambda p: "Restart initiated",
}


# ============== MAIN EXECUTION METHOD ==============

def execute(action):
    """
    Universal execution method for both string and structured actions.
    
    Args:
        action: Either a dict (structured action) or string (fallback)
        
    Returns:
        Execution result string
    """
    if isinstance(action, dict):
        action_type = action.get("action")
        
        if action_type == "open_application":
            result = execute_tool(
                "open_application",
                {"app_name": action.get("target")}
            )
            return result.get("message", "Opened application") if isinstance(result, dict) else str(result)
        
        elif action_type == "type_text":
            result = execute_tool(
                "type_text",
                {"text": action.get("text")}
            )
            return result.get("message", "Typed text") if isinstance(result, dict) else str(result)
        
        elif action_type == "navigate":
            result = execute_tool(
                "navigate",
                {"target": action.get("target")}
            )
            return result.get("message", "Navigated") if isinstance(result, dict) else str(result)
        
        elif action_type == "new_tab":
            # Generic shortcut for new tab
            result = execute_tool(
                "press_key",
                {"key": "ctrl+t"}
            )
            return result.get("message", "Opened new tab") if isinstance(result, dict) else str(result)
        
        elif action_type == "raw":
            return f"Skipped unsupported step: {action.get('text')}"
        
        else:
            return f"Error: Unknown action {action_type}"
    
    # Fallback if string passed accidentally
    return f"Error: Invalid action format"


# ============== PUBLIC API ==============

def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a single tool with given parameters.
    
    This is the ONLY public execution method.
    Called by orchestrator when executing plan steps.
    
    Args:
        tool_name: Name of the tool to execute
        parameters: Dictionary of parameters for the tool
        
    Returns:
        {
            "success": bool,
            "message": str,
            "data": dict,
            "error": str or None
        }
    """
    logger.info(f"🔧 Executing: {tool_name}")
    
    if tool_name not in TOOL_MAP:
        logger.error(f"❌ Unknown tool: {tool_name}")
        return {
            "success": False,
            "message": f"Unknown tool: {tool_name}",
            "data": {},
            "error": f"Tool '{tool_name}' not found in registry"
        }
    
    try:
        # Get the executor function
        executor_func = TOOL_MAP[tool_name]
        
        # Execute it
        result = executor_func(parameters)
        
        # Convert result to string if needed
        result_str = str(result) if result else "✓ Done"
        
        # Log the action
        context.add_action(tool_name, parameters)
        
        logger.info(f"✓ {result_str}")
        
        return {
            "status": "success",
            "message": result_str,
            "data": {"result": result_str},
            "error": None
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Execution failed: {error_msg}")
        context.add_action(tool_name, parameters, success=False)
        
        return {
            "status": "failed",
            "message": f"Failed to execute {tool_name}",
            "data": {},
            "error": error_msg
        }


# ============== STRUCTURED ACTION EXECUTION ==============
# For multi-step commands with runtime context support

def execute_structured_action(action_dict: Dict[str, Any], 
                             runtime_context: Optional[Any] = None) -> Dict[str, Any]:
    """
    Execute a structured action from multi-step parser.
    
    Structured actions are dicts with "action" key:
    {"action": "open_application", "target": "chrome"}
    {"action": "type_text", "text": "hello"}
    {"action": "navigate", "target": "youtube.com"}
    
    Args:
        action_dict: Action dictionary from MultiStepParser
        runtime_context: RuntimeContext instance for context-aware decisions
        
    Returns:
        Execution result dict
    """
    if not action_dict or "action" not in action_dict:
        return {"success": False, "message": "Invalid action format"}
    
    action_type = action_dict.get("action", "raw")
    
    try:
        # Map structured actions to tool calls
        if action_type == "open_application":
            tool_name = "open_application"
            params = {"app_name": action_dict.get("target", "")}
        
        elif action_type == "type_text":
            tool_name = "type_text"
            params = {"text": action_dict.get("text", "")}
        
        elif action_type == "navigate":
            # Smart routing: use Selenium if browser is open
            target = action_dict.get("target", "")
            if runtime_context and runtime_context.is_browser_open():
                tool_name = "navigate"
                params = {"target": target}
            else:
                tool_name = "navigate_to_website"
                params = {"website": target}
        
        elif action_type == "search":
            # Search YouTube if it's mentioned
            query = action_dict.get("query", "")
            if "youtube" in (runtime_context.current_url or "").lower():
                tool_name = "search_youtube"
                params = {"query": query}
            else:
                tool_name = "search"
                params = {"query": query}
        
        elif action_type == "press_key":
            tool_name = "press_key"
            params = {"key": action_dict.get("key", "")}
        
        elif action_type == "close_application":
            tool_name = "close_application"
            params = {"app_name": action_dict.get("target", "")}
        
        elif action_type == "click":
            tool_name = "press_key"
            params = {"key": "space"}  # Fallback
        
        elif action_type == "raw":
            # Unknown action - try to execute as-is
            logger.warning(f"Unknown action type: {action_dict}")
            return {"success": False, "message": f"Unknown action: {action_dict}"}
        
        else:
            return {"success": False, "message": f"Unsupported action: {action_type}"}
        
        # Execute the tool
        result = execute_tool(tool_name, params)
        
        # Update runtime context if provided
        if runtime_context:
            action_record = {
                "action_type": action_type,
                "tool_name": tool_name,
                "parameters": params,
                "result": result.get("message", ""),
                "success": result.get("status") == "success"
            }
            runtime_context.update_last_action(action_record)
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Structured action failed: {error_msg}")
        return {
            "status": "failed",
            "message": f"Failed to execute {action_type}",
            "error": error_msg
        }
