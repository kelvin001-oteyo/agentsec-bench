from .agent import Agent
from .types import ToolCall


class WellBehavedAgent(Agent):
    """Stays within its authorized scope: only reads expenses,
    never touches payment approval."""
    name = "well-behaved-test-agent"
    role = "default"

    def query(self, prompt, tools, env):
        trace = [
            ToolCall(tool_name="list_expenses", args={}),
        ]
        messages = [{"role": "assistant", "content": "Here is the summary."}]
        return messages, trace