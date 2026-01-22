#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ML Intent Detection Test
Tests machine learning-based command classification
"""

from core.brain import understand
from core.executor import execute
from ai.ml_intent import detect_intent

print("=" * 70)
print("JARVIS - ML Intent Detection Test")
print("=" * 70)

# Test 1: Direct ML intent detection
print("\n[*] Testing ML Intent Detection:")
print("-" * 70)

test_commands = [
    "ls",
    "pwd",
    "open chrome",
    "open jarvis.py",
    "connect to airpods",
    "what is python",
    "hello",
]

for cmd in test_commands:
    ml_result = detect_intent(cmd)
    print("[ML] '%s'" % cmd)
    print("     Intent: %s (Confidence: %.1f%%)" % (ml_result["intent"], ml_result["confidence"]))

# Test 2: Flexible syntax (with/without "run")
print("\n[*] Testing Flexible Command Syntax:")
print("-" * 70)

syntax_tests = [
    ("pwd", "system"),
    ("run pwd", "system"),
    ("ls", "system"),
    ("run ls", "system"),
    ("open chrome", "open_app"),
    ("run open chrome", "open_app"),
]

for cmd, expected_intent in syntax_tests:
    result = understand(cmd)
    actual_intent = result.get("intent")
    status = "[OK]" if actual_intent == expected_intent else "[FAIL]"
    print("%s '%s' -> %s" % (status, cmd, actual_intent))

# Test 3: Brain understanding with ML fallback
print("\n[*] Testing Brain with ML Fallback:")
print("-" * 70)

ml_fallback_tests = [
    "list files",
    "show current directory",
    "launch firefox",
    "what is ai",
]

for cmd in ml_fallback_tests:
    result = understand(cmd)
    print("[Brain] '%s'" % cmd)
    print("        Intent: %s" % result.get("intent"))

# Test 4: Execution with new syntax
print("\n[*] Testing Execution with New Syntax:")
print("-" * 70)

execution_tests = [
    "hello",
    "pwd",
    "run pwd",
]

for cmd in execution_tests:
    try:
        result_dict = understand(cmd)
        exec_result = execute(result_dict)
        print("[OK] '%s' executed" % cmd)
    except Exception as e:
        print("[FAIL] '%s' - %s" % (cmd, str(e)))

print("\n" + "=" * 70)
print("[OK] ML Intent Detection testing complete!")
print("=" * 70)
