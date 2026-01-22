#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLU (Natural Language Understanding) Test
Tests command variations with fuzzy matching
"""

from core.brain import understand
from core.executor import execute

print("=" * 70)
print("JARVIS - Natural Language Understanding Test")
print("=" * 70)

# Test cases with variations
test_cases = [
    # System commands (should work)
    ("pwd", "system", "Basic pwd command"),
    ("show current directory", "system", "Variation: show current directory"),
    ("ls", "system", "Basic ls command"),
    ("list files", "system", "Variation: list files"),
    
    # Open app variations
    ("open chrome", "open_app", "Basic: open chrome"),
    ("launch firefox", "open_app", "Variation: launch firefox"),
    ("start vscode", "open_app", "Variation: start vscode"),
    ("run notepad++", "open_app", "Variation: run notepad++"),
    
    # Open file variations
    ("open jarvis.py", "open_file", "Basic: open jarvis.py"),
    ("show config.yaml", "open_file", "Variation: show config.yaml"),
    ("view README.md", "open_file", "Variation: view README.md"),
    
    # Navigation variations
    ("cd users", "system", "Basic: cd users"),
    ("go to desktop", "system", "Variation: go to desktop"),
    ("navigate to ai", "system", "Variation: navigate to ai"),
    
    # Bluetooth variations
    ("connect to airpods", "system_control", "Variation: connect to airpods"),
    ("pair with mouse", "system_control", "Variation: pair with mouse"),
    
    # WiFi variations
    ("connect to wifi Home", "system_control", "Variation: connect to wifi Home"),
    ("join network MyWifi", "system_control", "Variation: join network MyWifi"),
    
    # Knowledge variations
    ("what is python", "knowledge", "Basic: what is python"),
    ("tell me about flutter", "knowledge", "Variation: tell me about flutter"),
    ("explain nodejs", "knowledge", "Variation: explain nodejs"),
    
    # Chat
    ("hello", "chat", "Basic: hello"),
]

print("\n[*] Testing Command Understanding with NLU:\n")

passed = 0
failed = 0

for cmd, expected_intent, description in test_cases:
    try:
        result = understand(cmd)
        actual_intent = result.get("intent", "unknown")
        
        if actual_intent == expected_intent:
            print("[OK] %s" % description)
            print("     Command: '%s' -> %s" % (cmd, actual_intent))
            if "parsed_data" in result and result["parsed_data"]:
                print("     Parsed: %s" % result["parsed_data"])
            passed += 1
        else:
            print("[FAIL] %s" % description)
            print("       Command: '%s' -> %s (expected %s)" % (cmd, actual_intent, expected_intent))
            failed += 1
    except Exception as e:
        print("[ERROR] %s - %s" % (description, str(e)))
        failed += 1
    
    print()

print("=" * 70)
print("Results: %d passed, %d failed out of %d tests" % (passed, failed, len(test_cases)))
print("=" * 70)

# Test execution with variations
print("\n[*] Testing Command Execution with NLU:\n")

execution_tests = [
    "hello",
    "pwd",
    "what is python",
]

for cmd in execution_tests:
    try:
        intent = understand(cmd)
        result = execute(intent)
        print("[OK] Executed: '%s'" % cmd)
        print("     Result: %s..." % str(result)[:60])
    except Exception as e:
        print("[FAIL] Failed: '%s' - %s" % (cmd, str(e)))
    print()

print("=" * 70)
print("[OK] NLU Enhancement testing complete!")
print("=" * 70)
