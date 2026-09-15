# AgentSec-Bench

A reproducible security evaluation framework for tool-using AI agents,
extending beyond AgentDojo's prompt-injection focus into authorization,
tool misuse, and privilege-escalation scenarios.

## Status
Early prototype. Currently supports:
- Core Scenario/Agent/Tool/Evaluator interfaces
- Two working scenarios (unauthorized payment approval, ambiguous refund authorization)
- Scripted test agents and live LLM agent integrations (OpenAI, Anthropic)