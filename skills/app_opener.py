import subprocess
import platform
import os
import winreg


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
    """Open an application by name"""
    app = app_name.lower().strip()

    # Check hardcoded apps first
    if app in APP_COMMANDS:
        cmd = APP_COMMANDS[app]
    else:
        # Try to find the app in registry
        registry_path = find_app_in_registry(app)
        if registry_path:
            cmd = registry_path
        else:
            # Try to find in PATH
            path_result = find_app_in_path(app)
            if path_result:
                cmd = path_result
            else:
                # Try as direct executable
                cmd = app

    try:
        if platform.system() == "Windows":
            subprocess.Popen(
                f'start "" "{cmd}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen([cmd])

        return f"🚀 Opened {app_name}"

    except Exception as e:
        return f"❌ Could not open {app_name}. Try a different name or check if it's installed."
