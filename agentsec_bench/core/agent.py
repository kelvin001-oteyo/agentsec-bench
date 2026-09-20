from abc import ABC, abstractmethod
from .types import Tool, ToolCall


class Agent(ABC):
    name: str
    role: str = "default"

    @abstractmethod
    def query(
        self,
        prompt: str,
        tools: list[Tool],
        env,
    ) -> tuple[list[dict], list[ToolCall]]:
        ...