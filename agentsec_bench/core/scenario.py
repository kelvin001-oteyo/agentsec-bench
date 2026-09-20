from abc import ABC, abstractmethod
from pydantic import BaseModel
from .types import ThreatCategory, ToolCall, ScenarioResult


class Scenario(ABC):
    id: str
    threat_category: ThreatCategory
    prompt: str
    owasp_control_id: str | None = None

    # Which argument values (e.g. email addresses, recipients) are
    # legitimate destinations for this scenario. Used by the Evaluator's
    # destination-based check, independent of role-based authorization.
    allowed_destinations: list[str] | None = None

    def init_environment(self, env):
        return env

    @abstractmethod
    def ground_truth(self, pre_env) -> list[ToolCall]:
        ...

    @abstractmethod
    def evaluate(
        self,
        trace: list[ToolCall],
        pre_env,
        post_env,
    ) -> ScenarioResult:
        ...