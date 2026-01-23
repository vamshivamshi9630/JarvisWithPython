# JARVIS – Personal AI Assistant Project

## What this project is
JARVIS is a personal AI assistant built in Python.
It uses an LLM-first, agent-based architecture.

## Core principles
- LLM is the primary brain
- No command-first logic
- Telugu conversational English replies
- Supports CHAT, QUERY, ACTION
- Multi-step workflows (WiFi, Bluetooth)
- Memory-based behavior

## Current architecture
User input
→ llm_core.py (reasoning)
→ executor_v2.py (routing)
→ local_handlers / system actions
→ response

## Style rules
- Friendly Telugu chat tone
- No robotic replies
- Avoid “Ardham kale” unless unavoidable

## Non-goals
- No medical/legal advice
- No hallucinated system actions
