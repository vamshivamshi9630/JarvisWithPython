import re
from skills.chat import is_greeting, is_small_talk

# ---------- FILE OPEN PATTERNS ----------
FILE_OPEN_PATTERNS = [
    r"^open\s+(.+?)\s+in\s+(.+)$",
    r"^open\s+(.+?)\s+using\s+(.+)$",
    r"^open\s+(.+?)\s+with\s+(.+)$",
]

# ---------- SYSTEM COMMANDS (Local execution) ----------
SYSTEM_CMDS = {
    "cls": ("cls", None),
    "clear": ("cls", None),
    "run cls": ("cls", None),

    "pwd": ("pwd", None),
    "current dir": ("pwd", None),
    "current directory": ("pwd", None),

    "ls": ("ls", None),
    "list": ("ls", None),
    "dir": ("ls", None),
    "show files": ("ls", None),
    "run ls": ("ls", None),
    "run dir": ("run dir", None),
}

# ---------- APPLICATIONS (Always local) ----------
LOCAL_APPS = {
    "chrome", "browser", "vscode", "code", "vs code", "notepad++", 
    "notepad plus plus", "file explorer", "explorer", "edge", "microsoft edge",
    "teams", "microsoft teams", "cmd", "command prompt", "powershell", "pwsh",
    "terminal", "git bash", "qt", "qt creator", "sourcetree", "git", "github",
    "slack", "discord", "telegram", "whatsapp", "zoom", "skype",
    "vlc", "media player", "vlc media player", "spotify", "steam", "epic games",
    "blender", "gimp", "photoshop", "firefox", "safari", "opera", "brave"
}

# ---------- SYSTEM CONTROLS ----------
SYSTEM_CONTROLS = {
    # Bluetooth
    "bluetooth on": ("bluetooth", "on"),
    "turn on bluetooth": ("bluetooth", "on"),
    "enable bluetooth": ("bluetooth", "on"),
    "bluetooth off": ("bluetooth", "off"),
    "turn off bluetooth": ("bluetooth", "off"),
    "disable bluetooth": ("bluetooth", "off"),
    "list bluetooth": ("list_bluetooth", None),
    "list bluetooth devices": ("list_bluetooth", None),
    "show bluetooth devices": ("list_bluetooth", None),
    "check bluetooth devices": ("list_bluetooth", None),
    "scan bluetooth": ("list_bluetooth", None),
    
    # WiFi
    "wifi on": ("wifi", "on"),
    "turn on wifi": ("wifi", "on"),
    "enable wifi": ("wifi", "on"),
    "wifi off": ("wifi", "off"),
    "turn off wifi": ("wifi", "off"),
    "disable wifi": ("wifi", "off"),
    "list wifi": ("list_wifi", None),
    "list wifi networks": ("list_wifi", None),
    "show wifi networks": ("list_wifi", None),
    "scan wifi": ("list_wifi", None),
    "available networks": ("list_wifi", None),
    
    # Volume
    "volume up": ("volume", "increase"),
    "increase volume": ("volume", "increase"),
    "turn up volume": ("volume", "increase"),
    "louder": ("volume", "increase"),
    "volume down": ("volume", "decrease"),
    "decrease volume": ("volume", "decrease"),
    "turn down volume": ("volume", "decrease"),
    "quieter": ("volume", "decrease"),
    "mute": ("volume", "mute"),
    "mute volume": ("volume", "mute"),
    "unmute": ("volume", "unmute"),
    "unmute volume": ("volume", "unmute"),
    
    # Brightness
    "brightness up": ("brightness", "increase"),
    "increase brightness": ("brightness", "increase"),
    "brighter": ("brightness", "increase"),
    "brightness down": ("brightness", "decrease"),
    "decrease brightness": ("brightness", "decrease"),
    "darker": ("brightness", "decrease"),
    
    # Screen
    "lock": ("lock", ""),
    "lock screen": ("lock", ""),
    "lock computer": ("lock", ""),
    "sleep": ("sleep", ""),
    "put to sleep": ("sleep", ""),
    "computer sleep": ("sleep", ""),
    
    # Power
    "shutdown": ("shutdown", "0"),
    "shut down": ("shutdown", "0"),
    "power off": ("shutdown", "0"),
    "turn off": ("shutdown", "0"),
    "restart": ("restart", "0"),
    "reboot": ("restart", "0"),
    
    # Airplane mode
    "airplane on": ("airplane", "on"),
    "airplane mode on": ("airplane", "on"),
    "enable airplane": ("airplane", "on"),
    "airplane off": ("airplane", "off"),
    "airplane mode off": ("airplane", "off"),
    "disable airplane": ("airplane", "off"),
}

# ---------- KNOWLEDGE PREFIXES (Goes to OpenAI) ----------
KNOWLEDGE_PREFIXES = (
    "what is",
    "explain",
    "tell me",
    "how to",
    "why",
    "what",
    "who",
    "when",
    "where",
    "google",
    "search",
)

def understand(command: str):
    if not command:
        return {"intent": "unknown"}

    cmd = command.lower().strip()

    # ---------- GREETINGS & CHAT ----------
    if is_greeting(cmd) or is_small_talk(cmd):
        return {"intent": "chat", "query": command}

    # ---------- SYSTEM CONTROLS ----------
    if cmd in SYSTEM_CONTROLS:
        control, action = SYSTEM_CONTROLS[cmd]
        return {"intent": "system_control", "control": control, "action": action}
    
    # NOTE: Specific volume/brightness levels don't work reliably on Windows
    # Only volume up/down and brightness up/down work (keyboard shortcuts)

    # ---------- SYSTEM COMMANDS ----------
    if cmd in SYSTEM_CMDS:
        action, _ = SYSTEM_CMDS[cmd]
        return {"intent": "system", "action": action}

    # ---------- CD / NAVIGATION ----------
    if cmd.startswith(("cd ", "go to ", "run cd ")):
        path = (
            cmd.replace("run", "")
               .replace("go to", "")
               .replace("cd", "")
               .strip()
        )
        
        # Map common patterns
        path_map = {
            "c": "C:\\",
            "c:": "C:\\",
            "c drive": "C:\\",
            "users": "C:\\Users",
            "desktop": "C:\\Users\\KudikalaVamshi\\Desktop",
            "ai": "ai",  # Relative path
            "skills": "skills",  # Relative path
            "core": "core",  # Relative path
        }
        
        path = path_map.get(path, path)
        return {"intent": "system", "action": "cd", "path": path}

    # ---------- OPEN FILE IN APP ----------
    for pattern in FILE_OPEN_PATTERNS:
        m = re.match(pattern, cmd)
        if m:
            return {
                "intent": "open_file",
                "file": m.group(1).strip(),
                "app": m.group(2).strip()
            }

    # ---------- OPEN FILE (DEFAULT EDITOR) ----------
    if cmd.startswith("open ") and "." in cmd:
        file_name = cmd.replace("open", "").strip()
        return {
            "intent": "open_file",
            "file": file_name,
            "app": None
        }

    # ---------- OPEN APPLICATION ----------
    if cmd.startswith("open "):
        target = cmd.replace("open", "").strip()
        
        # All open commands go to app_opener (it will handle smart detection)
        return {"intent": "open_app", "target": target}

    # ---------- CONNECT TO BLUETOOTH DEVICE ----------
    if cmd.startswith(("connect to ", "connect device ", "pair with ")):
        # Extract device name
        device_name = cmd.replace("connect to", "").replace("connect device", "").replace("pair with", "").strip()
        device_name = device_name.strip('"\'')  # Remove quotes if present
        return {"intent": "system_control", "control": "connect_bluetooth", "device": device_name}
    
    # ---------- CONNECT TO WIFI NETWORK ----------
    if cmd.startswith(("connect to wifi ", "connect to network ", "connect wifi ")):
        # Extract network name
        network_name = cmd.replace("connect to wifi", "").replace("connect to network", "").replace("connect wifi", "").strip()
        network_name = network_name.strip('"\'')  # Remove quotes if present
        return {"intent": "system_control", "control": "connect_wifi", "network": network_name}

    # ---------- KNOWLEDGE QUERIES (Send to OpenAI) ----------
    # Check for knowledge prefixes or standalone topics
    if cmd.startswith(KNOWLEDGE_PREFIXES):
        return {"intent": "knowledge", "query": command}
    
    # Check for single/multi-word topics that aren't commands
    # Exclude very short system-like words and reserved commands
    excluded_words = {"cd", "ls", "dir", "pwd", "cls", "run", "go", "open", "exit", "help"}
    first_word = cmd.split()[0] if cmd else ""
    
    if first_word and first_word not in excluded_words:
        # It's likely a knowledge query
        return {"intent": "knowledge", "query": command}

    return {"intent": "unknown"}
