"""
Orchestrator: The Central Intelligence System

This is the REAL BRAIN of JARVIS.

Instead of rule-based routing (if/else chains), the orchestrator:
1. Receives user input
2. Routes to appropriate handler (chat, direct_action, or goal/planning)
3. Executes step-by-step (for goals)
4. OBSERVES results (this is critical)
5. Replans if necessary (for complex goals)

Architecture:
  User Input
    ↓
  Router (is this chat? direct action? or goal?)
    ├─ Chat → Simple response
    ├─ Direct Action → Execute immediately
    └─ Goal → Call Planner → Orchestrator loop
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from core.router import Router
from core.multi_step_parser import MultiStepParser

# Extended automation support
try:
    from core.runtime_context import RuntimeContext
except ImportError:
    RuntimeContext = None

logger = logging.getLogger(__name__)

# Vector memory store for semantic search
try:
    from core.vector_store import get_vector_store
    VECTOR_STORE = get_vector_store()
except Exception as e:
    VECTOR_STORE = None
    logger.debug(f"Vector store not available: {e}")


class ExecutionStatus(Enum):
    """Result of executing a step"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # Some substeps worked
    FATAL = "fatal"  # Can't continue


class StepResult:
    """Result from executing a single tool call"""

    def __init__(
        self,
        tool_name: str,
        status: ExecutionStatus,
        message: str = "",
        data: Dict[str, Any] = None,
        error: str = None,
    ):
        self.tool_name = tool_name
        self.status = status
        self.message = message
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool_name,
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }

    def is_success(self) -> bool:
        return self.status in [ExecutionStatus.SUCCESS, ExecutionStatus.PARTIAL]


class Orchestrator:
    """
    Central controller for JARVIS.

    This is where:
    - Strategy (planning) meets Execution
    - Reasoning (LLM) meets Reality (tools)
    - Intent becomes Action

    The orchestrator doesn't do the thinking (Planner does).
    The orchestrator doesn't do the action (Executor does).
    The orchestrator decides WHAT to do and HANDLES THE RESULTS.
    """

    def __init__(self, planner, executor, observer=None, context_manager=None, max_replans: int = 2):
        """
        Initialize the orchestrator.

        Args:
            planner: Instance of Planner (from ai.planner)
            executor: Instance of Executor (from core.executor)
            observer: Instance of Observer (from core.observer) - optional for ReAct loop
            context_manager: Instance tracking state/history - optional
            max_replans: How many times to replan on failure (2-3 is good)
        """
        self.planner = planner
        self.executor = executor
        self.observer = observer
        self.context = context_manager
        self.max_replans = max_replans
        
        # Initialize runtime context for desktop automation
        if RuntimeContext:
            self.runtime_context = RuntimeContext()
        else:
            self.runtime_context = None

        # Track attempt history for debugging
        self.attempt_history: List[Dict[str, Any]] = []
        self.current_attempt = 0

        logger.debug(
            f"Orchestrator initialized (max replans: {max_replans}, observer: {'yes' if observer else 'no'}, runtime_context: {'yes' if self.runtime_context else 'no'})"
        )


    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point: Convert user input to result.

        Routes request based on Router classification:
        1. Structured_direct - Multi-step direct commands (no LLM)
        2. Direct_action - Single direct command (no LLM)
        3. Chat - Simple greetings (no tools)
        4. Goal - Complex requests (needs LLM planning)

        Args:
            user_input: Natural language request from user

        Returns:
            {
                "success": bool,
                "goal": str,
                "result": str,
                "attempts": int,
                "details": {execution details}
            }
        """
        # GATE: Classify input before anything else
        route = Router.classify(user_input)
        print(f"[ROUTER] Route: {route}")
        logger.debug(f"[ROUTER] Route: {route} for input: {user_input[:50]}...")
        
        # ROUTE 1: Chat (simple greetings - no tools, no planning)
        if route == "chat":
            response = Router.get_chat_response(user_input)
            return {
                "success": True,
                "goal": "Chat response",
                "result": response,
                "attempts": 1,
                "details": {"method": "chat"}
            }
        
        # ROUTE 2: Direct action (single command - direct tool execution, no planning)
        if route == "direct_action":
            action = Router.get_direct_action(user_input)
            if not action:
                return {
                    "success": False,
                    "goal": "Execute command",
                    "result": "Command not found",
                    "attempts": 1,
                    "details": {"method": "direct_action", "error": "no match"}
                }
            
            tool_name, params = action
            try:
                result = self._execute_single_tool(tool_name, params)
                
                if result.is_success():
                    return {
                        "success": True,
                        "goal": f"Execute {tool_name}",
                        "result": result.message,
                        "attempts": 1,
                        "details": {"method": "direct_action"}
                    }
                else:
                    return {
                        "success": False,
                        "goal": f"Execute {tool_name}",
                        "result": result.error or result.message,
                        "attempts": 1,
                        "details": {"method": "direct_action"}
                    }
            except Exception as e:
                logger.debug(f"Direct action failed: {e}")
                return {
                    "success": False,
                    "goal": "Execute command",
                    "result": f"Execution failed",
                    "attempts": 1,
                    "details": {"method": "direct_action", "error": str(e)}
                }
        
        # ROUTE 3: Structured direct (multi-step with direct verbs - no LLM)
        elif route == "structured_direct":
            structured_actions = MultiStepParser.parse(user_input)
            
            results = []
            
            for idx, action in enumerate(structured_actions, 1):
                print(f"[STEP {idx}] {action}")
                
                result = self.executor.execute(action)
                
                results.append(str(result))
                
                if isinstance(result, str) and result.lower().startswith("error"):
                    return {
                        "success": False,
                        "goal": "Execute multi-step command",
                        "result": f"Failed at step {idx}: {result}",
                        "attempts": 1,
                        "details": {"method": "structured_direct", "error": result}
                    }
            
            return {
                "success": True,
                "goal": "Execute multi-step command",
                "result": "\n".join(results),
                "attempts": 1,
                "details": {"method": "structured_direct", "steps": len(results)}
            }
        
        # ROUTE 4: Goal (complex request - use LLM planner)
        else:
            # Reset for this request
            self.attempt_history = []
            self.current_attempt = 0

            # Try to execute plan, with replanning on failure
            while self.current_attempt < (1 + self.max_replans):
                self.current_attempt += 1

                try:
                    # Step 1: REASON (what should we do?)
                    plan = self._get_plan(user_input)
                    
                    # Check if model is missing (guard check from planner)
                    if plan and plan.get("goal") == "no_model":
                        return {
                            "success": False,
                            "goal": "Execute plan",
                            "result": "Local AI brain is not available. Only simple commands will work.",
                            "attempts": 1,
                            "details": {"method": "planning", "error": "model_missing"}
                        }
                    
                    if not plan or not plan.get("steps"):
                        # If planner returns empty plan, don't retry
                        return {
                            "success": False,
                            "goal": "Execute plan",
                            "result": "Sorry, I couldn't figure out how to help with that.",
                            "attempts": 1,
                            "details": {"method": "planning", "error": "empty_plan"}
                        }

                    # Step 2: ACT (do the things)
                    execution_results = self._execute_plan(plan)

                    # Step 3: OBSERVE (what happened?)
                    should_continue = self._observe_results(
                        execution_results, plan
                    )

                    if should_continue:
                        return self._success_response(
                            plan,
                            execution_results,
                            user_input,
                        )
                    else:
                        # Plan failed, try again if we have attempts left
                        if self.current_attempt < (1 + self.max_replans):
                            logger.debug(
                                f"Execution failed. Replanning..."
                            )
                            # Add failure context for replanning
                            user_input = self._enhance_input_with_context(
                                user_input,
                                execution_results,
                            )
                            continue
                        else:
                            return self._failed_response(
                                f"Failed after {self.current_attempt} attempts",
                                user_input,
                                execution_results,
                            )

                except Exception as e:
                    logger.debug(f"Orchestrator error: {str(e)}")
                    return self._failed_response(
                        f"Sorry, something went wrong.",
                        user_input,
                    )

            return self._failed_response(
                f"Max retries exceeded",
                user_input,
            )

    def _get_plan(self, user_input: str) -> Optional[Dict[str, Any]]:
        """
        Step 1: REASON — Call planner to create strategy.

        This is where LLM intelligence enters the system.
        Injects relevant memory from vector store for context.
        """
        logger.debug(f"Asking planner: '{user_input}'")

        try:
            context = self.context.get_context() if self.context else {}
            
            # MEMORY INJECTION: Search for relevant memories before planning
            memory_context = ""
            if VECTOR_STORE:
                relevant_memories = VECTOR_STORE.search(user_input, k=3)
                if relevant_memories:
                    memory_context = "\nRelevant Past Knowledge:\n"
                    for i, (memory_text, similarity) in enumerate(relevant_memories, 1):
                        confidence = f"{(similarity * 100):.0f}%"
                        memory_context += f"  [{i}] ({confidence}) {memory_text}\n"
                    logger.debug(f"Injected {len(relevant_memories)} memories into planning context")
            
            # Add memory context to user input for planner
            user_input_enhanced = user_input
            if memory_context:
                user_input_enhanced = f"{memory_context}\nCurrent Request: {user_input}"
            
            plan = self.planner.plan(user_input_enhanced, context)

            if plan and "steps" in plan:
                logger.debug(f"Plan created: {len(plan['steps'])} step(s)")
                return plan
            else:
                logger.debug("Planner returned invalid plan")
                return None

        except Exception as e:
            logger.debug(f"Planner error: {str(e)}")
            return None

    def _execute_plan(self, plan: Dict[str, Any]) -> List[StepResult]:
        """
        Step 2: ACT — Execute the plan step by step.

        Executor's job: Just run the tools. Don't think.
        Orchestrator's job: Decide what to do with the results.
        """
        logger.debug(f"Executing {len(plan['steps'])} steps...")

        results: List[StepResult] = []

        for step_num, step in enumerate(plan["steps"], 1):
            tool_name = step.get("tool")
            parameters = step.get("parameters", {})

            logger.debug(f"Executing step {step_num}: {tool_name}")

            try:
                # Call actual executor
                result = self._execute_single_tool(tool_name, parameters)
                results.append(result)

                # Update context with this step's result
                if self.context:
                    self.context.add_action(tool_name, result.to_dict())

            except Exception as e:
                logger.debug(f"Step {step_num} exception: {str(e)}")
                result = StepResult(
                    tool_name=tool_name,
                    status=ExecutionStatus.FATAL,
                    error=str(e),
                )
                results.append(result)

        return results

    def _execute_single_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> StepResult:
        """
        Execute a single tool using executor.

        This delegates to executor.execute_tool() which should:
        - Look up the tool
        - Call it with parameters
        - Return success/failure
        """
        try:
            # Executor should have this method
            if hasattr(self.executor, "execute_tool"):
                result = self.executor.execute_tool(tool_name, parameters)

                # Convert to StepResult
                if isinstance(result, dict):
                    return StepResult(
                        tool_name=tool_name,
                        status=ExecutionStatus(
                            result.get("status", "failed")
                        ),
                        message=result.get("message", ""),
                        data=result.get("data", {}),
                        error=result.get("error"),
                    )
                else:
                    return StepResult(
                        tool_name=tool_name,
                        status=ExecutionStatus.SUCCESS,
                        message=str(result),
                    )

            else:
                logger.warning(
                    f"Executor doesn't have execute_tool. Using fallback."
                )
                # Fallback: try execute() method (old interface)
                if hasattr(self.executor, "execute"):
                    result = self.executor.execute(
                        {"tool": tool_name, **parameters}
                    )
                    return StepResult(
                        tool_name=tool_name,
                        status=ExecutionStatus.SUCCESS,
                        message=str(result),
                    )

        except Exception as e:
            logger.error(f"Executor failed on {tool_name}: {str(e)}")

        return StepResult(
            tool_name=tool_name,
            status=ExecutionStatus.FAILED,
            error=f"Could not execute {tool_name}",
        )

    def _execute_single_tool_by_name(self, step_text: str) -> StepResult:
        """
        Execute a tool by parsing the step text.
        
        Tries to match the step against known tools.
        Falls back to search if no exact match.
        
        Args:
            step_text: Natural language step string like "open chrome"
            
        Returns:
            StepResult from execution
        """
        step_lower = step_text.lower().strip()
        
        # Try exact match from DIRECT_ACTIONS
        action = Router.get_direct_action(step_lower)
        if action:
            tool_name, params = action
            return self._execute_single_tool(tool_name, params)
        
        # Try to find a matching tool by name
        try:
            # Try common patterns
            if step_lower.startswith("open "):
                app_name = step_lower.replace("open ", "").strip()
                return self._execute_single_tool("open_application", {"app_name": app_name})
            
            elif step_lower.startswith("search"):
                query = step_lower.replace("search", "").strip()
                return self._execute_single_tool("search_web", {"query": query})
            
            elif "youtube" in step_lower or "youtube.com" in step_lower:
                return self._execute_single_tool("navigate_to_website", {"url": "youtube.com"})
            
            elif step_lower.startswith("go to "):
                url = step_lower.replace("go to ", "").strip()
                return self._execute_single_tool("navigate_to_website", {"url": url})
            
            elif "play" in step_lower:
                query = step_lower.replace("play", "").strip()
                return self._execute_single_tool("play_media", {"query": query})
        
        except Exception as e:
            logger.debug(f"Error parsing step '{step_text}': {e}")
        
        # If all else fails, return failure
        return StepResult(
            tool_name=step_text,
            status=ExecutionStatus.FAILED,
            error=f"Could not determine how to execute: {step_text}",
        )

    def _observe_results(
        self, results: List[StepResult], plan: Dict[str, Any]
    ) -> bool:
        """
        Step 3: OBSERVE — Did the plan work?

        Return True if all steps succeeded.
        Return False if we should replan.
        """
        if not results:
            return False

        # If we have an observer, verify each result
        if self.observer:
            for i, step in enumerate(plan.get("steps", [])):
                if i >= len(results):
                    break
                    
                result = results[i]
                verification = self.observer.verify(step, result.to_dict())
                
                if not verification.get("success"):
                    result.status = ExecutionStatus.FAILED
                    result.error = verification.get("explanation", "Verification failed")

        # Return True if all steps succeeded
        all_succeeded = all(r.is_success() for r in results)
        return all_succeeded

    def _execute_multi_step_plan(
        self, plan: Dict[str, Any], original_input: str
    ) -> Dict[str, Any]:
        """
        Execute a multi-step parsed plan (structured command).
        
        This bypasses the LLM planner and directly executes steps.
        Avoids 30-90 second delays for commands like:
        "open chrome and go to youtube and play rajasaab songs"
        """
        logger.debug(f"Executing multi-step plan: {len(plan.get('steps', []))} steps")
        
        try:
            # Execute steps sequentially
            results = self._execute_plan(plan)
            
            # Verify results
            should_continue = self._observe_results(results, plan)
            
            if should_continue:
                response = self._success_response(plan, results, original_input)
                # Preserve the multi_step method indicator
                if "details" not in response:
                    response["details"] = {}
                response["details"]["method"] = "multi_step"
                return response
            else:
                response = self._failed_response(
                    "Some steps failed",
                    original_input,
                    results
                )
                if "details" not in response:
                    response["details"] = {}
                response["details"]["method"] = "multi_step"
                return response
        except Exception as e:
            logger.debug(f"Multi-step execution failed: {e}")
            response = self._failed_response(
                "Could not execute steps",
                original_input
            )
            if "details" not in response:
                response["details"] = {}
            response["details"]["method"] = "multi_step"
            return response
    def _enhance_input_with_context(
        self, original_input: str, failed_results: List[StepResult]
    ) -> str:
        """
        When replanning, enhance input with failure information.

        Example:
          Original: "open chrome"
          Enhanced: "open chrome (previous attempt failed: application not found).
                     Try using edge instead."

        This helps planner make better decisions on retry.
        """
        if not failed_results:
            return original_input

        failure_context = [
            f"{r.tool_name} failed: {r.error}" for r in failed_results
            if not r.is_success()
        ]

        if failure_context:
            enhanced = (
                f"{original_input}\n\n"
                f"Previous attempt failed with:\n"
                f"- {chr(10).join(failure_context)}\n"
                f"Please suggest an alternative approach."
            )
            logger.info(f"📝 Enhanced input with failure context")
            return enhanced

        return original_input

    def _success_response(
        self,
        plan: Dict[str, Any],
        execution_results: List[StepResult],
        user_input: str,
    ) -> Dict[str, Any]:
        """Format a successful completion response"""
        details = {
            "plan": plan,
            "execution": [r.to_dict() for r in execution_results],
        }
        
        # Preserve method if it exists in plan
        if "method" in plan:
            details["method"] = plan["method"]
        
        result_summary = self._generate_summary(execution_results)
        
        # AUTO-LEARNING: Store successful interaction in vector memory
        if VECTOR_STORE:
            try:
                VECTOR_STORE.add_interaction(
                    user_input=user_input,
                    ai_response=result_summary
                )
                logger.debug(f"Interaction learned and stored in memory")
            except Exception as e:
                logger.debug(f"Failed to store interaction in memory: {e}")
            
            # Auto-save memory to disk after successful execution
            try:
                VECTOR_STORE.save()
                logger.debug("Memory saved to disk")
            except Exception as e:
                logger.debug(f"Failed to save memory: {e}")
        
        return {
            "success": True,
            "status": "completed",
            "user_input": user_input,
            "goal": plan.get("goal", "Goal achieved"),
            "result": result_summary,
            "steps_executed": len(execution_results),
            "attempts": self.current_attempt,
            "details": details,
        }

    def _failed_response(
        self,
        reason: str,
        user_input: str,
        execution_results: List[StepResult] = None,
    ) -> Dict[str, Any]:
        """Format a failed response"""
        return {
            "success": False,
            "status": "failed",
            "user_input": user_input,
            "result": reason,
            "attempts": self.current_attempt,
            "details": {
                "execution": (
                    [r.to_dict() for r in execution_results]
                    if execution_results
                    else []
                ),
            },
        }

    def _generate_summary(self, results: List[StepResult]) -> str:
        """Create human-readable summary of execution"""
        if not results:
            return "No steps executed"

        steps_summary = []
        for r in results:
            status_icon = "✅" if r.is_success() else "❌"
            steps_summary.append(f"{status_icon} {r.tool_name}: {r.message}")

        return "\n".join(steps_summary)

    def get_attempt_history(self) -> List[Dict[str, Any]]:
        """For debugging: see all attempts"""
        return self.attempt_history

    def reset(self):
        """Clear history for new session"""
        self.attempt_history = []
        self.current_attempt = 0
        logger.info("🔄 Orchestrator reset")
