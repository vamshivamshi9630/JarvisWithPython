import re
from skills.chat import is_greeting, is_small_talk
from ai.nlu import nlu, understand_command
from ai.ml_intent import detect_intent

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
    "scan bluetooth devices": ("list_bluetooth", None),
    "show available bluetooth": ("list_bluetooth", None),
    "available bluetooth": ("list_bluetooth", None),
    
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
    "show available wifi": ("list_wifi", None),
    "show available wifis": ("list_wifi", None),
    "show available wifi networks": ("list_wifi", None),
    "show available networks": ("list_wifi", None),
    "scan wifi": ("list_wifi", None),
    "available networks": ("list_wifi", None),
    "list networks": ("list_wifi", None),
    "show networks": ("list_wifi", None),
    
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
    "turn on airplane": ("airplane", "on"),
    "turn on aeroplane": ("airplane", "on"),
    "turn on aeroplane mode": ("airplane", "on"),
    "aeroplane mode on": ("airplane", "on"),
    "aeroplane on": ("airplane", "on"),
    "airplane off": ("airplane", "off"),
    "airplane mode off": ("airplane", "off"),
    "disable airplane": ("airplane", "off"),
    "turn off airplane": ("airplane", "off"),
    "turn off aeroplane": ("airplane", "off"),
    "aeroplane off": ("airplane", "off"),
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
    
    # FLEXIBLE SYNTAX: Support both "run cmd" and "cmd" syntax
    # Try without "run" prefix if it exists
    if cmd.startswith("run "):
        # Extract command without "run" prefix
        base_cmd = cmd[4:].strip()
        base_command = command[4:].strip()  # Keep original case for some operations
        
        # Try understanding the base command
        base_result = understand_base(base_cmd, base_command)
        if base_result.get("intent") != "unknown":
            return base_result
    
    # Try understanding as-is
    return understand_base(cmd, command)


def understand_base(cmd: str, command: str):
    """
    Base command understanding logic
    Args:
        cmd: lowercase stripped command
        command: original command (preserving case where needed)
    """
    if not cmd:
        return {"intent": "unknown"}

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
    
    # Support for common system command variations
    system_variations = {
        "show files": ("ls", None),
        "list files": ("ls", None),
        "show current directory": ("pwd", None),
        "list directory": ("ls", None),
    }
    
    if cmd in system_variations:
        action, _ = system_variations[cmd]
        return {"intent": "system", "action": action}

    # ---------- CD / NAVIGATION ----------
    if cmd.startswith(("cd ", "go to ", "run cd ", "navigate to ", "go into ")):
        # Use NLU for better extraction
        nlu_result = understand_command(cmd, "system")
        path = None
        
        if "directory" in nlu_result["parsed_data"]:
            path = nlu_result["parsed_data"]["directory"]
        else:
            # Fallback
            path = (
                cmd.replace("run", "")
                   .replace("navigate to", "")
                   .replace("go into", "")
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
    if cmd.startswith(("open ", "show ", "view ", "read ", "edit ")) and "." in cmd:
        file_name = None
        # Use NLU to extract file name more intelligently
        nlu_result = understand_command(cmd, "open_file")
        if "file_name" in nlu_result["parsed_data"]:
            file_name = nlu_result["parsed_data"]["file_name"]
        else:
            # Fallback parsing
            for prefix in ["open ", "show ", "view ", "read ", "edit "]:
                if cmd.startswith(prefix):
                    file_name = cmd.replace(prefix, "").strip()
                    break
        
        if file_name:
            return {
                "intent": "open_file",
                "file": file_name,
                "app": None
            }

    # ---------- OPEN APPLICATION ----------
    if cmd.startswith(("open ", "launch ", "run ", "start ")):
        # Use NLU to extract app name intelligently
        nlu_result = understand_command(cmd, "open_app")
        target = None
        
        if "app_name" in nlu_result["parsed_data"]:
            target = nlu_result["parsed_data"]["app_name"]
        else:
            # Fallback to original method
            for prefix in ["open ", "launch ", "run ", "start "]:
                if cmd.startswith(prefix):
                    target = cmd.replace(prefix, "").strip()
                    break
        
        if target:
            return {"intent": "open_app", "target": target}
    
    # ---------- FUZZY MATCH APP NAMES (Handle typos like "ntepad++", "chrom", "vscod") ----------
    from difflib import get_close_matches
    from skills.app_opener import APP_COMMANDS
    
    # Try to match typos against known apps
    cmd_lower = cmd.lower().strip()
    close_matches = get_close_matches(cmd_lower, APP_COMMANDS.keys(), n=1, cutoff=0.70)
    if close_matches:
        # This looks like an app name with a typo
        return {"intent": "open_app", "target": cmd}

    # ---------- CONNECT TO BLUETOOTH DEVICE ----------
    if cmd.startswith(("connect to ", "connect device ", "pair with ", "connect ", "pair ", "connect bluetooth to ", "connect to bluetooth ")):
        # Use NLU to extract device name more intelligently
        nlu_result = understand_command(cmd, "connect_device")
        device_name = None
        
        if "device_name" in nlu_result["parsed_data"]:
            device_name = nlu_result["parsed_data"]["device_name"]
        else:
            # Fallback to original method - remove all prefixes
            device_name = cmd
            for prefix in ["connect to bluetooth ", "connect bluetooth to ", "connect to ", "connect device ", "pair with ", "pair ", "connect "]:
                if device_name.startswith(prefix):
                    device_name = device_name[len(prefix):].strip()
                    break
            device_name = device_name.strip('"\'')
        
        if device_name:
            return {"intent": "system_control", "control": "connect_bluetooth", "device": device_name}
    
    # ---------- CONNECT TO WIFI NETWORK ----------
    if cmd.startswith(("connect to wifi ", "connect to network ", "connect wifi ", "join wifi ", "join network ", "connect to ", "wifi to ")):
        # Use NLU to extract network name more intelligently
        nlu_result = understand_command(cmd, "connect_wifi")
        network_name = None
        
        if "network_name" in nlu_result["parsed_data"]:
            network_name = nlu_result["parsed_data"]["network_name"]
        else:
            # Fallback to original method - remove all prefixes
            network_name = cmd
            for prefix in ["connect to wifi ", "connect to network ", "connect wifi ", "join wifi ", "join network ", "connect to ", "wifi to ", "network to "]:
                if network_name.startswith(prefix):
                    network_name = network_name[len(prefix):].strip()
                    break
            network_name = network_name.strip('"\'')
        
        if network_name:
            return {"intent": "system_control", "control": "connect_wifi", "network": network_name}

    # ---------- KNOWLEDGE QUERIES (Send to OpenAI) ----------
    # Check for knowledge prefixes or standalone topics
    if cmd.startswith(KNOWLEDGE_PREFIXES):
        # Use NLU to clean up the query
        nlu_result = understand_command(cmd, "knowledge")
        query = nlu_result["parsed_data"].get("query", command)
        return {"intent": "knowledge", "query": query}
    
    # Check for single/multi-word topics that aren't commands
    # Exclude very short system-like words and reserved commands
    excluded_words = {"cd", "ls", "dir", "pwd", "cls", "run", "go", "open", "exit", "help"}
    first_word = cmd.split()[0] if cmd else ""
    
    # Don't send very short strings (likely typos) to knowledge
    # Only single/double letter combos or very short queries go to knowledge
    is_likely_typo = len(cmd) < 4 and " " not in cmd
    is_knowledge_like = any(prefix in cmd for prefix in ["what", "how", "why", "explain", "tell me", "search"])
    
    if first_word and first_word not in excluded_words and not is_likely_typo:
        # It's likely a knowledge query
        if is_knowledge_like or len(cmd.split()) == 1:
            return {"intent": "knowledge", "query": command}

    # ML FALLBACK: Use machine learning to classify unknown commands
    ml_result = detect_intent(command)
    if ml_result["intent"] != "unknown" and ml_result["confidence"] >= 50:
        # High confidence ML prediction
        if ml_result["intent"] == "system":
            # Try to extract action from ML context
            cmd_lower = command.lower().strip()
            if "run" in cmd_lower:
                # Remove "run" prefix and try again
                cleaned_cmd = cmd_lower.replace("run", "").strip()
                if cleaned_cmd in SYSTEM_CMDS:
                    action, _ = SYSTEM_CMDS[cleaned_cmd]
                    return {"intent": "system", "action": action}
            return {"intent": "system", "action": cmd_lower}
        elif ml_result["intent"] == "open_app":
            # Extract app name
            app_name = cmd.replace("run", "").strip()
            return {"intent": "open_app", "target": app_name}
        elif ml_result["intent"] == "knowledge":
            return {"intent": "knowledge", "query": command}
        elif ml_result["intent"] == "system_control_connect":
            if "bluetooth" in cmd.lower():
                device = cmd.replace("connect", "").replace("pair", "").replace("with", "").strip()
                return {"intent": "system_control", "control": "connect_bluetooth", "device": device}
            else:
                network = cmd.replace("connect", "").replace("join", "").replace("wifi", "").replace("network", "").strip()
                return {"intent": "system_control", "control": "connect_wifi", "network": network}

    return {"intent": "unknown"}
