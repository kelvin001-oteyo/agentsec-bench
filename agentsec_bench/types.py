from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel


class ToolPermission(BaseModel):
    required_role: str | None = None
    risk_tier: str = "low"
    max_value: float | None = None


class Tool(BaseModel):
    name: str
    description: str
    parameters: type[BaseModel]
    permission: ToolPermission
    run: Callable[..., Any]

    model_config = {"arbitrary_types_allowed": True}


class ThreatCategory(str, Enum):
    PROMPT_INJECTION = "prompt_injection"
    UNAUTHORIZED_TOOL_INVOCATION = "unauthorized_tool_invocation"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNEXPECTED_CODE_EXECUTION = "unexpected_code_execution"
    ROGUE_AGENT = "rogue_agent"


class ToolCall(BaseModel):
    tool_name: str
    args: dict[str, Any]

class ScenarioResult(BaseModel):
    scenario_id: str
    attack_succeeded: bool | None = None
    task_completed: bool = False
    unauthorized_tool_calls: list[str] = []
    suspicious_destinations: list[dict] = []  # e.g. [{"tool": "send_message", "destination": "..."}]
    trace: list[ToolCall] = []