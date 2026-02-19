#!/usr/bin/env python3
"""
Self-Learning Memory Store - Practical Examples

Real-world usage examples showing how to use the learning system.
Run this file to see demonstrations of all features.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.memory_store import get_memory_store
from core.context import ContextManager


def example_1_learn_preferences():
    """Example: Learning user preferences"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 1: Learning & Storing User Preferences                       ║
╚════════════════════════════════════════════════════════════════════════╝

When JARVIS learns about your preferences, it can use them in planning
and decision-making.
    """)
    
    memory = get_memory_store()
    
    # Learn preferences
    memory.learn_preference("preferred_browser", "Firefox")
    memory.learn_preference("preferred_editor", "VSCode")
    memory.learn_preference("preferred_shell", "PowerShell")
    memory.learn_preference("work_hours_start", "09:00")
    memory.learn_preference("dark_mode_enabled", True)
    
    print("\n✓ Learned 5 preferences:\n")
    
    prefs = memory.get_all_preferences()
    for key, value in prefs.items():
        print(f"   {key:.<35} {value}")
    
    # Retrieve single preference
    browser = memory.get_preference("preferred_browser")
    print(f"\n✓ Retrieved preference: preferred_browser = {browser}")
    
    print("""
These preferences are automatically included in the Planner's context,
so all plans respect them.
    """)


def example_2_track_tool_usage():
    """Example: Tracking tool effectiveness"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 2: Analyzing Tool Effectiveness                              ║
╚════════════════════════════════════════════════════════════════════════╝

JARVIS tracks which tools work best for different tasks. This helps
improve planning and tool selection over time.
    """)
    
    memory = get_memory_store()
    
    # Simulate tool usage (opening Chrome multiple times)
    print("\n→ Simulating 15 tool executions...\n")
    
    success_count = 0
    for i in range(15):
        # 13 successes, 2 failures (realistic scenario)
        success = i not in [5, 12]
        success_count += 1 if success else 0
        
        memory.record_tool_outcome(
            tool_name="open_application",
            task_type="browser_launch",
            parameters={"app": "Chrome", "profile": "default"},
            success=success,
            execution_time=0.8 + (0.1 * i)
        )
    
    # Analyze effectiveness
    stats = memory.get_tool_effectiveness("open_application")
    
    print(f"✓ Tool Usage Statistics:\n")
    print(f"   Total Uses:        {stats['total_uses']}")
    print(f"   Success Rate:      {stats['success_rate']:.1%}")
    print(f"   Avg Execution:     {stats['avg_execution_time']:.2f}s")
    
    if stats['task_types']:
        print(f"\n   By Task Type:")
        for task, rate in stats['task_types'].items():
            print(f"     - {task}: {rate:.1%}")
    
    print("""
With this data, JARVIS can decide:
  - Which tool is most reliable for this task
  - Whether to use this tool or try alternatives
  - Estimated execution time
    """)


def example_3_auto_learning():
    """Example: Automatic learning from execution"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 3: Automatic Learning from Successful Execution              ║
╚════════════════════════════════════════════════════════════════════════╝

When a user command executes successfully, JARVIS learns the mapping
automatically. Confidence increases with each successful use.
    """)
    
    memory = get_memory_store()
    
    user_command = "open my downloads folder"
    action = "open_folder"
    parameters = {"path": "C:\\Users\\{user}\\Downloads", "show_in_explorer": True}
    
    print(f"\nUser says: \"{user_command}\"")
    print(f"Executes:  {action}")
    print(f"Params:    {parameters}\n")
    
    # Simulate 4 successful executions
    confidence_progression = []
    for attempt in range(1, 5):
        memory.learn_from_execution(
            user_input=user_command,
            action=action,
            parameters=parameters,
            success=True,
            execution_time=0.6
        )
        
        mapping = memory.find_phrase_mapping(user_command.lower().strip())
        confidence = mapping['confidence'] if mapping else 0
        confidence_progression.append(confidence)
        
        print(f"   Attempt {attempt}: Confidence = {confidence:.1%}")
    
    print(f"""
After 4 uses, confidence is now {confidence_progression[-1]:.1%}!

→ On the 5th use with confidence > 0.8:
  Router recognizes as learned command
  Skips LLM planning (2-3 sec saved)
  Executes directly in 0.2 seconds! ⚡
    """)


def example_4_phrase_mappings():
    """Example: Training phrase mappings"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 4: Learned Phrase Mappings                                   ║
╚════════════════════════════════════════════════════════════════════════╝

User language patterns are learned and mapped to actions. These create
"shortcuts" that execute instantly without LLM planning.
    """)
    
    memory = get_memory_store()
    
    # Learn some custom mappings
    mappings_to_learn = [
        {
            "phrase": "check my emails",
            "action": "open_application",
            "params": {"app_name": "outlook"}
        },
        {
            "phrase": "start working",
            "action": "multi_step",
            "params": {
                "steps": ["open_ide", "open_terminal", "open_browser"]
            }
        },
        {
            "phrase": "save my work",
            "action": "keyboard_shortcut",
            "params": {"keys": ["ctrl", "s"]}
        },
        {
            "phrase": "show me memory stats",
            "action": "show_stats",
            "params": {}
        },
    ]
    
    print("\n✓ Training phrase mappings:\n")
    
    for mapping in mappings_to_learn:
        memory.learn_phrase_mapping(
            user_phrase=mapping["phrase"],
            action=mapping["action"],
            parameters=mapping["params"],
            confidence=0.8
        )
        print(f'   "{mapping["phrase"]}"')
        print(f'    ↓ {mapping["action"]}\n')
    
    # Retrieve high-confidence mappings
    high_conf = memory.get_high_confidence_mappings(min_confidence=0.75)
    
    print(f"\n✓ Retrieved {len(high_conf)} high-confidence mappings:")
    for phrase in list(high_conf.keys())[:2]:
        print(f'   • "{phrase}"')
    
    print("""
These mappings are instantly retrieved by Router, providing:
  - Natural language understanding (learns YOUR phrases)
  - Zero latency execution (no LLM needed)
  - Personalized command shortcuts
    """)


def example_5_behavior_patterns():
    """Example: Recording behavior patterns"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 5: Recording Behavior Patterns                               ║
╚════════════════════════════════════════════════════════════════════════╝

Track sequences of actions that users frequently perform together.
These can be suggested or automated in the future.
    """)
    
    memory = get_memory_store()
    context = ContextManager()
    
    # Record some daily routines
    patterns = {
        "morning_startup": [
            "check_weather",
            "check_emails",
            "open_calendar",
            "open_slack",
            "open_ide"
        ],
        "end_of_day": [
            "commit_code",
            "close_ide",
            "sync_files",
            "close_apps",
            "lock_screen"
        ],
        "meeting_prep": [
            "check_calendar",
            "open_zoom",
            "test_audio",
            "share_screen"
        ]
    }
    
    print("\n✓ Recording behavior patterns:\n")
    
    for pattern_name, actions in patterns.items():
        # Record 2-3 times to simulate repeated behavior
        for occurrence in range(2):
            memory.record_action_sequence(pattern_name, actions)
        
        print(f'   {pattern_name}:')
        for action in actions[:3]:
            print(f'     • {action}')
        print(f'     ... ({len(actions)} total)\n')
    
    # Retrieve patterns
    all_patterns = memory.get_action_patterns(count=2)
    
    print(f"✓ Found {len(all_patterns)} recorded patterns\n")
    for pattern, occurrences in list(all_patterns.items())[:1]:
        print(f"   Pattern: {pattern}")
        print(f"   Occurrences: {len(occurrences)}")
        if occurrences:
            first = occurrences[0]
            print(f"   Actions: {' → '.join(first.get('actions', [])[:3])}...")
    
    print("""
Future capabilities:
  - Suggest completing the pattern ("continue with meeting_prep?")
  - Automate the entire sequence
  - Predict what user will do next
    """)


def example_6_memory_management():
    """Example: Checking and managing memory"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 6: Memory Management & Statistics                            ║
╚════════════════════════════════════════════════════════════════════════╝

Check what JARVIS has learned and manage the memory system.
    """)
    
    memory = get_memory_store()
    
    stats = memory.get_stats()
    
    print("\n✓ Memory Statistics:\n")
    print(f"   Learned Preferences:    {stats['preferences_count']:>3}")
    print(f"   Behavior Patterns:      {stats['patterns_count']:>3}")
    print(f"   Phrase Mappings:        {stats['phrase_mappings_count']:>3}")
    print(f"   Tool Executions Tracked:{stats['tool_outcomes_count']:>3}")
    print(f"   Last Updated:           {stats['last_updated']}")
    
    print("""
Using the memory_manager.py utility:

   python memory_manager.py stats      # This output!
   python memory_manager.py prefs      # See all preferences
   python memory_manager.py mappings   # See learned phrases
   python memory_manager.py patterns   # See action sequences
   python memory_manager.py tools      # See tool effectiveness
   python memory_manager.py export     # Save memories as JSON
   python memory_manager.py clear      # Reset all memories
    """)


def example_7_context_integration():
    """Example: Using ContextManager for learning"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 7: Learning via ContextManager                               ║
╚════════════════════════════════════════════════════════════════════════╝

The ContextManager provides easy methods to trigger learning from
within your code.
    """)
    
    context = ContextManager()
    
    print("\n✓ ContextManager learning methods:\n")
    
    # Example 1: Learn a preference
    context.learn_user_preference("color_theme", "dark")
    print('   context.learn_user_preference("color_theme", "dark")')
    print('   ✓ Preference learned\n')
    
    # Example 2: Learn an action sequence
    code_session = ["open_ide", "open_terminal", "open_debugger"]
    context.learn_action_sequence("code_session", code_session)
    print(f'   context.learn_action_sequence("code_session", {code_session})')
    print('   ✓ Action sequence recorded\n')
    
    # Example 3: Learn from successful action
    context.learn_from_action(
        user_input="open vscode",
        tool_name="open_application",
        parameters={"app_name": "vscode"},
        success=True,
        execution_time=0.8
    )
    print('   context.learn_from_action(...) [success=True]')
    print('   ✓ Action learning recorded + tool effectiveness tracked\n')
    
    # Example 4: Retrieve learning
    prefs = context.get_learned_preferences()
    print(f'   context.get_learned_preferences()')
    print(f'   ✓ Retrieved {len(prefs)} preferences\n')
    
    # Example 5: Get memory stats
    memory_stats = context.get_memory_stats()
    print(f'   context.get_memory_stats()')
    print(f'   ✓ Retrieved stats: {memory_stats}\n')
    
    print("""
Integrate these calls in your Executor to enable automatic learning:

   # After tool execution succeeds:
   context.learn_from_action(
       user_input=original_request,
       tool_name=executed_tool,
       parameters=tool_params,
       success=True,
       execution_time=elapsed_seconds
   )
    """)


def example_8_practical_workflow():
    """Example: Complete learning workflow"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║  EXAMPLE 8: Complete Workflow - From Raw Command to Learned Skill     ║
╚════════════════════════════════════════════════════════════════════════╝

Here's how the learning system works end-to-end in a real scenario.
    """)
    
    memory = get_memory_store()
    
    print("\n─ SCENARIO: User opens Chrome multiple times\n")
    
    user_input = "open chrome"
    
    print(f'USER SAYS: "{user_input}"\n')
    
    print("ITERATION 1: First time\n")
    print("  [Router]   No learned mapping found")
    print("  [Planner]  Creating plan... (takes 2.5s)")
    print("  [Executor] Executes: open_application('chrome')")
    print("  [Memory]   Recording tool outcome (success)")
    memory.record_tool_outcome(
        "open_application", "browser_launch",
        {"app_name": "chrome"}, True, 1.2
    )
    print("  [Memory]   Learning phrase mapping (0.7 confidence)")
    memory.learn_phrase_mapping(user_input, "open_application", 
                                {"app_name": "chrome"}, 0.7)
    print("  TOTAL TIME: 2.7s ⏱️\n")
    
    print("ITERATION 2: Second time\n")
    print("  [Router]   Found learned mapping (0.7 confidence)")
    print("  [Memory]   Still below 0.8 threshold - use planner")
    print("  [Planner]  Creating plan... (takes 2.5s)")
    print("  [Executor] Executes: open_application('chrome')")
    print("  [Memory]   Increasing confidence: 0.7 → 0.8")
    memory.learn_from_execution(user_input, "open_application", 
                               {"app_name": "chrome"}, True, 1.1)
    print("  TOTAL TIME: 2.6s ⏱️\n")
    
    print("ITERATION 3-4: Third and fourth times\n")
    for i in range(2):
        print(f"  [Execution {i+3}] Confidence growing...")
        memory.learn_from_execution(user_input, "open_application",
                                   {"app_name": "chrome"}, True, 1.0)
    mapping = memory.find_phrase_mapping(user_input)
    conf = mapping['confidence'] if mapping else 0
    print(f"  [Memory]   Confidence now: {conf:.1%}")
    print("  TOTAL TIME: ~2.5s each ⏱️\n")
    
    print("ITERATION 5+: Fifth time onwards (MAGIC HAPPENS!)\n")
    print("  [Router]   Found learned mapping (0.9 confidence)")
    print("  ⚡ FAST PATH: Confidence >= 0.8")
    print("  [Executor] Directly opens Chrome")
    print("  [Memory]   Recording success, tracking effectiveness")
    print("  TOTAL TIME: 0.2s ⚡⚡⚡\n")
    
    print("RESULTS:")
    print(f"  •  Iterations 1-2: 2.7s, 2.6s (planning overhead)")
    print(f"  •  Iterations 3-4: 2.5s each (still planning but confidence building)")
    print(f"  •  Iteration 5+:  0.2s (instant execution!) 🚀\n")
    
    print("LEARNING ACHIEVED:")
    print(f"  ✓ Phrase mapping: '{user_input}' → open_application")
    print(f"  ✓ Confidence: {mapping['confidence']:.0%}")
    print(f"  ✓ Speed improvement: 13x faster!")
    print(f"  ✓ Natural language: Learns user's exact phrasing")
    print(f"  ✓ Persistent: Will still work next session\n")


def main():
    """Run all examples"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║     JARVIS SELF-LEARNING MEMORY STORE - PRACTICAL EXAMPLES             ║
║                                                                        ║
║                     Watch JARVIS Learn in Action!                      ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    input("\nPress Enter to continue...\n")
    
    examples = [
        example_1_learn_preferences,
        example_2_track_tool_usage,
        example_3_auto_learning,
        example_4_phrase_mappings,
        example_5_behavior_patterns,
        example_6_memory_management,
        example_7_context_integration,
        example_8_practical_workflow,
    ]
    
    for i, example in enumerate(examples, 1):
        example()
        if i < len(examples):
            input("Press Enter to continue to next example...\n")
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                      END OF EXAMPLES                                   ║
╚════════════════════════════════════════════════════════════════════════╝

Next Steps:
  1. Run the memory manager to see what's been learned:
     python memory_manager.py stats

  2. Check the documentation:
     Read LEARNING_MEMORY_GUIDE.md for full reference

  3. Run the test suite:
     python test_memory_store.py

  4. Integrate learning into your Executor:
     see example_7_context_integration() above

Start using JARVIS and watch it learn! 🚀
    """)


if __name__ == "__main__":
    main()
