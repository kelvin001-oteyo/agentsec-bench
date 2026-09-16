# AgentSec-Bench

A reproducible security evaluation framework for tool-using AI agents,
extending beyond AgentDojo's prompt-injection focus into authorization,
tool misuse, privilege escalation, and data exfiltration.

## Status

Working prototype. Currently supports:

- Core Scenario / Agent / Tool / Evaluator interfaces
- 5 scenarios across 4 threat patterns:
  - Unauthorized tool invocation (payment approval, refund authorization, privilege escalation)
  - Prompt injection (hidden instructions in retrieved content)
  - Data exfiltration (sensitive data sent to unauthorized destinations)
- Two independent detection mechanisms:
  - Role-based authorization checks
  - Destination-based checks (catches cases role checks alone miss)
- 14 automated tests (ground-truth validation + agent behavior checks)
- JSON results export with OWASP control mapping
- HTML report generation

## Not yet done

- Live LLM agent evaluation (OpenAI and Anthropic integrations are built,
  pending account funding)
- Baseline comparison against AgentDojo
- Docker-based reproducibility
- Broader scenario coverage

## Running it

    uv sync
    uv run python run_test.py        # run all scenarios
    uv run python check_scenarios.py  # validate ground truth
    uv run pytest -v                  # run test suite
    uv run python generate_report.py  # produce report.html