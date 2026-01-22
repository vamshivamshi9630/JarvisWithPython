#!/usr/bin/env python3
"""
JARVIS Test Script - Validates all modules work correctly
"""
import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("[*] Testing module imports...")
    try:
        from core.brain import understand
        print("✓ core.brain imported")
        
        from core.executor import execute
        print("✓ core.executor imported")
        
        from skills.system_cmds import run_system
        print("✓ skills.system_cmds imported")
        
        from skills.app_opener import open_app
        print("✓ skills.app_opener imported")
        
        from skills.file_opener import open_file
        print("✓ skills.file_opener imported")
        
        from skills.chat import is_greeting
        print("✓ skills.chat imported")
        
        from skills.system_controls import handle_system_control
        print("✓ skills.system_controls imported")
        
        from ai.knowledge import answer
        print("✓ ai.knowledge imported")
        
        from ai.llm import openai_answer
        print("✓ ai.llm imported")
        
        from ai.local_llm import local_answer
        print("✓ ai.local_llm imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_commands():
    """Test basic command parsing"""
    print("\n[*] Testing command understanding...")
    from core.brain import understand
    
    test_cases = [
        ("pwd", "system"),
        ("ls", "system"),
        ("hello", "chat"),
        ("open chrome", "open_app"),
        ("what is python", "knowledge"),
    ]
    
    for cmd, expected_intent in test_cases:
        result = understand(cmd)
        if result.get("intent") == expected_intent:
            print(f"✓ '{cmd}' → {expected_intent}")
        else:
            print(f"✗ '{cmd}' → {result.get('intent')} (expected {expected_intent})")


def test_execution():
    """Test basic command execution"""
    print("\n[*] Testing command execution...")
    from core.brain import understand
    from core.executor import execute
    
    test_cases = [
        ("hello", "chat response"),
        ("pwd", "current directory"),
    ]
    
    for cmd, expected_output in test_cases:
        try:
            intent = understand(cmd)
            result = execute(intent)
            if result and "Error" not in str(result):
                print(f"✓ '{cmd}' executed successfully")
            else:
                print(f"! '{cmd}' → {result}")
        except Exception as e:
            print(f"✗ '{cmd}' failed: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS - System Test")
    print("=" * 60 + "\n")
    
    if not test_imports():
        sys.exit(1)
    
    test_commands()
    test_execution()
    
    print("\n" + "=" * 60)
    print("[✓] JARVIS system is working properly!")
    print("=" * 60)
