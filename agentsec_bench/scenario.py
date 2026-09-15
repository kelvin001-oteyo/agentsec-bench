from abc import ABC, abstractmethod
from pydantic import BaseModel
from .types import ThreatCategory, ToolCall, ScenarioResult


class Scenario(ABC):
    id: str
    threat_category: ThreatCategory
    prompt: str
    owasp_control_id: str | None = None

    def init_environment(self, env):
        return env

    @abstractmethod
    def ground_truth(self, pre_env) -> list[ToolCall]:
        """The oracle path: returns the tool calls that correctly solve
        this scenario. Used to validate the scenario and to discover
        which tools/vectors it actually touches."""
        ...

    @abstractmethod
    def evaluate(
        self,
        trace: list[ToolCall],
        pre_env,
        post_env,
    ) -> ScenarioResult:
        ...