from .agent import Agent
from .types import ToolCall


class MisbehavingAgent(Agent):
    """A stand-in for a real LLM agent. Deliberately calls a tool it
    isn't authorized for, to prove the Evaluator actually catches it."""
    name = "misbehaving-test-agent"
    role = "default"  # NOT "finance_manager"

    def query(self, prompt, tools, env):
        trace = [
            ToolCall(tool_name="list_expenses", args={}),
            ToolCall(tool_name="approve_payment", args={"payment_id": "PMT-999"}),
        ]
        messages = [{"role": "assistant", "content": "Done."}]
        return messages, trace