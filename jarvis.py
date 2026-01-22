#!/usr/bin/env python3
"""
JARVIS - AI Personal Assistant
Intelligently routes commands to local execution or OpenAI knowledge queries
"""

import os
import sys

# ==================== ADMIN PRIVILEGE CHECK ====================
def is_admin():
    """Check if running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Show warning if running without admin
if not is_admin():
    print("\n[!] JARVIS is running WITHOUT Administrator privileges.")
    print("[*] WiFi and Bluetooth control will NOT work.")
    print("[*] To enable full features:")
    print("    - Windows: Run 'run_as_admin.vbs' (double-click)")
    print("    - PowerShell: Right-click jarvis.py > 'Run as administrator'")
    print("\n")

# ==================== JARVIS STARTS HERE ====================


# ==================== JARVIS STARTS HERE ====================

from core.brain import understand
from core.executor import execute

print("=" * 60)
print("JARVIS - AI Personal Assistant")
print("="*60)
print("\nCommand Types:")
print("  * System: ls, pwd, dir, cls")
print("  * Navigation: cd users, go to c, go to ai")
print("  * Apps: open chrome, open vscode, open notepad++")
print("  * Files: open jarvis.py, open config.yaml in notepad++")
print("  * Knowledge: flutter, what is flutter, explain python")
print("\nType 'exit' to quit, 'help' for more info")
print("=" * 60 + "\n")

while True:
    try:
        cmd = input("You > ").strip()
        
        if not cmd:
            continue
            
        if cmd.lower() == "exit":
            print("[*] Goodbye!")
            break
            
        if cmd.lower() == "help":
            print("""
JARVIS Help:

SYSTEM COMMANDS:
  ls, dir, list          -> List files
  pwd                    -> Current directory
  cls, clear             -> Clear screen
  
NAVIGATION:
  cd <path>              -> Change directory
  go to <path>           -> Change directory
  go to c                -> Go to C: drive
  go to ai               -> Go to JARVIS folder
  
APPS:
  open chrome            -> Open browser
  open vscode            -> Open VS Code
  open notepad++         -> Open Notepad++
  open file explorer     -> Open File Explorer
  
FILES:
  open <filename>        -> Open file
  open <file> in <app>   -> Open with specific app
  
KNOWLEDGE QUERIES:
  flutter                -> Ask about Flutter
  what is <topic>        -> What is...
  explain <topic>        -> Explain topic
  how to <task>          -> How to do something
  <topic>                -> Generic knowledge query
            """)
            continue

        # Process command through AI
        intent = understand(cmd)
        result = execute(intent)

        if result:
            print(result)
            
    except KeyboardInterrupt:
        print("\n[*] Interrupted. Goodbye!")
        break
    except Exception as e:
        print(f"[!] Error: {e}")

