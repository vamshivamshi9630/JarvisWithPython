#!/usr/bin/env python3
"""
JARVIS - AI Personal Assistant (Fully Offline)

Intelligently routes commands using local LLM planning and execution.
Works completely offline after first run (model auto-downloads).
"""

import os
import sys
import logging

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
    print("\n[!] JARVIS: Running without Administrator privileges.")
    print("[*] WiFi control and some system features may not work.\n")

# ==================== JARVIS STARTS HERE ====================

# Setup logging - suppress most output by default
logging.basicConfig(
    level=logging.CRITICAL,  # Only show critical errors
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Import offline components
from ai.local_llm import LocalLLM, get_local_llm
from ai.planner import Planner
from core.executor import execute_tool
from core.orchestrator import Orchestrator
from core.tool_registry import ToolRegistry
from core.context import ContextManager
from core.observer import Observer

# Adapter for executor to work with orchestrator
class ExecutorAdapter:
    """Adapter for execute_tool function to work with orchestrator."""
    
    def execute_tool(self, tool_name: str, parameters: dict):
        """Call pure executor function"""
        return execute_tool(tool_name, parameters)
    
    def execute(self, action: dict):
        """Execute structured action dict"""
        from core.executor import execute
        return execute(action)


# Initialize system (suppress logs)
try:
    llm = get_local_llm()
    tool_registry = ToolRegistry()
    planner = Planner(tool_registry)
    executor_adapter = ExecutorAdapter()
    context_manager = ContextManager()
    observer = Observer()
    orchestrator = Orchestrator(
        planner=planner,
        executor=executor_adapter,
        observer=observer,
        context_manager=context_manager,
        max_replans=2
    )
except Exception as e:
    print(f"[ERROR] Failed to initialize: {e}")
    sys.exit(1)

print("JARVIS > Ready!")
print("JARVIS > Type 'help' for commands or 'exit' to quit.\n")

# ==================== MAIN LOOP ====================

while True:
    try:
        cmd = input("You > ").strip()
        
        if not cmd:
            continue
            
        if cmd.lower() == "exit":
            print("JARVIS > Goodbye!")
            break
            
        if cmd.lower() == "help":
            print("""
JARVIS - Intelligent Assistant (Fully Offline)

Examples:
  • hi, hello
  • open chrome (simple commands)
  • open chrome and search youtube for music (complex commands)
  • lock screen, mute, get time
  • what is python, explain machine learning
  • prepare my pc for coding

Type 'exit' to quit.
            """)
            continue

        # Process command through agent system
        result_dict = orchestrator.process(cmd)
        
        # Display clean result
        if result_dict.get("success"):
            print(f"JARVIS > {result_dict.get('result', 'Done!')}\n")
        else:
            print(f"JARVIS > {result_dict.get('result', 'Sorry, I could not complete that.')}\n")
            
    except KeyboardInterrupt:
        print("\nJARVIS > Goodbye!")
        break
    except Exception as e:
        print(f"JARVIS > Error: {str(e)}\n")
        logger.error(f"Error: {e}", exc_info=False)
