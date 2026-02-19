#!/usr/bin/env python3
"""Validate router classification changes"""
import sys
sys.path.insert(0, '/mnt/d/Personal_project/JarvisWithPython')

from core.router import Router

# Test system info routing
test_cases = [
    ('battery', 'direct_action'),
    ('cpu usage', 'direct_action'),
    ('disk space', 'direct_action'),
    ('ip address', 'direct_action'),
    ('is chrome running', 'direct_action'),
    ('toggle wifi', 'direct_action'),
    ('brightness 50', 'direct_action'),
    ('set volume 75', 'direct_action'),
    ('hello', 'chat'),
    ('thanks', 'chat')
]

print("Router Classification Test Results")
print("=" * 60)

passed = 0
failed = 0

for test_input, expected_route in test_cases:
    actual_route = Router.classify(test_input)
    status = "PASS" if actual_route == expected_route else "FAIL"
    
    if status == "PASS":
        passed += 1
    else:
        failed += 1
    
    print(f"{status:5} | {test_input:25} -> {actual_route:20} (expect: {expected_route})")

print("=" * 60)
print(f"Results: {passed} passed, {failed} failed")

if failed > 0:
    sys.exit(1)
