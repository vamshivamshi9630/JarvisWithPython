#!/usr/bin/env python3
"""
Vector Memory Manager - Manage long-term semantic memory

Commands:
  python vector_memory_manager.py stats       - Show memory statistics
  python vector_memory_manager.py search QUERY - Search memories
  python vector_memory_manager.py teach FACT  - Teach a fact
  python vector_memory_manager.py list        - List all memories
  python vector_memory_manager.py clear       - Clear all memories (⚠️)
  python vector_memory_manager.py export      - Export to JSON
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.vector_store import get_vector_store


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def cmd_stats():
    """Show memory statistics"""
    print_header("VECTOR MEMORY STATISTICS")
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available. Install: pip install faiss-cpu sentence-transformers")
        return
    
    stats = memory.get_stats()
    
    print(f"Total Memories:       {stats.get('total_entries', 0)}")
    print(f"Indexed in FAISS:     {stats.get('index_size', 0)}")
    print(f"Embedding Dimension:  {stats.get('embedding_dimension', 0)}")
    
    print("\nBy Type:")
    for mem_type, count in stats.get('by_type', {}).items():
        print(f"  {mem_type:.<20} {count}")
    
    print("\nBy Source:")
    for source, count in stats.get('by_source', {}).items():
        print(f"  {source:.<20} {count}")


def cmd_search():
    """Search memories"""
    if len(sys.argv) < 3:
        print("Usage: python vector_memory_manager.py search QUERY")
        return
    
    query = " ".join(sys.argv[2:])
    
    print_header(f"SEARCHING FOR: '{query}'")
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available.")
        return
    
    results = memory.search(query, k=5)
    
    if not results:
        print("No memories found.")
        return
    
    for i, (text, similarity) in enumerate(results, 1):
        confidence = f"{(similarity * 100):.1f}%"
        print(f"[{i}] ({confidence} match)")
        print(f"    {text[:100]}")
        if len(text) > 100:
            print(f"    ...")
        print()


def cmd_teach():
    """Teach a fact"""
    if len(sys.argv) < 3:
        print("Usage: python vector_memory_manager.py teach FACT")
        print("Example: python vector_memory_manager.py teach 'Earth orbits the Sun'")
        return
    
    fact = " ".join(sys.argv[2:])
    
    print_header("TEACHING NEW FACT")
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available.")
        return
    
    if memory.teach_fact(fact):
        memory.save()
        print(f"✓ Fact learned and saved:")
        print(f"  '{fact}'")
    else:
        print("✗ Failed to teach fact")


def cmd_list():
    """List all memories"""
    print_header("ALL MEMORIES")
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available.")
        return
    
    memories = memory.get_all_memories()
    
    if not memories:
        print("No memories stored.")
        return
    
    print(f"Total: {len(memories)} memories\n")
    
    for i, mem in enumerate(memories[:20], 1):  # Show first 20
        mem_type = mem.get('entry_type', 'unknown')
        source = mem.get('source', 'unknown')
        text = mem.get('text', '')[:60]
        timestamp = mem.get('timestamp', 'unknown')[:10]
        
        print(f"{i:2d}. [{mem_type:.<12}] [{source}] {timestamp}")
        print(f"    {text}")
        print()
    
    if len(memories) > 20:
        print(f"... and {len(memories) - 20} more memories")


def cmd_clear():
    """Clear all memories"""
    print_header("⚠️  CLEAR ALL MEMORIES")
    
    confirm = input("This will DELETE all memories. Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available.")
        return
    
    if memory.clear():
        memory.save()
        print("✓ All memories cleared.")
    else:
        print("✗ Failed to clear memories")


def cmd_export():
    """Export memories to JSON"""
    print_header("EXPORTING MEMORIES")
    
    memory = get_vector_store()
    if not memory:
        print("Vector memory not available.")
        return
    
    export_data = memory.export()
    
    export_path = Path("memory_export.json")
    with open(export_path, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    stats = export_data.get('stats', {})
    print(f"✓ Exported to {export_path}\n")
    print(f"Memories: {stats.get('total_entries', 0)}")
    print(f"File size: {export_path.stat().st_size / 1024:.1f} KB")


def cmd_help():
    """Show help"""
    print(__doc__)


def main():
    """Main command handler"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        "stats": cmd_stats,
        "search": cmd_search,
        "teach": cmd_teach,
        "list": cmd_list,
        "clear": cmd_clear,
        "export": cmd_export,
        "help": cmd_help,
        "-h": cmd_help,
        "--help": cmd_help,
    }
    
    if command in commands:
        try:
            commands[command]()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Unknown command: {command}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
