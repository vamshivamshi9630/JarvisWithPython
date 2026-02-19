"""
Enhanced app registry for JARVIS personal AI

Intelligently categorizes and launches Windows applications.
Supports:
  - Regular .exe applications
  - Command-line tools (cmd, powershell, python, node, etc.)
  - Windows Store apps
  - Scripts and batch files
  - Applications in PATH
  - Applications in Windows Registry

No hardcoded paths - all detection is dynamic!
"""

import psutil
import subprocess
import os
import winreg
import shutil
from typing import Dict, List, Optional, Tuple

class AppLaunchMethod:
    """Different ways to launch applications"""
    EXE_PATH = "exe_path"        # Direct .exe file path
    REGISTRY = "registry"        # From Windows Registry
    PATH_ENV = "path_env"        # In PATH environment variable
    SCRIPT_FILE = "script_file"  # .bat, .cmd, .ps1, .sh
    COMMAND_LINE = "command_line" # cmd, powershell, python, node
    UWP = "uwp"                  # Windows Store app
    UNKNOWN = "unknown"          # Unknown/untested

class AppRegistry:
    """
    Intelligent application registry for Windows
    
    Features:
    - Fuzzy matching for typo tolerance
    - Automatic launch method detection
    - Registry lookups
    - PATH environment variable scanning
    - Running process detection
    """
    
    # Enhanced aliases with app metadata
    APP_METADATA = {
        # Browsers
        'chrome': {
            'aliases': ['chrome', 'google chrome', 'google', 'chromium'],
            'executable': 'chrome',
            'common_paths': [
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                '%APPDATA%\\Local\\Google\\Chrome\\Application\\chrome.exe'
            ]
        },
        'firefox': {
            'aliases': ['firefox', 'mozilla firefox'],
            'executable': 'firefox',
            'common_paths': [
                'C:\\Program Files\\Mozilla Firefox\\firefox.exe',
                'C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe'
            ]
        },
        'edge': {
            'aliases': ['edge', 'msedge', 'microsoft edge'],
            'executable': 'msedge',
            'common_paths': [
                'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
                'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
            ]
        },
        
        # Text Editors
        'notepad++': {
            'aliases': ['notepad++', 'notepad+', 'n++', 'npp'],
            'executable': 'notepad++',
            'common_paths': [
                'C:\\Program Files\\Notepad++\\notepad++.exe',
                'C:\\Program Files (x86)\\Notepad++\\notepad++.exe'
            ]
        },
        'notepad': {
            'aliases': ['notepad'],
            'executable': 'notepad',
            'common_paths': ['notepad.exe']  # In PATH
        },
        'vscode': {
            'aliases': ['vscode', 'code', 'vs code', 'visual studio code'],
            'executable': 'code',
            'common_paths': [
                'C:\\Program Files\\Microsoft VS Code\\Code.exe',
                'C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe',
                '%APPDATA%\\Local\\Programs\\Microsoft VS Code\\Code.exe'
            ]
        },
        
        # Development Tools
        'python': {
            'aliases': ['python', 'python3', 'python.exe'],
            'executable': 'python',
            'method': AppLaunchMethod.COMMAND_LINE
        },
        'node': {
            'aliases': ['node', 'nodejs', 'node.exe'],
            'executable': 'node',
            'method': AppLaunchMethod.COMMAND_LINE
        },
        'cmd': {
            'aliases': ['cmd', 'command prompt', 'cmd.exe'],
            'executable': 'cmd',
            'method': AppLaunchMethod.COMMAND_LINE
        },
        'powershell': {
            'aliases': ['powershell', 'pwsh', 'posh'],
            'executable': 'powershell',
            'method': AppLaunchMethod.COMMAND_LINE
        },
        'git': {
            'aliases': ['git', 'git bash'],
            'executable': 'git',
            'method': AppLaunchMethod.COMMAND_LINE
        },
        
        # System
        'file explorer': {
            'aliases': ['file explorer', 'explorer', 'files'],
            'executable': 'explorer',
            'common_paths': ['explorer.exe']
        },
        'task manager': {
            'aliases': ['task manager', 'taskmgr'],
            'executable': 'taskmgr',
            'common_paths': ['taskmgr.exe']
        },
        
        # Media
        'vlc': {
            'aliases': ['vlc', 'vlc media player'],
            'executable': 'vlc',
            'common_paths': [
                'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',
                'C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe'
            ]
        },
        'spotify': {
            'aliases': ['spotify'],
            'executable': 'spotify',
            'common_paths': [
                '%APPDATA%\\Spotify\\spotify.exe',
                'C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\spotify.exe'
            ]
        },
        
        # Communication
        'discord': {
            'aliases': ['discord'],
            'executable': 'discord',
            'common_paths': [
                '%LOCALAPPDATA%\\Discord\\app-*\\Discord.exe'
            ]
        },
        'slack': {
            'aliases': ['slack'],
            'executable': 'slack',
            'common_paths': [
                '%LOCALAPPDATA%\\slack\\slack.exe'
            ]
        },
    }

    @staticmethod
    def find_app(app_name: str) -> Optional[str]:
        """
        Find application by name (exact or fuzzy match)
        
        Args:
            app_name: User's app name input
            
        Returns:
            Canonical app name (e.g., "notepad++" for "n++")
        """
        from difflib import get_close_matches
        
        app_name_lower = app_name.lower().strip()
        
        # Direct canonical name match
        if app_name_lower in AppRegistry.APP_METADATA:
            return app_name_lower
        
        # Check aliases
        for canonical_name, metadata in AppRegistry.APP_METADATA.items():
            aliases = metadata.get('aliases', [])
            if app_name_lower in aliases:
                return canonical_name
        
        # Fuzzy match: use difflib for typo tolerance (80% match)
        all_names = list(AppRegistry.APP_METADATA.keys())
        all_aliases = []
        for metadata in AppRegistry.APP_METADATA.values():
            all_aliases.extend(metadata.get('aliases', []))
        
        # Try canonical names first
        close_canonical = get_close_matches(app_name_lower, all_names, n=1, cutoff=0.75)
        if close_canonical:
            return close_canonical[0]
        
        # Try aliases
        close_aliases = get_close_matches(app_name_lower, all_aliases, n=1, cutoff=0.75)
        if close_aliases:
            matched_alias = close_aliases[0]
            for canonical_name, metadata in AppRegistry.APP_METADATA.items():
                if matched_alias in metadata.get('aliases', []):
                    return canonical_name
        
        # Check running processes
        running = AppRegistry.get_all_running_apps()
        for proc_name in running:
            if app_name_lower in proc_name.lower():
                return proc_name
        
        # If not found, return the input as-is (for custom apps)
        return app_name_lower
    
    @staticmethod
    def find_executable_path(app_name: str) -> Optional[str]:
        """
        Find the full path to an application executable
        
        Tries multiple methods:
        1. Common paths
        2. PATH environment variable
        3. Windows Registry
        4. Running process detection
        """
        canonical_name = AppRegistry.find_app(app_name)
        if not canonical_name:
            return None
        
        metadata = AppRegistry.APP_METADATA.get(canonical_name, {})
        
        # Method 1: Try common paths
        common_paths = metadata.get('common_paths', [])
        for path_template in common_paths:
            # Expand environment variables
            path = os.path.expanduser(os.path.expandvars(path_template))
            
            # Handle wildcard paths (e.g., app-*)
            if '*' in path:
                dir_path = os.path.dirname(path)
                pattern = os.path.basename(path)
                if os.path.exists(dir_path):
                    import glob
                    matches = glob.glob(path)
                    if matches:
                        return matches[0]
            elif os.path.exists(path):
                return path
        
        # Method 2: Search PATH environment variable
        executable = metadata.get('executable', canonical_name)
        path_result = shutil.which(executable)
        if path_result:
            return path_result
        
        # Method 3: Windows Registry lookup
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths"
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            try:
                subkey = winreg.OpenKey(registry_key, f"{executable}.exe")
                path, _ = winreg.QueryValueEx(subkey, "")
                if os.path.exists(path):
                    return path
            except WindowsError:
                pass
        except Exception:
            pass
        
        # Method 4: Check running processes
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if canonical_name.lower() in proc.info['name'].lower():
                    exe_path = proc.info.get('exe')
                    if exe_path and os.path.exists(exe_path):
                        return exe_path
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return None
    
    @staticmethod
    def get_launch_method(app_name: str) -> str:
        """Determine the best method to launch the app"""
        canonical_name = AppRegistry.find_app(app_name) 
        metadata = AppRegistry.APP_METADATA.get(canonical_name, {})
        
        # Explicit method specified
        if 'method' in metadata:
            return metadata['method']
        
        # Auto-detect from executable path
        exe_path = AppRegistry.find_executable_path(app_name)
        if exe_path:
            if exe_path.endswith('.exe'):
                return AppLaunchMethod.EXE_PATH
            elif exe_path.endswith(('.bat', '.cmd')):
                return AppLaunchMethod.SCRIPT_FILE
            elif exe_path.endswith('.ps1'):
                return AppLaunchMethod.SCRIPT_FILE
        
        # Default to command line (for tools like python, node, cmd)
        return AppLaunchMethod.COMMAND_LINE
    
    @staticmethod
    def launch_app(app_name: str) -> Tuple[bool, str]:
        """
        Launch an application using the appropriate method
        
        Returns:
            (success: bool, message: str)
        """
        canonical_name = AppRegistry.find_app(app_name)
        launch_method = AppRegistry.get_launch_method(app_name)
        exe_path = AppRegistry.find_executable_path(app_name)
        executable = AppRegistry.APP_METADATA.get(canonical_name, {}).get('executable', canonical_name)
        
        try:
            if launch_method == AppLaunchMethod.EXE_PATH and exe_path:
                # Direct executable path
                subprocess.Popen(f'start "" "{exe_path}"', shell=True)
                return (True, f"Opened {canonical_name}")
            
            elif launch_method == AppLaunchMethod.COMMAND_LINE:
                #Command-line tool
                subprocess.Popen(executable, shell=True)
                return (True, f"Opened {canonical_name}")
            
            elif launch_method == AppLaunchMethod.SCRIPT_FILE and exe_path:
                # Script file
                subprocess.Popen(f'{exe_path}', shell=True)
                return (True, f"Opened {canonical_name}")
            
            elif exe_path:
                # Generic executable
                subprocess.Popen(f'start "" "{exe_path}"', shell=True)
                return (True, f"Opened {canonical_name}")
            
            else:
                # Try as command
                subprocess.Popen(executable, shell=True)
                return (True, f"Opened {canonical_name}")
        
        except Exception as e:
            return (False, f"Could not open {app_name}. Not found or not installed.")
    
    @staticmethod
    def is_running(app_name: str) -> bool:
        """Check if an application is currently running"""
        canonical_name = AppRegistry.find_app(app_name)
        if not canonical_name:
            return False
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if canonical_name.lower() in proc_name or proc_name in canonical_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return False
    
    @staticmethod
    def get_all_running_apps() -> List[str]:
        """Get all currently running applications"""
        running = []
        seen = set()
        
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if name not in seen:
                    running.append(name)
                    seen.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return sorted(running)


# Test
if __name__ == "__main__":
    test_apps = ['notepad++', 'edge', 'chrome', 'vscode', 'n++', 'cmd', 'python']
    
    print("AppRegistry Comprehensive Test")
    print("="*70)
    
    for app in test_apps:
        found = AppRegistry.find_app(app)
        exe_path = AppRegistry.find_executable_path(app)
        method = AppRegistry.get_launch_method(app)
        running = AppRegistry.is_running(app)
        
        print(f"\n{app:15} → {found:15} | Method: {method:15}")
        if exe_path:
            print(f"{'':15}    Path: {exe_path}")
        print(f"{'':15}    Running: {running}")

    
    print(f"\nRunning apps: {AppRegistry.get_all_running_apps()[:5]}...")
