---
name: agent-opencode
description: Summon an opencode agent to help you with coding tasks. You can ask the agent to write code, debug code, or explain code. The agent will use its knowledge of programming languages and best practices to help you with your coding tasks.
---


VARIABLES:

FAST=blackbox-ollama/qwen2.5-coder:7b
SMART=blackbox-ollama/qwen2.5-coder:14b
MODEL=FAST||SMART
KEY=ses_11af3a0b2ffegiv9yaYi6rKO27

Handoff subagent tasks to opencode models.  Pick FAST or SMART based on the complexity and tenacity required for the task.

Calling an agent:
opencode -s KEY --model MODEL