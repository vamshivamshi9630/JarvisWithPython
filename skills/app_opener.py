import subprocess
import platform
import os
import winreg
from difflib import get_close_matches
import sys

# Windows-specific constant for creating new console window
if platform.system() == "Windows":
    CREATE_NEW_CONSOLE = 0x00000010  # From Windows API
else:
    CREATE_NEW_CONSOLE = 0

try:
    from core.app_registry import AppRegistry
except ImportError:
    AppRegistry = None

# Fallback APP_COMMANDS if AppRegistry not available
APP_COMMANDS = {
    "chrome": "chrome",
    "browser": "chrome",
    "vscode": "code",
    "code": "code",
    "vs code": "code",
    "notepad++": "notepad++",
    "notepad plus plus": "notepad++",
    "notepad": "notepad",
    "file explorer": "explorer",
    "explorer": "explorer",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "teams": "teams",
    "microsoft teams": "teams",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "pwsh": "pwsh",
    "terminal": "powershell",
    "git bash": "bash",
    "qt": "qt",
    "qt creator": "qtcreator",
    "sourcetree": "sourcetree",
    "git": "git",
    "github": "git",
    "slack": "slack",
    "discord": "discord",
    "telegram": "telegram",
    "whatsapp": "whatsapp",
    "zoom": "zoom",
    "skype": "skype",
    "vlc": "vlc",
    "media player": "vlc",
    "vlc media player": "vlc",
    "spotify": "spotify",
    "steam": "steam",
    "epic games": "epic",
    "steam games": "steam",
    "blender": "blender",
    "gimp": "gimp",
    "photoshop": "photoshop",
    "illustrator": "illustrator",
    "premiere": "premiere",
    "audition": "audition",
    "firefox": "firefox",
    "safari": "safari",
    "opera": "opera",
    "brave": "brave",
    "google drive": "googledrive",
    "dropbox": "dropbox",
    "onedrive": "onedrive",
    "icloud": "icloud",
    "sublime": "sublime",
    "atom": "atom",
    "notepad2": "notepad2",
    "winrar": "winrar",
    "7zip": "7zfm",
    "winzip": "winzip",
}


def find_app_in_registry(app_name):
    """Try to find app executable in Windows Registry"""
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths"
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
        
        # Try to find with .exe
        try:
            subkey = winreg.OpenKey(registry_key, f"{app_name}.exe")
            path, _ = winreg.QueryValueEx(subkey, "")
            return path
        except:
            pass
        
        # Close and try HKEY_CURRENT_USER
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
        try:
            subkey = winreg.OpenKey(registry_key, f"{app_name}.exe")
            path, _ = winreg.QueryValueEx(subkey, "")
            return path
        except:
            pass
    except:
        pass
    
    return None


def find_app_in_path(app_name):
    """Try to find app in system PATH"""
    try:
        result = subprocess.run(
            f'where {app_name}' if platform.system() == "Windows" else f'which {app_name}',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None


def open_app(app_name: str):
    """
    Open an application with intelligent detection and fuzzy matching.
    
    Supports:
    - Regular .exe applications  
    - Command-line tools (cmd, python, node, etc.)
    - Windows Store apps
    - Scripts and batch files
    - Applications in PATH
    - Registry lookup
    
    Features:
    - Typo correction via fuzzy matching
    - Automatic launch method detection
    - No hardcoded paths (fully dynamic)
    """
    app = app_name.lower().strip()
    
    # PRIMARY METHOD: Use enhanced AppRegistry
    if AppRegistry:
        try:
            success, message = AppRegistry.launch_app(app)
            return message
        except AttributeError:
            pass  # Old version of AppRegistry, fall through
        except Exception as e:
            pass  # Fall through to other methods
    
    # FALLBACK METHOD 1: Exact match in APP_COMMANDS
    cmd = None
    if app in APP_COMMANDS:
        cmd = APP_COMMANDS[app]
    
    # FALLBACK METHOD 2: Fuzzy matching for typos (80% similarity)
    if not cmd:
        close_matches = get_close_matches(app, APP_COMMANDS.keys(), n=1, cutoff=0.80)
        if close_matches:
            corrected_app = close_matches[0]
            cmd = APP_COMMANDS[corrected_app]
            app = corrected_app  # Use corrected name in messages
    
    # FALLBACK METHOD 3: Registry lookup
    if not cmd:
        registry_path = find_app_in_registry(app)
        if registry_path:
            cmd = registry_path
    
    # FALLBACK METHOD 4: PATH lookup
    if not cmd:
        path_result = find_app_in_path(app)
        if path_result:
            cmd = path_result
    
    # FALLBACK METHOD 5: Try as direct executable
    if not cmd:
        cmd = app
    
    # Execute the application
    try:
        if platform.system() == "Windows":
            # Special handling for terminal applications - use CREATE_NEW_CONSOLE flag
            if cmd.lower() in ["cmd", "cmd.exe", "command prompt"]:
                # Open CMD in a completely new console window
                subprocess.Popen(
                    "cmd.exe",
                    creationflags=CREATE_NEW_CONSOLE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif cmd.lower() in ["powershell", "pwsh", "powershell.exe"]:
                # Open PowerShell in a completely new console window
                subprocess.Popen(
                    "powershell.exe",
                    creationflags=CREATE_NEW_CONSOLE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Regular applications - use start command
                subprocess.Popen(
                    f'start "" "{cmd}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        else:
            subprocess.Popen([cmd])

        return f"Opened {app_name}"

    except Exception as e:
        return f"Could not open '{app_name}'. Not found in system."
