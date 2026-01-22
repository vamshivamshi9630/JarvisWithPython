#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Complete Feature Demonstration
Shows all new ML and flexible syntax features
"""

from core.brain import understand
from core.executor import execute

print("=" * 80)
print("JARVIS - Complete Feature Demonstration")
print("=" * 80)

demo_commands = [
    # Flexible Syntax - with and without "run"
    ("pwd", "Show current directory"),
    ("run pwd", "Same command with 'run' prefix"),
    ("ls", "List files"),
    ("run ls", "List files with 'run' prefix"),
    
    # NLU - Command variations
    ("show current directory", "NLU variation of pwd"),
    ("list files", "NLU variation of ls"),
    ("launch firefox", "NLU variation of open app"),
    ("navigate to users", "NLU variation of cd"),
    
    # ML Intent Detection - Edge cases
    ("dir", "System command"),
    ("hello", "Chat greeting"),
    ("what is python", "Knowledge query"),
    
    # Open apps and files
    ("open chrome", "Open application"),
    ("open jarvis.py", "Open file"),
    ("open config.yaml in notepad++", "Open file with editor"),
    
    # System control
    ("volume up", "Increase volume"),
    ("connect to airpods", "Connect Bluetooth device"),
    
    # Complex commands
    ("run open chrome", "Run with open app"),
    ("run list", "Run with list command"),
]

print("\n[Demo] Testing command variations and ML detection:\n")

for cmd, description in demo_commands:
    try:
        # Understand the command
        intent_result = understand(cmd)
        intent = intent_result.get("intent", "unknown")
        
        # Try to execute
        exec_result = execute(intent_result)
        
        # Show results
        print("[%s]" % intent.upper())
        print("  Command: '%s'" % cmd)
        print("  Description: %s" % description)
        if exec_result:
            result_str = str(exec_result)
            if len(result_str) > 70:
                result_str = result_str[:67] + "..."
            print("  Result: %s" % result_str)
        print()
        
    except Exception as e:
        print("[ERROR]")
        print("  Command: '%s'" % cmd)
        print("  Error: %s" % str(e)[:60])
        print()

print("=" * 80)
print("[OK] Feature demonstration complete!")
print("=" * 80)

print("\n[Summary of New Features]:\n")
print("1. ML-BASED INTENT DETECTION")
print("   - Keyword-based machine learning classifier")
print("   - No heavy dependencies (pure Python)")
print("   - Trained on command patterns")
print("   - Fallback for unknown commands")
print()

print("2. FLEXIBLE COMMAND SYNTAX")
print("   - Commands work WITH or WITHOUT 'run' prefix")
print("   - Examples:")
print("     * 'pwd' and 'run pwd' both work")
print("     * 'ls' and 'run ls' both work")
print("     * 'open chrome' and 'run open chrome' both work")
print()

print("3. NATURAL LANGUAGE UNDERSTANDING (NLU)")
print("   - Command variations recognized")
print("   - Examples:")
print("     * 'pwd' / 'show current directory' / 'current dir'")
print("     * 'ls' / 'list files' / 'show files'")
print("     * 'open' / 'launch' / 'run' / 'start' for apps")
print()

print("=" * 80)
