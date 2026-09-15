from .types import Tool, ToolCall
from .agent import Agent
from .scenario import Scenario


class Evaluator:
    def __init__(self, tools: list[Tool]):
        self.tools = tools
        self._tools_by_name = {t.name: t for t in tools}

    def run(self, scenario: Scenario, agent: Agent, env) -> "ScenarioResult":
        pre_env = env.model_copy(deep=True)
        messages, trace = agent.query(scenario.prompt, self.tools, env)
        post_env = env

        result = scenario.evaluate(trace, pre_env, post_env)
        result.unauthorized_tool_calls = [
            call.tool_name for call in trace
            if self._is_unauthorized(call, agent)
        ]
        return result

    def _is_unauthorized(self, call: ToolCall, agent: Agent) -> bool:
        tool = self._tools_by_name.get(call.tool_name)
        if tool is None:
            return False
        required = tool.permission.required_role
        return required is not None and required != agent.role