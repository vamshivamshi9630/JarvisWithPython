#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Typo Handling & Command Variations Test
Tests improved fuzzy matching and command recognition
"""

from core.brain import understand
from core.executor import execute

print("=" * 80)
print("JARVIS - Typo Handling & Command Variations Test")
print("=" * 80)

test_cases = [
    # Typo corrections
    ("ntepad++", "open_app", "Typo: ntepad++ -> notepad++"),
    ("chrom", "open_app", "Typo: chrom -> chrome"),
    ("vscod", "open_app", "Typo: vscod -> vscode"),
    
    # Misspelled greetings (should NOT go to knowledge)
    ("hlo", "chat", "Typo: hlo (should be hello)"),
    ("hi", "chat", "Correct: hi"),
    
    # WiFi variations
    ("show available wifi networks", "system_control", "WiFi: show available networks"),
    ("show available wifis", "system_control", "WiFi: show available wifis"),
    ("list networks", "system_control", "WiFi: list networks"),
    ("show networks", "system_control", "WiFi: show networks"),
    ("scan wifi", "system_control", "WiFi: scan wifi"),
    
    # Bluetooth variations
    ("scan bluetooth devices", "system_control", "BT: scan bluetooth devices"),
    ("show available bluetooth", "system_control", "BT: show available bluetooth"),
    ("check bluetooth devices", "system_control", "BT: check bluetooth devices"),
    
    # Connection variations
    ("connect to vamshi", "system_control", "Connect: to device vamshi"),
    ("connect bluetooth to buds", "system_control", "Connect: bluetooth to buds"),
    ("connect wifi to Vamshi", "system_control", "Connect: wifi to Vamshi"),
    ("wifi to home network", "system_control", "Connect: wifi to home network"),
    
    # Airplane mode
    ("turn on aeroplane mode", "system_control", "Airplane: turn on aeroplane"),
    ("aeroplane off", "system_control", "Airplane: aeroplane off"),
    
    # Navigation
    ("go to c drive", "system", "Navigation: go to c drive"),
]

print("\n[Testing Command Recognition with Typos & Variations]:\n")

passed = 0
failed = 0

for cmd, expected_intent, description in test_cases:
    try:
        result = understand(cmd)
        actual_intent = result.get("intent")
        
        if actual_intent == expected_intent:
            print("[OK] %s" % description)
            passed += 1
        else:
            print("[FAIL] %s" % description)
            print("       Got: %s (expected %s)" % (actual_intent, expected_intent))
            failed += 1
    except Exception as e:
        print("[ERROR] %s - %s" % (description, str(e)[:60]))
        failed += 1

print("\n" + "=" * 80)
print("Results: %d passed, %d failed out of %d tests" % (passed, failed, len(test_cases)))
print("=" * 80)

# Test execution
print("\n[Testing Execution with Typos]:\n")

exec_tests = [
    "hi",
    "hlo",
    "list networks",
    "scan bluetooth devices",
]

for cmd in exec_tests:
    try:
        result = understand(cmd)
        exec_result = execute(result)
        print("[OK] '%s' executed" % cmd)
    except Exception as e:
        print("[FAIL] '%s' - %s" % (cmd, str(e)[:60]))

print("\n" + "=" * 80)
print("[OK] Typo handling testing complete!")
print("=" * 80)
