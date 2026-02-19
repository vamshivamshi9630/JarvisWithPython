#!/usr/bin/env python3
"""
Memory Management Utility - Inspect and manage JARVIS learned memories

Commands:
  python memory_manager.py stats       - Show memory statistics
  python memory_manager.py prefs       - Show all learned preferences
  python memory_manager.py mappings    - Show all learned phrase mappings
  python memory_manager.py patterns    - Show behavior patterns
  python memory_manager.py tools       - Show tool effectiveness
  python memory_manager.py export      - Export all memories to JSON
  python memory_manager.py clear       - Clear all memories (WARNING!)
"""

import sys
import json
from pathlib import Path
from core.memory_store import get_memory_store


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


def cmd_stats():
    """Show memory statistics"""
    print_header("MEMORY STATISTICS")
    
    memory = get_memory_store()
    stats = memory.get_stats()
    
    print(f"Learned Preferences:  {stats.get('preferences_count', 0)}")
    print(f"Behavior Patterns:    {stats.get('patterns_count', 0)}")
    print(f"Phrase Mappings:      {stats.get('phrase_mappings_count', 0)}")
    print(f"Tool Outcomes:        {stats.get('tool_outcomes_count', 0)}")
    print(f"Last Updated:         {stats.get('last_updated', 'Never')}")


def cmd_prefs():
    """Show all learned preferences"""
    print_header("LEARNED USER PREFERENCES")
    
    memory = get_memory_store()
    prefs = memory.get_all_preferences()
    
    if not prefs:
        print("No preferences learned yet.")
        return
    
    for key, value in prefs.items():
        print(f"• {key}: {value}")


def cmd_mappings():
    """Show all learned phrase mappings"""
    print_header("LEARNED PHRASE MAPPINGS")
    
    memory = get_memory_store()
    mappings = memory.get_high_confidence_mappings(min_confidence=0.5)
    
    if not mappings:
        print("No phrase mappings learned yet.")
        return
    
    for phrase, mapping in mappings.items():
        confidence = mapping.get("confidence", 0)
        action = mapping.get("action")
        print(f"\n'{phrase}'")
        print(f"  → Action: {action}")
        print(f"  → Confidence: {confidence:.1%}")
        params = mapping.get("parameters", {})
        if params:
            print(f"  → Parameters: {json.dumps(params)}")


def cmd_patterns():
    """Show behavior patterns"""
    print_header("LEARNED BEHAVIOR PATTERNS")
    
    memory = get_memory_store()
    patterns = memory.get_action_patterns(count=3)
    
    if not patterns:
        print("No patterns learned yet.")
        return
    
    for pattern_name, occurrences in patterns.items():
        print(f"\n{pattern_name} ({len(occurrences)} occurrences):")
        for i, occurrence in enumerate(occurrences[-3:], 1):
            timestamp = occurrence.get("timestamp", "Unknown")
            actions = occurrence.get("actions", [])
            print(f"  {i}. [{timestamp}] {' → '.join(actions)}")


def cmd_tools():
    """Show tool effectiveness statistics"""
    print_header("TOOL EFFECTIVENESS ANALYSIS")
    
    memory = get_memory_store()
    tools_data = memory.memories.get("tool_outcomes", {})
    
    if not tools_data:
        print("No tool outcomes recorded yet.")
        return
    
    for tool_name, outcomes in sorted(tools_data.items()):
        effectiveness = memory.get_tool_effectiveness(tool_name)
        success_rate = effectiveness.get("success_rate", 0)
        total_uses = effectiveness.get("total_uses", 0)
        avg_time = effectiveness.get("avg_execution_time", 0)
        
        if total_uses == 0:
            continue
        
        print(f"\n{tool_name}:")
        print(f"  Uses:         {total_uses}")
        print(f"  Success Rate: {success_rate:.1%}")
        print(f"  Avg Time:     {avg_time:.2f}s")
        
        task_types = effectiveness.get("task_types", {})
        if task_types:
            print(f"  By Task Type:")
            for task_type, rate in task_types.items():
                print(f"    - {task_type}: {rate:.1%}")


def cmd_export():
    """Export all memories to JSON file"""
    print_header("EXPORTING MEMORIES")
    
    memory = get_memory_store()
    memories = memory.export_memories()
    
    export_path = Path("memory_export.json")
    with open(export_path, 'w') as f:
        json.dump(memories, f, indent=2, default=str)
    
    print(f"✓ Memories exported to {export_path}")
    print(f"\nExported:")
    print(f"  Preferences:  {len(memories.get('user_preferences', {}))}")
    print(f"  Patterns:     {len(memories.get('behavior_patterns', {}))}")
    print(f"  Mappings:     {len(memories.get('phrase_mappings', {}))}")
    print(f"  Tools:        {sum(len(v) for v in memories.get('tool_outcomes', {}).values())}")


def cmd_clear():
    """Clear all memories"""
    print_header("⚠️  CLEAR ALL MEMORIES")
    
    confirm = input("This will DELETE all learned memories. Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    
    memory = get_memory_store()
    memory.clear_memory()
    print("✓ All memories cleared.")


def print_usage():
    """Print usage information"""
    print(__doc__)


def main():
    """Main command handler"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "stats": cmd_stats,
        "prefs": cmd_prefs,
        "preferences": cmd_prefs,
        "mappings": cmd_mappings,
        "patterns": cmd_patterns,
        "tools": cmd_tools,
        "export": cmd_export,
        "clear": cmd_clear,
        "help": print_usage,
        "-h": print_usage,
        "--help": print_usage,
    }
    
    if command in commands:
        try:
            commands[command]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
